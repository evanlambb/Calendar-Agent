"""
Improved Calendar Agent with enhanced error handling and configuration
"""
from typing import Annotated
import datetime as dt
import logging
import sys

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
import os
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import SystemMessage

from tools import *
from config import CalendarConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('calendar_agent.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Validate configuration on startup
is_valid, errors = CalendarConfig.validate_config()
if not is_valid:
    logger.error("Configuration validation failed:")
    for error in errors:
        logger.error(f"  - {error}")
    logger.info("Please check your configuration and ensure all required files exist.")
    sys.exit(1)

logger.info("Calendar Agent configuration validated successfully")

memory = InMemorySaver()

class State(TypedDict):
    messages: Annotated[list, add_messages]

def create_agent():
    """Initialize and configure the calendar agent"""
    try:
        graph_builder = StateGraph(State)
        tools = [create_event, get_events, get_current_datetime, delete_event]
        
        llm = init_chat_model(CalendarConfig.DEFAULT_MODEL)
        llm_with_tools = llm.bind_tools(tools)
        
        def chatbot(state: State):
            # Get current date/time info
            now = dt.datetime.now()
            current_info = f"Today is {now.strftime('%A, %B %d, %Y')} and the current time is {now.strftime('%I:%M %p')}."
            
            # Use the same comprehensive system prompt as original
            system_prompt = f"""You are a helpful calendar assistant. {current_info}

CONFLICT DETECTION WORKFLOW:
Before creating any event, ALWAYS follow this process:

1. FIRST: Call get_events() to check the target date for existing events
2. ANALYZE: Check if requested time conflicts with existing events using TIME RANGES
3. HANDLE CONFLICTS appropriately (see below)
4. ONLY THEN: Create the event if no conflicts or user approves

TIME RANGE ANALYSIS:
- Events are displayed as "HH:MM-HH:MM: Title" (e.g., "09:00-16:00: Work")
- Two events conflict if their time ranges overlap
- Examples of conflicts:
  • Existing: "09:00-16:00: Work" + New: "14:00-15:00: Meeting" = CONFLICT
  • Existing: "09:00-12:00: Work" + New: "13:00-14:00: Meeting" = NO CONFLICT
  • Existing: "14:00-15:00: Call" + New: "15:00-16:00: Meeting" = NO CONFLICT (back-to-back is OK)

CONFLICT HANDLING RULES:
- If the conflict is due to an all day event, ignore it as a conflict and schedule the event anyway.

For SPECIFIC TIMES (e.g., "2pm tomorrow", "8pm tonight"):
- If conflict exists: Ask user to choose:
  • Option 1: Double-book anyway
  • Option 2: Schedule after current event ends
  • Option 3: Pick different time
- Example: "You have 'Team Meeting' from 14:00-15:00. Would you like me to:
  1. Book this anyway (you'll have overlapping events)
  2. Schedule it from 15:00-16:00 instead
  3. Choose a different time?"

For FLEXIBLE TIMES (e.g., "anytime after 5pm", "sometime tomorrow"):
- Automatically find first available slot that fits the duration
- If you find a conflict, skip to next available time
- Example: "I see you're busy 5-6pm, so I'll book your workout 6-7pm instead."

IMPORTANT: Never create overlapping events without explicit user permission.
IMPORTANT: Never delete events without explicit user confirmation.

TONE: Be helpful, efficient, and proactive. Confirm details clearly after creating events and always confirm before deleting events."""
            
            messages = state["messages"]
            
            if not messages or not isinstance(messages[0], SystemMessage):
                system_msg = SystemMessage(content=system_prompt)
                messages = [system_msg] + messages
            
            return {"messages": [llm_with_tools.invoke(messages)]}
        
        # Build graph
        graph_builder.add_node("chatbot", chatbot)
        tool_node = ToolNode(tools=tools)
        graph_builder.add_node("tools", tool_node)
        
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_conditional_edges("chatbot", tools_condition)
        graph_builder.add_edge("tools", "chatbot")
        
        graph = graph_builder.compile(checkpointer=memory)
        config = {"configurable": {"thread_id": CalendarConfig.THREAD_ID}}
        
        logger.info("Calendar agent initialized successfully")
        return graph, config
        
    except Exception as e:
        logger.error(f"Failed to initialize calendar agent: {e}")
        raise

def stream_graph_updates(graph, config, user_input: str):
    """Process user input and stream responses"""
    try:
        for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}, config):
            for value in event.values():
                print("Assistant:", value["messages"][-1].content)
    except Exception as e:
        logger.error(f"Error processing user input '{user_input}': {e}")
        print("I'm sorry, I encountered an error processing your request. Please try again.")

def main():
    """Main application loop with improved error handling"""
    logger.info("Starting Calendar Agent...")
    
    try:
        graph, config = create_agent()
        print("🤖 Calendar Agent is ready! Type 'quit' to exit.")
        
        while True:
            try:
                user_input = input("User: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    logger.info("Calendar Agent session ended by user")
                    break
                    
                logger.debug(f"Processing user input: {user_input}")
                stream_graph_updates(graph, config, user_input)
                
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                logger.info("Calendar Agent session interrupted")
                break
                
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                print("An unexpected error occurred. Please try again.")
                continue
                
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print("Failed to start Calendar Agent. Please check the logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 