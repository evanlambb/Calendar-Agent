#!/usr/bin/env python3
"""
Test script for delete_event functionality
"""

import datetime as dt
from tools import delete_event, get_events, create_event

def test_delete_workflow():
    """Test the complete delete event workflow"""
    
    print("🧪 Testing Delete Event Functionality")
    print("=" * 50)
    
    # Test 1: Search for events to delete
    print("\n1️⃣ Testing event search by keywords...")
    result = delete_event(event_search="meeting")
    print("Search Result:")
    print(result)
    
    print("\n" + "-" * 30)
    
    # Test 2: Try to delete with invalid parameters
    print("\n2️⃣ Testing invalid parameters...")
    result = delete_event()
    print("Invalid Parameters Result:")
    print(result)
    
    print("\n" + "-" * 30)
    
    # Test 3: Search for non-existent event
    print("\n3️⃣ Testing search for non-existent event...")
    result = delete_event(event_search="unicorn birthday party")
    print("Non-existent Event Result:")
    print(result)
    
    print("\n" + "-" * 30)
    
    # Test 4: Show current events for context
    print("\n4️⃣ Showing current calendar events for context...")
    today = dt.datetime.now().strftime('%Y-%m-%d')
    tomorrow = (dt.datetime.now() + dt.timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"\nToday's events ({today}):")
    print(get_events(today))
    
    print(f"\nTomorrow's events ({tomorrow}):")
    print(get_events(tomorrow))
    
    print("\n" + "=" * 50)
    print("✅ Delete functionality test completed!")
    print("\nTo test actual deletion:")
    print("1. First create a test event")
    print("2. Search for it using delete_event(event_search='test')")
    print("3. Copy the event ID from the results")
    print("4. Confirm deletion using delete_event(event_id='YOUR_ID', confirm_delete=True)")

if __name__ == "__main__":
    test_delete_workflow() 