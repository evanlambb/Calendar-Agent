from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
import os

# Add parent directory to path to import agent_improved
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent_improved import create_agent

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create agent ONCE at startup - this preserves memory across requests
print("🤖 Initializing Calendar Agent...")
graph, base_config = create_agent()
print("✅ Calendar Agent ready!")

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = "mobile_user"

class ChatResponse(BaseModel):
    response: str
    thread_id: str

@app.post("/chat", response_model=ChatResponse)
def query_agent(request: ChatRequest) -> ChatResponse:
    try:
        # Use the SAME graph instance (preserves memory)
        config = {"configurable": {"thread_id": request.thread_id}}
        
        # Process message through agent
        response_text = ""
        for event in graph.stream(
            {"messages": [{"role": "user", "content": request.message}]}, 
            config
        ):
            for value in event.values():
                response_text = value["messages"][-1].content
        
        return ChatResponse(
            response=response_text,
            thread_id=request.thread_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Calendar Agent API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)