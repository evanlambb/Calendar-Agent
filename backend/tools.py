import datetime as dt
import os.path
from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from langchain.tools import tool
from config import CalendarConfig
from utils import get_credentials_path, get_token_path, ensure_credentials_exist

# Initialize configuration
config = CalendarConfig()
SCOPES = config.CALENDAR_SCOPES

def get_credentials():
  """
  Allows me to access my google calendar from API
  Uses absolute paths that work from any directory
  """
  # Get absolute paths to credentials and token files
  credentials_path = ensure_credentials_exist()  # Also checks if file exists
  token_path = get_token_path()
  
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists(token_path):
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          credentials_path, SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(token_path, "w") as token:
      token.write(creds.to_json())
  
  return creds

@tool
def create_event(
    summary: str, 
    start_time: str, 
    end_time: str = None,
    description: str = "",
    location: str = "",
    attendees: List[str] = None,
    duration_minutes: int = None,
    repeat_frequency: str = None,
    repeat_count: int = None
) -> str:
  """
  Create a new calendar event. 
  
  IMPORTANT WORKFLOW: Before calling this function, ALWAYS call get_events() first 
  to check for scheduling conflicts on the target date. Never double-book without 
  user permission.
  
  WHEN TO USE:
  - User wants to schedule/book/create any calendar event
  - User says "schedule me", "book me", "add to my calendar", "create event"
  - User provides specific times or asks for flexible scheduling
  
  CONFLICT HANDLING:
  - If get_events() shows existing events at requested time, ask user:
    1. Double-book anyway, or 2. Schedule after existing event, or 3. Pick new time
  - For flexible times ("anytime after 5pm"), automatically avoid conflicts
  
  PARAMETER GUIDELINES:
  - summary: Use user's description or infer from context ("meeting", "workout", "lunch")
  - start_time: Always format as 'YYYY-MM-DD HH:MM' (24-hour format)
  - For duration vs end_time: Use duration_minutes when user says "for X minutes/hours"
  - attendees: Only include if user mentions specific people/emails
  - repeat: Only use if user says "daily", "weekly", "every day", etc.
  
  TIME PARSING EXAMPLES (assuming today is 2025-07-15):
  - "8pm tonight" → start_time="2025-07-15 20:00"  
  - "tomorrow at lunch" → start_time="2025-07-16 12:00"
  - "for 2 hours" → duration_minutes=120
  - "until 3pm" → end_time="2025-07-15 15:00"
  
  Args:
      summary (str): Event title/description - REQUIRED, cannot be empty
      start_time (str): Start time in 'YYYY-MM-DD HH:MM' format - REQUIRED
      end_time (str, optional): End time in 'YYYY-MM-DD HH:MM' format  
      description (str, optional): Longer description/notes for the event
      location (str, optional): Where the event takes place
      attendees (List[str], optional): Email addresses to invite
      duration_minutes (int, optional): Event length in minutes (alternative to end_time)
      repeat_frequency (str, optional): "daily", "weekly", or "monthly" for recurring events
      repeat_count (int, optional): How many times to repeat (required if repeat_frequency set)
  
  Returns:
      str: Success message with event details and link, or error message explaining what went wrong
      
  EXAMPLE WORKFLOWS (assuming today is 2025-07-15):
  1. User: "Book me for lunch tomorrow at 12pm"
      → Call get_events("2025-07-16") first to check conflicts
      → If no conflicts: create_event("Lunch", "2025-07-16 12:00", duration_minutes=60)
      
  2. User: "Schedule team meeting for 1 hour every Tuesday"  
      → create_event("Team Meeting", "2025-07-16 10:00", duration_minutes=60, 
                    repeat_frequency="weekly", repeat_count=10)
  """
  try: 
    service = build("calendar", "v3", credentials=get_credentials())
    
    # Validate required parameters are meaningful
    if not summary or not summary.strip():
        return "❌ Error: Event summary cannot be empty"
    
    if not start_time or not start_time.strip():
        return "❌ Error: Start time cannot be empty"
    
    # Validation: exactly one of end_time or duration_minutes must be provided
    if end_time and duration_minutes:
        return "❌ Error: Please provide either end_time OR duration_minutes, not both"
    
    if not end_time and not duration_minutes:
        return "❌ Error: Please provide either end_time OR duration_minutes"

    # Validation for repeat parameters
    if repeat_frequency and not repeat_count:
        return "❌ Error: If repeat_frequency is provided, repeat_count is required"

    if repeat_count and not repeat_frequency:
        return "❌ Error: If repeat_count is provided, repeat_frequency is required"

    if repeat_frequency and repeat_frequency not in ["daily", "weekly", "monthly"]:
        return "❌ Error: repeat_frequency must be 'daily', 'weekly', or 'monthly'"

    # Convert user format to API format
    try:
        start_dt = dt.datetime.strptime(start_time, "%Y-%m-%d %H:%M")
        
        if duration_minutes:
            # Calculate end_time from start_time + duration
            end_dt = start_dt + dt.timedelta(minutes=duration_minutes)
        else:
            # Parse the provided end_time
            end_dt = dt.datetime.strptime(end_time, "%Y-%m-%d %H:%M")
        
        start_iso = start_dt.isoformat()
        end_iso = end_dt.isoformat()
        
    except ValueError:
        return "❌ Error: Please use format 'YYYY-MM-DD HH:MM' for times"

    # Generate recurrence rule if needed
    recurrence_rule = None
    if repeat_frequency and repeat_count:
        freq_map = {
            "daily": "DAILY",
            "weekly": "WEEKLY", 
            "monthly": "MONTHLY"
        }
        recurrence_rule = f"RRULE:FREQ={freq_map[repeat_frequency]};COUNT={repeat_count}"

    # Start with required fields
    event = {
        "summary": summary,
        "start": {
            "dateTime": start_iso,
            "timeZone": "America/Toronto"  # Consistent with get_events timeZone parameter
        },
        "end": {
            "dateTime": end_iso,
            "timeZone": "America/Toronto"  # Consistent with get_events timeZone parameter
        }
    }

    # Add optional fields only if provided
    if description:  # Only add if not empty string
        event["description"] = description

    if location:     # Only add if not empty string
        event["location"] = location

    if attendees:    # Only add if list is provided and not empty
        event["attendees"] = [{"email": email} for email in attendees]

    # Add recurrence if specified
    if recurrence_rule:
        event["recurrence"] = [recurrence_rule]

    created_event = service.events().insert(calendarId="primary", body=event).execute()
    return f"✅ Event '{summary}' created successfully! Link: {created_event.get('htmlLink')}"
    
  except HttpError as error:
    return f"❌ Error creating event: {error}"

