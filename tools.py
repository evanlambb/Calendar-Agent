# @tool
# def get_events(start_date: str, end_date: str = None, max_results: int = 50) -> str:
#     """
#     Retrieve calendar events for specified date range. This is essential for conflict detection.
    
#     WHEN TO USE:
#     - ALWAYS call this BEFORE create_event() to check for scheduling conflicts
#     - User asks "what do I have", "what's on my calendar", "am I free", "what's my schedule"
#     - User wants to see events for specific day/week
#     - Need to find available time slots
    
#     CONFLICT DETECTION WORKFLOW:
#     1. Call this function for the target date
#     2. Parse returned events to check for time conflicts
#     3. If conflicts exist with requested time, ask user how to handle
#     4. If user wants flexible scheduling, use results to find free slots
    
#     TIME CONFLICT ANALYSIS:
#     - Compare requested start/end times with existing events
#     - Look for overlaps: new_start < existing_end AND new_end > existing_start
#     - Consider buffer time between events (suggest 15-30 min gaps)
    
#     Args:
#         start_date (str): Date to search from in 'YYYY-MM-DD' format - REQUIRED
#         end_date (str, optional): End date in 'YYYY-MM-DD' format (defaults to start_date)
#         max_results (int, optional): Maximum number of events to return (default 50)
    
#     Returns:
#         str: Formatted list of events with times and titles, or "No events found" message
        
#     OUTPUT FORMAT EXAMPLE:
#         "Events for 2025-07-16:
#         • 09:00: Team Standup
#         • 12:00: Lunch with Sarah  
#         • 14:30: Client Call
#         • 16:00: Project Review"
        
#     USAGE EXAMPLES:
#     - Before scheduling: get_events("2025-07-16") to check tomorrow's schedule
#     - User question: "What do I have tomorrow?" → get_events("2025-07-16")  
#     - Weekly view: get_events("2025-07-14", "2025-07-20")
#     """


@tool
def get_weather(city: str) -> str:
    """
    Takes the name of a city and returns the current weather in the city

    Args: 
        city (str): Name of the city that you want the weather for

    Returns:
        str: the weather. One of [sunny, rainy]
    """
    city = city.strip().lower()

    if city == "toronto":
        return "sunny"
    else:
        return "rainy"