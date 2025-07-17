# 📅 AI Calendar Agent

An intelligent calendar assistant built with **LangGraph** and **Google Calendar API** that helps you manage your schedule using natural language.

## ✨ Features

- **🤖 Natural Language Processing**: Talk to your calendar in plain English
- **📝 Smart Event Creation**: "Schedule me for lunch tomorrow at 12pm"
- **🔍 Intelligent Event Search**: "What do I have this week?"
- **🗑️ Safe Event Deletion**: "Delete my dentist appointment" (with confirmation)
- **⚠️ Conflict Detection**: Automatically checks for scheduling conflicts
- **🔄 Flexible Scheduling**: "Book a workout anytime after 5pm"

## 🛠️ Technology Stack

- **LangGraph**: AI agent framework for complex workflows
- **LangChain**: Tool integration and AI model management
- **Google Calendar API**: Calendar operations and data access
- **Google Gemini 2.5 Flash**: Natural language understanding
- **Python 3.8+**: Core implementation

## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/calendar-agent.git
cd calendar-agent
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Google Calendar API Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Calendar API
4. Create credentials (OAuth 2.0 Client ID)
5. Download credentials as `credentials.json` and place in project root

### 4. Environment Variables
Create a `.env` file in the project root:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 5. Run the Agent
```bash
python agent.py
```

## 📖 Usage Examples

### Creating Events
```
User: "Schedule me for a workout at 8pm tonight for 1 hour"
Assistant: ✅ Event 'Workout' created successfully!

User: "Book lunch with Sarah tomorrow at noon"  
Assistant: I see you have 'Team Meeting' from 12-1pm. Would you like me to:
1. Book this anyway (overlapping events)
2. Schedule it from 1-2pm instead  
3. Choose a different time?
```

### Viewing Events
```
User: "What do I have tomorrow?"
Assistant: Events for 2025-01-17:
• 09:00: Team Standup
• 12:00: Lunch with Sarah
• 14:30: Client Call
```

### Deleting Events
```
User: "Delete my dentist appointment"
Assistant: 🔍 Found 1 matching event:
📅 'Dentist Appointment' on 2025-01-17 at 14:00
❓ Is this the event you want to delete?

User: "Yes"
Assistant: ✅ Event 'Dentist Appointment' has been deleted successfully!
```

## 🏗️ Architecture

```
📱 User Input (Natural Language)
    ↓
🤖 LangGraph Agent (Gemini 2.5 Flash)
    ↓
🛠️ Tool Selection & Execution
    ├── create_event()
    ├── get_events()  
    ├── delete_event()
    └── get_current_datetime()
    ↓
📅 Google Calendar API
    ↓
✅ Structured Response
```

## 🔧 Tools & Functions

### Core Calendar Tools
- **`@tool create_event`**: Create new calendar events with conflict detection
- **`@tool get_events`**: Retrieve events for conflict checking and viewing
- **`@tool delete_event`**: Safe event deletion with confirmation workflow
- **`@tool get_current_datetime`**: Current date/time for relative scheduling

### Safety Features
- **Conflict Detection**: Always checks for scheduling conflicts before booking
- **Confirmation Workflow**: Never deletes events without user confirmation  
- **Flexible Scheduling**: Automatically finds available time slots
- **Error Handling**: Graceful handling of API errors and edge cases

## 🧪 Testing

Run the test scripts:
```bash
# Test event creation
python test_create_event.py

# Test event deletion workflow  
python test_delete_event.py

# Demonstrate @tool decorator benefits
python demonstrate_tool_decorator.py
```

## 🔐 Security Notes

- **Never commit** `credentials.json`, `token.json`, or `.env` files
- Store API keys securely in environment variables
- Google Calendar tokens are stored locally in `token.json`
- Review and audit calendar permissions regularly

## 🚧 Development Status

- ✅ Basic calendar CRUD operations
- ✅ Natural language processing
- ✅ Conflict detection and resolution
- ✅ Safe deletion workflow
- 🔄 Future: Mobile React Native app integration

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Contact

Your Name - your.email@example.com
Project Link: [https://github.com/YOUR_USERNAME/calendar-agent](https://github.com/YOUR_USERNAME/calendar-agent)