@tool
def get_events(start_date: str, end_date: str = None, max_results: int = 50) -> str:
    """
    Retrieve calendar events for specified date range. This is essential for conflict detection.
    
    WHEN TO USE:
    - ALWAYS call this BEFORE create_event() to check for scheduling conflicts
    - User asks "what do I have", "what's on my calendar", "am I free", "what's my schedule"
    - User wants to see events for specific day/week
    - Need to find available time slots
    
    CONFLICT DETECTION WORKFLOW:
    1. Call this function for the target date
    2. Parse returned events to check for time conflicts
    3. If conflicts exist with requested time, ask user how to handle
    4. If user wants flexible scheduling, use results to find free slots
    
    TIME CONFLICT ANALYSIS:
    - Compare requested start/end times with existing events
    - Look for overlaps: new_start < existing_end AND new_end > existing_start
    - Consider buffer time between events (suggest 15-30 min gaps)
    
    Args:
        start_date (str): Date to search from in 'YYYY-MM-DD' format - REQUIRED
        end_date (str, optional): End date in 'YYYY-MM-DD' format (defaults to start_date)
        max_results (int, optional): Maximum number of events to return (default 50)
    
    Returns:
        str: Formatted list of events with times and titles, or "No events found" message
        
    OUTPUT FORMAT EXAMPLE:
        "Events for 2025-07-16:
        • 09:00: Team Standup
        • 12:00: Lunch with Sarah  
        • 14:30: Client Call
        • 16:00: Project Review"
        
    USAGE EXAMPLES:
    - Before scheduling: get_events("2025-07-16") to check tomorrow's schedule
    - User question: "What do I have tomorrow?" → get_events("2025-07-16")  
    - Weekly view: get_events("2025-07-14", "2025-07-20")
    """
    try:
        if not end_date:
            end_date = start_date
            
        # Convert to full datetime for API using Toronto timezone (consistent with create_event)
        # Google Calendar API requires RFC3339 format with timezone info
        start_datetime = f"{start_date}T00:00:00-05:00"  # Toronto timezone (EST)
        end_datetime = f"{end_date}T23:59:59-05:00"      # Toronto timezone (EST)
        
        creds = get_credentials()
        service = build("calendar", "v3", credentials=creds)
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_datetime,
            timeMax=end_datetime,
            timeZone='America/Toronto',  # Specify Toronto timezone for consistent interpretation
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return f"No events found for {start_date}"
        
        result = f"Events for {start_date}:\n"
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            title = event.get('summary', 'No title')
            
            # Format time range nicely
            if 'T' in start and 'T' in end:
                start_time = start.split('T')[1][:5]  # Get HH:MM
                end_time = end.split('T')[1][:5]      # Get HH:MM
                result += f"• {start_time}-{end_time}: {title}\n"
            elif 'T' in start:  # Start has time but end doesn't (unusual case)
                start_time = start.split('T')[1][:5]
                result += f"• {start_time}: {title}\n"
            else:
                result += f"• All day: {title}\n"
        
        return result
        
    except Exception as error:
        return f"Error getting events: {str(error)}"

