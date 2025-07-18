# 📱 Calendar Agent Mobile App - Project Roadmap

## 🎯 **Goal**: Convert Python calendar agent to React Native mobile app in 1-2 days

**Architecture**: FastAPI (Python backend) + React Native/Expo (mobile frontend)

---

## 📋 **Day 1: Backend API Development (3-4 hours)**

### **Phase 1.1: Setup FastAPI (30 minutes)**

**Install dependencies:**
```bash
pip install fastapi uvicorn python-multipart
```

**Create `api_server.py`:**
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio
import json

# Import your existing agent
from agent import graph, config

app = FastAPI(title="Calendar Agent API", version="1.0.0")

# Enable CORS for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = "mobile_user"

class ChatResponse(BaseModel):
    response: str
    thread_id: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Use your existing graph with thread config
        config_dict = {"configurable": {"thread_id": request.thread_id}}
        
        # Get response from your agent
        response_text = ""
        for event in graph.stream(
            {"messages": [{"role": "user", "content": request.message}]}, 
            config_dict
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
async def health_check():
    return {"status": "healthy", "message": "Calendar Agent API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Test the API:**
```bash
python api_server.py
# Visit: http://localhost:8000/docs (FastAPI auto-docs)
```

### **Phase 1.2: Verify Calendar Integration (30 minutes)**

**Test with curl:**
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "What events do I have tomorrow?"}'
```

**Expected response:**
```json
{
  "response": "Let me check your calendar for tomorrow...",
  "thread_id": "mobile_user"
}
```

### **Phase 1.3: Network Configuration (30 minutes)**

**Find your computer's IP address:**
```bash
# Windows
ipconfig | findstr IPv4

# Expected output: IPv4 Address. . . . . . . . . . . : 192.168.1.XXX
```

**Update server for network access:**
```python
# In api_server.py, change the uvicorn.run line:
uvicorn.run(app, host="0.0.0.0", port=8000)  # Allows network access
```

**Test from phone browser:**
- Visit: `http://192.168.1.XXX:8000/health` (replace XXX with your IP)
- Should see: `{"status": "healthy", "message": "Calendar Agent API is running"}`

---

## 📱 **Day 2: Mobile App Development (4-5 hours)**

### **Phase 2.1: Expo Setup (30 minutes)**

**Create new Expo project:**
```bash
npx create-expo-app CalendarAgentMobile --template blank-typescript
cd CalendarAgentMobile
```

**Install dependencies:**
```bash
npx expo install expo-status-bar react-native-safe-area-context
npm install axios
```

**Start development server:**
```bash
npx expo start
```

### **Phase 2.2: Basic Chat UI (2 hours)**

**Update `App.tsx`:**
```typescript
import React, { useState, useRef, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}

const API_BASE_URL = 'http://192.168.1.XXX:8000'; // Replace XXX with your IP

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollViewRef = useRef<ScrollView>(null);

  const sendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText.trim(),
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.text,
          thread_id: 'mobile_user',
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: data.response,
        sender: 'assistant',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      Alert.alert('Error', 'Failed to send message. Make sure the server is running.');
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    scrollViewRef.current?.scrollToEnd({ animated: true });
  }, [messages]);

  return (
    <SafeAreaProvider>
      <StatusBar style="auto" />
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.headerText}>📅 Calendar Agent</Text>
        </View>

        <KeyboardAvoidingView 
          style={styles.chatContainer}
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        >
          <ScrollView
            ref={scrollViewRef}
            style={styles.messagesContainer}
            contentContainerStyle={styles.messagesContent}
          >
            {messages.length === 0 && (
              <View style={styles.welcomeContainer}>
                <Text style={styles.welcomeText}>
                  👋 Hi! I'm your calendar assistant.{'\n'}
                  Try asking me to check your schedule or create events!
                </Text>
              </View>
            )}
            
            {messages.map((message) => (
              <View
                key={message.id}
                style={[
                  styles.messageContainer,
                  message.sender === 'user' ? styles.userMessage : styles.assistantMessage,
                ]}
              >
                <Text style={styles.messageText}>{message.text}</Text>
                <Text style={styles.timestamp}>
                  {message.timestamp.toLocaleTimeString([], { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </Text>
              </View>
            ))}
            
            {isLoading && (
              <View style={[styles.messageContainer, styles.assistantMessage]}>
                <Text style={styles.messageText}>Thinking...</Text>
              </View>
            )}
          </ScrollView>

          <View style={styles.inputContainer}>
            <TextInput
              style={styles.textInput}
              value={inputText}
              onChangeText={setInputText}
              placeholder="Ask about your calendar..."
              multiline
              maxLength={500}
              editable={!isLoading}
              onSubmitEditing={sendMessage}
              blurOnSubmit={false}
            />
            <TouchableOpacity
              style={[styles.sendButton, (!inputText.trim() || isLoading) && styles.sendButtonDisabled]}
              onPress={sendMessage}
              disabled={!inputText.trim() || isLoading}
            >
              <Text style={styles.sendButtonText}>Send</Text>
            </TouchableOpacity>
          </View>
        </KeyboardAvoidingView>
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#007AFF',
    padding: 16,
    alignItems: 'center',
  },
  headerText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  chatContainer: {
    flex: 1,
  },
  messagesContainer: {
    flex: 1,
    padding: 16,
  },
  messagesContent: {
    flexGrow: 1,
  },
  welcomeContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  welcomeText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 24,
  },
  messageContainer: {
    marginVertical: 4,
    padding: 12,
    borderRadius: 12,
    maxWidth: '80%',
  },
  userMessage: {
    backgroundColor: '#007AFF',
    alignSelf: 'flex-end',
  },
  assistantMessage: {
    backgroundColor: 'white',
    alignSelf: 'flex-start',
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  messageText: {
    fontSize: 16,
    lineHeight: 20,
  },
  timestamp: {
    fontSize: 12,
    color: '#999',
    marginTop: 4,
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 16,
    backgroundColor: 'white',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  textInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginRight: 12,
    maxHeight: 100,
    fontSize: 16,
  },
  sendButton: {
    backgroundColor: '#007AFF',
    borderRadius: 20,
    paddingHorizontal: 20,
    paddingVertical: 12,
    justifyContent: 'center',
  },
  sendButtonDisabled: {
    backgroundColor: '#ccc',
  },
  sendButtonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16,
  },
});
```

### **Phase 2.3: Testing & Polish (1 hour)**

**Update the IP address in App.tsx:**
```typescript
const API_BASE_URL = 'http://192.168.1.XXX:8000'; // Replace with your actual IP
```

**Test on your Android phone:**
1. Install Expo Go app from Google Play Store
2. Scan QR code from `npx expo start`
3. Test basic conversation with your calendar agent

---

## 🚀 **Day 3: Deployment & Polish (Optional)**

### **Cloud Deployment Options:**

**Option A: Railway (Free tier)**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy backend
railway login
railway init
railway up
```

**Option B: Render (Free tier)**
- Upload code to GitHub
- Connect Render to your repository
- Deploy as web service

### **Mobile App Polish:**
- Add app icon
- Improve error handling
- Add conversation persistence
- Better loading states

---

## ✅ **Success Criteria**

By end of implementation, you should have:
- ✅ FastAPI server running on your computer
- ✅ React Native app on your phone
- ✅ Successful calendar queries via mobile interface
- ✅ All existing calendar agent features accessible from phone

---

## 🔄 **Future "Ideal World" Features (Post-MVP)**

1. **Real-time Updates** (1 week)
   - WebSocket connection
   - Live calendar sync
   - Push notifications

2. **Offline Support** (1 week)  
   - Local data caching
   - Offline queue for requests
   - Background sync

3. **Advanced UI** (1 week)
   - Voice input
   - Rich calendar visualization
   - Gesture controls

4. **Cloud-Native Backend** (1 week)
   - Serverless deployment
   - Database integration
   - Multi-user support

---

## 🛠️ **Troubleshooting**

**Common Issues:**
- **Can't connect from phone**: Check firewall, ensure both devices on same WiFi
- **CORS errors**: Verify CORS middleware in FastAPI
- **Import errors**: Ensure all Python dependencies installed in same environment
- **Expo errors**: Clear cache with `npx expo start --clear`

**Quick Fixes:**
```bash
# Reset Expo cache
npx expo start --clear

# Check server accessibility
curl http://YOUR_IP:8000/health

# Restart FastAPI server
python api_server.py
```

---

## 📊 **Time Estimates**

| Phase | Time | Description |
|-------|------|-------------|
| FastAPI Setup | 1 hour | Convert agent to API |
| Network Config | 30 min | Enable phone access |
| React Native UI | 2 hours | Basic chat interface |
| Integration | 1 hour | Connect app to API |
| Testing | 1 hour | Debug and polish |
| **Total** | **5.5 hours** | **Complete MVP** |

This gets you from Python CLI to mobile app in under 6 hours! 🚀 