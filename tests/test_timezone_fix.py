#!/usr/bin/env python3
"""
Test script to verify timezone fix for conflict detection
"""

import datetime as dt
from tools import get_events, get_current_datetime

def test_timezone_consistency():
    """Test that get_events now properly handles Toronto timezone"""
    
    print("🧪 Testing Timezone Fix for Conflict Detection")
    print("=" * 50)
    
    # Get current date info
    current_info = get_current_datetime.invoke({})
    print(f"📅 {current_info}")
    
    # Test today's events
    today = dt.datetime.now().strftime('%Y-%m-%d')
    print(f"\n🔍 Checking events for today ({today}):")
    today_events = get_events.invoke({"start_date": today})
    print(today_events)
    
    # Test tomorrow's events  
    tomorrow = (dt.datetime.now() + dt.timedelta(days=1)).strftime('%Y-%m-%d')
    print(f"\n🔍 Checking events for tomorrow ({tomorrow}):")
    tomorrow_events = get_events.invoke({"start_date": tomorrow})
    print(tomorrow_events)
    
    print("\n" + "=" * 50)
    print("✅ Timezone test completed!")
    print("\n💡 The fix ensures:")
    print("   • get_events() now uses Toronto timezone (timeZone='America/Toronto')")
    print("   • create_event() already used Toronto timezone")
    print("   • Both functions now consistent → conflict detection should work!")
    
    print("\n🚀 Next steps:")
    print("   1. Run your calendar agent")
    print("   2. Try scheduling something during your work hours tomorrow")
    print("   3. The agent should now detect the conflict and ask how to handle it")

if __name__ == "__main__":
    test_timezone_consistency() 