@tool
def delete_event(event_search: str = None, event_id: str = None, confirm_delete: bool = False) -> str:
    """
    Delete a calendar event by searching for it with keywords or using a specific event ID.
    
    WORKFLOW:
    1. If event_search provided: Search for matching events and list candidates
    2. User confirms which event to delete by providing event_id
    3. Call again with event_id and confirm_delete=True to actually delete
    
    WHEN TO USE:
    - User says "delete", "remove", "cancel" an event
    - User describes event to delete: "delete my dentist appointment", "remove meeting with John"
    - Always confirm before deleting to avoid mistakes
    
    SEARCH PRIORITY:
    - PRIMARY: Event title/summary (e.g., "Dentist Appointment", "Team Meeting")
    - SECONDARY: Event description field
    - TERTIARY: Event location field
    - Word-by-word matching in titles for partial matches
    
    SAFETY FEATURES:
    - Never deletes without confirmation
    - Shows full event details before deletion
    - Returns clear error messages for ambiguous requests
    
    Args:
        event_search (str, optional): Keywords to search for in event title, description, or location
        event_id (str, optional): Specific Google Calendar event ID to delete
        confirm_delete (bool, optional): Set to True to actually perform deletion after confirmation
    
    Returns:
        str: List of matching events for confirmation, success message, or error message
        
    EXAMPLE WORKFLOW:
    1. User: "Delete my dentist appointment tomorrow"
       → delete_event(event_search="dentist appointment")
       → Returns: "Found 1 matching event: [Event details]. To delete, confirm the event ID."
        
    2. User confirms: "Yes, delete that event"  
       → delete_event(event_id="abc123", confirm_delete=True)
       → Returns: "✅ Event 'Dentist Appointment' deleted successfully"
    """
    try:
        service = build("calendar", "v3", credentials=get_credentials())
        
        # Case 1: Confirm deletion with specific event ID
        if event_id and confirm_delete:
            try:
                # Get event details first for confirmation message
                event = service.events().get(calendarId='primary', eventId=event_id).execute()
                event_title = event.get('summary', 'Untitled Event')
                
                # Delete the event
                service.events().delete(calendarId='primary', eventId=event_id).execute()
                return f"✅ Event '{event_title}' has been deleted successfully!"
                
            except HttpError as error:
                if error.resp.status == 404:
                    return "❌ Error: Event not found. It may have already been deleted."
                else:
                    return f"❌ Error deleting event: {error}"
        
        # Case 2: Search for events by keywords
        elif event_search:
            # Get events from a reasonable time range (past 7 days to next 30 days)
            now = dt.datetime.now()
            start_date = (now - dt.timedelta(days=7)).strftime('%Y-%m-%d')
            end_date = (now + dt.timedelta(days=30)).strftime('%Y-%m-%d')
            
            start_datetime = f"{start_date}T00:00:00Z"
            end_datetime = f"{end_date}T23:59:59Z"
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_datetime,
                timeMax=end_datetime,
                maxResults=100,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                return "❌ No events found in your calendar to search through."
            
            # Search for matching events (case-insensitive partial matching)
            # PRIMARY: Search event title/summary first
            search_lower = event_search.lower()
            matching_events = []
            
            for event in events:
                event_title = event.get('summary', '').lower()      # Event title/summary (PRIMARY)
                event_desc = event.get('description', '').lower()   # Event description (SECONDARY)
                event_location = event.get('location', '').lower()  # Event location (TERTIARY)
                
                # Search priority: title first, then description, then location
                if (search_lower in event_title or 
                    search_lower in event_desc or 
                    search_lower in event_location or
                    any(word in event_title for word in search_lower.split())):
                    matching_events.append(event)
            
            if not matching_events:
                return f"❌ No events found matching '{event_search}'. Try being more specific or check the event title."
            
            # Format the results for user confirmation
            if len(matching_events) == 1:
                event = matching_events[0]
                start = event['start'].get('dateTime', event['start'].get('date'))
                title = event.get('summary', 'Untitled Event')
                location = event.get('location', '')
                event_id = event.get('id')
                
                # Format the date/time nicely
                if 'T' in start:
                    date_part = start.split('T')[0]
                    time_part = start.split('T')[1][:5]
                    formatted_time = f"{date_part} at {time_part}"
                else:
                    formatted_time = f"{start} (all day)"
                
                location_text = f" at {location}" if location else ""
                
                result = f"🔍 Found 1 matching event:\n"
                result += f"📅 '{title}' on {formatted_time}{location_text}\n\n"
                result += f"❓ Is this the event you want to delete? If yes, I'll delete it for you."
                result += f"\n\n💡 Event ID: {event_id}"
                
                return result
                
            else:
                result = f"🔍 Found {len(matching_events)} matching events:\n\n"
                for i, event in enumerate(matching_events, 1):
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    title = event.get('summary', 'Untitled Event')
                    location = event.get('location', '')
                    event_id = event.get('id')
                    
                    # Format the date/time nicely
                    if 'T' in start:
                        date_part = start.split('T')[0]
                        time_part = start.split('T')[1][:5]
                        formatted_time = f"{date_part} at {time_part}"
                    else:
                        formatted_time = f"{start} (all day)"
                    
                    location_text = f" at {location}" if location else ""
                    result += f"{i}. '{title}' on {formatted_time}{location_text}\n"
                    result += f"   Event ID: {event_id}\n\n"
                
                result += "❓ Which event would you like to delete? Please tell me the number or be more specific."
                return result
        
        # Case 3: Invalid parameters
        else:
            return "❌ Error: Please provide either keywords to search for an event or an event ID to delete."
    
    except HttpError as error:
        return f"❌ Error accessing calendar: {error}"
    except Exception as error:
        return f"❌ Unexpected error: {str(error)}"


@tool
def get_current_datetime() -> str:
    """
    Get current date, time, and day of week information.
    
    WHEN TO USE:
    - User asks "what day is it", "what's today's date", "what time is it"
    - Need to calculate relative dates ("tomorrow", "next week", "tonight")
    - Converting casual language to specific dates
    - ALWAYS call this if you need current date for scheduling
    
    RELATIVE DATE CALCULATIONS:
    Use the returned date to calculate:
    - "tonight" = today's date + evening time (18:00-22:00)
    - "tomorrow" = current date + 1 day
    - "next week" = current date + 7 days  
    - "this weekend" = upcoming Saturday/Sunday
    
    Returns:
        str: Current date, time, and day formatted as:
        "Current date: YYYY-MM-DD, Current time: HH:MM, Day of week: Monday"
        
    EXAMPLE USAGE:
    User: "Schedule me for a workout tonight"
    → Call get_current_datetime() first
    → Parse result to get today's date  
    → Convert "tonight" to specific time like "2025-07-15 20:00"
    → Then call create_event()
    """
    now = dt.datetime.now()
    return f"Current date: {now.strftime('%Y-%m-%d')}, Current time: {now.strftime('%H:%M')}, Day of week: {now.strftime('%A')}"




