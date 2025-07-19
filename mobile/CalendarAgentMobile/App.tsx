import React, { useState, useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
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
  Keyboard,
  Dimensions,
} from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';

// API Configuration - Update this with your computer's IP address
const API_BASE_URL = 'http://192.168.1.14:8000';

// Define what a message looks like
interface Message {
  id: string;           // Unique identifier
  text: string;         // The actual message content
  sender: 'user' | 'assistant';  // Who sent it
  timestamp: Date;      // When it was sent
}

export default function App() {
  // State to track all messages
  const [messages, setMessages] = useState<Message[]>([]);
  
  // State to track what user is currently typing
  const [inputText, setInputText] = useState('');
  
  // State to track if we're waiting for assistant response
  const [isLoading, setIsLoading] = useState(false);
  
  // Voice recording state
  const [isRecording, setIsRecording] = useState(false);
  const [recordingPermission, setRecordingPermission] = useState(false);

  // Keyboard state for debugging
  const [keyboardHeight, setKeyboardHeight] = useState(0);
  const [isKeyboardVisible, setIsKeyboardVisible] = useState(false);

  // Ref for ScrollView to enable auto-scrolling
  const scrollViewRef = React.useRef<ScrollView>(null);

  // Manual keyboard detection for better control
  useEffect(() => {
    const keyboardDidShowListener = Keyboard.addListener('keyboardDidShow', (event) => {
      setKeyboardHeight(event.endCoordinates.height);
      setIsKeyboardVisible(true);
    });

    const keyboardDidHideListener = Keyboard.addListener('keyboardDidHide', () => {
      setKeyboardHeight(0);
      setIsKeyboardVisible(false);
    });

    const keyboardWillShowListener = Keyboard.addListener('keyboardWillShow', (event) => {
      // iOS preview event - could be used for smoother animations if needed
    });

    const keyboardWillHideListener = Keyboard.addListener('keyboardWillHide', () => {
      // iOS preview event - could be used for smoother animations if needed
    });

    return () => {
      keyboardDidShowListener?.remove();
      keyboardDidHideListener?.remove();
      keyboardWillShowListener?.remove();
      keyboardWillHideListener?.remove();
    };
  }, []);

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    if (messages.length > 0) {
      setTimeout(() => {
        scrollViewRef.current?.scrollToEnd({ animated: true });
      }, 100); // Small delay to ensure content is rendered
    }
  }, [messages]);

  // Auto-scroll to bottom when keyboard state changes
  useEffect(() => {
    setTimeout(() => {
      scrollViewRef.current?.scrollToEnd({ animated: true });
    }, 0); // Longer delay for keyboard layout changes
  }, [isKeyboardVisible]);

  // Voice recording functions
  const startVoiceRecording = async () => {
    try {
      setIsRecording(true);
      // TODO: Implement actual voice recording here
      Alert.alert('Voice Recording', 'Voice recording started! (Feature coming soon)');
    } catch (error) {
      console.error('Error starting voice recording:', error);
      Alert.alert('Error', 'Failed to start voice recording');
    }
  };

  const stopVoiceRecording = async () => {
    try {
      setIsRecording(false);
      // TODO: Implement voice-to-text conversion here
      Alert.alert('Voice Recording', 'Voice recording stopped! (Feature coming soon)');
    } catch (error) {
      console.error('Error stopping voice recording:', error);
      Alert.alert('Error', 'Failed to stop voice recording');
    }
  };

  const toggleVoiceRecording = () => {
    if (isRecording) {
      stopVoiceRecording();
    } else {
      startVoiceRecording();
    }
  };

  // Function to send a message
  const sendMessage = async () => {
    if (!inputText.trim() || isLoading) return; // Don't send empty messages or if already loading

    // Create a new user message
    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText.trim(),
      sender: 'user',
      timestamp: new Date(),
    };

    // Add user message to the array immediately
    setMessages(prevMessages => [...prevMessages, userMessage]);
    
    // Clear the input and show loading
    setInputText('');
    setIsLoading(true);

    try {
      // Call your backend API
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        message: userMessage.text,
        thread_id: 'mobile_user',
      });

      // Create assistant response message
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.data.response,
        sender: 'assistant',
        timestamp: new Date(),
      };

      // Add assistant message to the array
      setMessages(prevMessages => [...prevMessages, assistantMessage]);

    } catch (error) {
      console.error('Error sending message:', error);
      
      // Show error to user
      Alert.alert('Connection Error', 'Failed to connect to calendar agent. Make sure the server is running.');
      
      // Add error message to chat
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error connecting to the server. Please try again.',
        sender: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
      
    } finally {
      // Always stop loading
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerText}>📅 Calendar Agent</Text>
        </View>

        {/* Chat Container with Manual Keyboard Handling */}
        <View style={styles.chatContainer}>

          
          {/* Messages Area */}
          <ScrollView 
            ref={scrollViewRef}
            style={styles.messagesContainer}
            contentContainerStyle={{
              paddingBottom: isKeyboardVisible ? keyboardHeight + 30 : 30
            }}
          >
            {messages.length === 0 ? (
              // Show welcome message when no messages
              <View style={styles.welcomeContainer}>
                <Text style={styles.welcomeText}>
                  👋 Hi! I'm your calendar assistant.{'\n'}
                  Try asking me to check your schedule or create events!
                </Text>
              </View>
            ) : (
              // Show actual messages
              messages.map((message) => (
                <View
                  key={message.id}
                  style={[
                    styles.messageContainer,
                    message.sender === 'user' ? styles.userMessage : styles.assistantMessage,
                  ]}
                >
                  <Text style={[
                    styles.messageText,
                    { color: message.sender === 'user' ? 'white' : 'white' }
                  ]}>
                    {message.text}
                  </Text>
                  {/* <Text style={styles.timestamp}>
                    {message.timestamp.toLocaleTimeString([], { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </Text> */}
                </View>
              ))
            )}
            
            {/* Loading indicator */}
            {isLoading && (
              <View style={[styles.messageContainer, styles.assistantMessage]}>
                <Text style={[styles.messageText, { color: 'white' }]}>
                  Thinking...
                </Text>
              </View>
            )}
          </ScrollView>

          {/* Input Area - Google Messages Style */}
          <View style={[
            styles.inputContainer,
            { 
              transform: [{ translateY: isKeyboardVisible ? -keyboardHeight : 0 }]
            }
          ]}>
            {isRecording ? (
              /* Voice Recording UI */
              <View style={styles.recordingContainer}>
                <TouchableOpacity 
                  style={styles.voiceButtonRecording}
                  onPress={toggleVoiceRecording}
                >
                  <Ionicons name="stop" size={24} color="white" />
                </TouchableOpacity>
                <View style={styles.recordingIndicator}>
                  <Text style={styles.recordingText}>Recording...</Text>
                  <View style={styles.recordingWave}>
                    <Text style={styles.waveText}>🎤 ●●●</Text>
                  </View>
                </View>
                <TouchableOpacity 
                  style={styles.cancelButton}
                  onPress={() => setIsRecording(false)}
                >
                  <Ionicons name="close" size={24} color="#666" />
                </TouchableOpacity>
              </View>
            ) : (
              /* Normal Chat UI */
              <View style={styles.chatInputRow}>
                {/* Text Input */}
                <TextInput
                  style={styles.textInput}
                  value={inputText}
                  onChangeText={setInputText}
                  placeholder="Message"
                  placeholderTextColor="#999"
                  multiline
                  maxLength={500}
                  editable={!isLoading}
                />
                
                {/* Send Button or Voice Button */}
                {inputText.trim().length > 0 ? (
                  /* Show Send Button when there's text */
                  <TouchableOpacity 
                    style={[
                      styles.sendButton,
                      (!inputText.trim() || isLoading) && styles.sendButtonDisabled
                    ]}
                    onPress={sendMessage}
                    disabled={!inputText.trim() || isLoading}
                  >
                    <Ionicons 
                      name="send" 
                      size={20} 
                      color="white" 
                    />
                  </TouchableOpacity>
                ) : (
                  /* Show Voice Button when no text */
                  <TouchableOpacity 
                    style={styles.voiceButtonCircular}
                    onPress={toggleVoiceRecording}
                  >
                    <Ionicons name="mic" size={20} color="white" />
                  </TouchableOpacity>
                )}
              </View>
            )}
          </View>
        </View>

        <StatusBar 
          style="light" 
          backgroundColor="#101417" 
          translucent={false}
        />
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#101417',  // Light gray background
  },
  header: {
    backgroundColor: '#007AFF',  // iOS blue
    padding: 16,
    alignItems: 'center',
  },
  headerText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  chatContainer: {
    flex: 1,  // Take up remaining space after header
  },
  messagesContainer: {
    flex: 1,          // Take up available space between header and input
    padding: 16,
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
    marginVertical: 6,     // Space between messages
    paddingHorizontal: 16, // More balanced horizontal padding
    paddingVertical: 12,   // Separate vertical padding
    borderRadius: 25,      // Perfectly circular ends like iMessage
    maxWidth: '95%',       // Don't take full width
  },
  userMessage: {
    backgroundColor: '#004660',  // Blue for user
    alignSelf: 'flex-end',       // Align to right
  },
  assistantMessage: {
    backgroundColor: '#292a2c',    // White for assistant
    alignSelf: 'flex-start',     // Align to left
  },
  messageText: {
    fontSize: 18,
    textAlign: 'left',     // Ensure consistent text alignment
    // Color is now dynamic in the component
  },
  timestamp: {
    fontSize: 12,
    color: '#999',
    marginTop: 4,
  },
  inputContainer: {
    flexDirection: 'row',        // Horizontal layout
    padding: 10,                 // Reduced from 16 to 10
    backgroundColor: 'transparent',
    alignItems: 'flex-end',      // Align items to bottom for better voice button alignment
  },
  textInput: {
    flex: 1,                     // Take up most space
    borderWidth: 1,
    borderColor: '#e0e0e0',
    backgroundColor: '#f8f8f8',  // Light gray background like Google Messages
    borderRadius: 25,            // More rounded like Google Messages
    paddingHorizontal: 16,
    paddingVertical: 14,
    marginRight: 6,              // Reduced from 10 to 6
    fontSize: 18,
    maxHeight: 100,              // Limit height for multiline
    minHeight: 48,               // Minimum height (increased to match button)
  },

  sendButton: {
    backgroundColor: '#007AFF',
    borderRadius: 24,            // Circular button (increased for larger size)
    width: 48,                   // Fixed width for circle (matches textbox height)
    height: 48,                  // Fixed height for circle (matches textbox height)
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 4,               // Reduced from 8 to 4
  },
  sendButtonDisabled: {
    backgroundColor: '#ccc',
    opacity: 0.7,
  },
  voiceButtonCircular: {
    backgroundColor: '#007AFF', // Blue for circular voice button
    borderRadius: 24,           // Circular button (increased for larger size)
    width: 48,                  // Fixed width for circle (matches textbox height)
    height: 48,                 // Fixed height for circle (matches textbox height)
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 4,               // Reduced from 8 to 4
  },
  voiceButtonRecording: {
    backgroundColor: '#FF3B30', // Red for recording
    borderRadius: 20,
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  recordingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f0f0f0',
    borderRadius: 25,
    padding: 10,
    marginRight: 10,
  },
  recordingIndicator: {
    flexDirection: 'column',
    marginLeft: 10,
    marginRight: 10,
  },
  recordingText: {
    fontSize: 12,
    color: '#666',
    marginBottom: 5,
  },
  recordingWave: {
    flexDirection: 'row',
  },
  waveText: {
    fontSize: 16,
  },
  cancelButton: {
    padding: 8,
  },
  chatInputRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
  },
});
