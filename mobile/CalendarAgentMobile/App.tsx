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
import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';
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
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [recordingUri, setRecordingUri] = useState<string | null>(null);
  const [recordingStartTime, setRecordingStartTime] = useState<number | null>(null);

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

  // Cleanup recording on component unmount
  useEffect(() => {
    return () => {
      if (recording) {
        recording.stopAndUnloadAsync();
      }
    };
  }, [recording]);

  // Voice recording functions
  const startVoiceRecording = async () => {
    try {
      // Prevent multiple recordings
      if (recording || isRecording) {
        console.log('Recording already in progress');
        return;
      }

      // Request microphone permissions with detailed checking
      console.log('Requesting microphone permissions...');
      const permissionResponse = await Audio.requestPermissionsAsync();
      console.log('Permission response:', permissionResponse);
      
      if (permissionResponse.status !== 'granted') {
        Alert.alert(
          'Permission Denied', 
          `Microphone permission is required for voice recording. Status: ${permissionResponse.status}`
        );
        return;
      }
      
      // Additional Android info
      if (Platform.OS === 'android') {
        console.log('Android detected - will use LOW_QUALITY preset for better compatibility');
      }

      // Configure audio recording with better Android support
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
        staysActiveInBackground: true,
        shouldDuckAndroid: true,
        playThroughEarpieceAndroid: false,
      });

      // Use simpler recording options for better Android compatibility
      const recordingOptions = Platform.OS === 'android' 
        ? Audio.RecordingOptionsPresets.LOW_QUALITY
        : Audio.RecordingOptionsPresets.HIGH_QUALITY;

      // Create recording with explicit preparation for Android
      const newRecording = new Audio.Recording();
      
      try {
        await newRecording.prepareToRecordAsync(recordingOptions);
        console.log('Recording prepared successfully');
        
        await newRecording.startAsync();
        console.log('Recording started successfully');
        
        setRecording(newRecording);
        setIsRecording(true);
        setRecordingStartTime(Date.now());
      } catch (prepareError) {
        console.error('Error preparing/starting recording:', prepareError);
        // Fallback to createAsync method
        const { recording: fallbackRecording } = await Audio.Recording.createAsync(recordingOptions);
        setRecording(fallbackRecording);
        setIsRecording(true);
        setRecordingStartTime(Date.now());
        console.log('Recording started with fallback method');
      }
      
    } catch (error) {
      console.error('Error starting voice recording:', error);
      Alert.alert('Error', 'Failed to start voice recording');
      // Reset state on error
      setIsRecording(false);
      setRecording(null);
      setRecordingStartTime(null);
    }
  };

  const stopVoiceRecording = async () => {
    try {
      if (!recording) {
        console.log('No recording to stop');
        setIsRecording(false);
        return;
      }

      console.log('Stopping recording...');
      
      // Check minimum recording duration (1 second)
      const recordingDuration = recordingStartTime ? Date.now() - recordingStartTime : 0;
      if (recordingDuration < 1000) {
        Alert.alert('Recording Too Short', 'Please record for at least 1 second.');
        return;
      }
      
      // Get recording status before stopping
      const status = await recording.getStatusAsync();
      console.log('Recording status:', status);
      
      // Only stop if recording is actually recording
      if (status.isRecording) {
        console.log('Recording duration was:', status.durationMillis, 'ms');
        console.log('Metering level:', status.metering);
        
        // Stop recording with better error handling
        await recording.stopAndUnloadAsync();
        
        const uri = recording.getURI();
        console.log('Final recording URI:', uri);
        
        // Check if file actually exists and has content
        if (uri) {
          try {
            const fileInfo = await FileSystem.getInfoAsync(uri);
            console.log('File info:', fileInfo);
            
            if (fileInfo.exists) {
              console.log('File size:', fileInfo.size, 'bytes');
              if (fileInfo.size && fileInfo.size > 1000) { // At least 1KB
                console.log('Valid recording file found');
              } else {
                console.log('Recording file is too small:', fileInfo.size, 'bytes');
              }
            } else {
              console.log('Recording file does not exist at:', uri);
            }
          } catch (fileCheckError) {
            console.error('Error checking file:', fileCheckError);
          }
        }
        
        // Reset audio mode
        await Audio.setAudioModeAsync({
          allowsRecordingIOS: false,
        });
        
        // Update state
        setRecordingUri(uri);
        setRecording(null);
        setIsRecording(false);
        setRecordingStartTime(null);
        
        // Process the recording if we have a valid URI
        if (uri) {
          await processVoiceRecording(uri);
        } else {
          Alert.alert('Recording Error', 'No audio data was captured. Please try again.');
        }
      } else {
        console.log('Recording was not in recording state');
        // Clean up the recording object
        await recording.stopAndUnloadAsync();
        setRecording(null);
        setIsRecording(false);
        setRecordingStartTime(null);
        Alert.alert('Recording Error', 'Recording was not active. Please try again.');
      }
      
    } catch (error) {
      console.error('Error stopping voice recording:', error);
      
      // Always reset state on error
      setIsRecording(false);
      setRecording(null);
      setRecordingStartTime(null);
      
      // Show user-friendly error message
      const errorMessage = error instanceof Error ? error.message : String(error);
      if (errorMessage.includes('no valid audio data')) {
        Alert.alert('Recording Too Short', 'Please record for at least 1 second and try again.');
      } else {
        Alert.alert('Recording Error', 'Failed to stop recording. Please try again.');
      }
    }
  };

  const processVoiceRecording = async (uri: string) => {
    try {
      // Get file info for display
      const fileInfo = await FileSystem.getInfoAsync(uri);
      const fileSizeKB = fileInfo.exists && 'size' in fileInfo && fileInfo.size 
        ? Math.round(fileInfo.size / 1024) 
        : 0;
      
      Alert.alert(
        'Recording Complete! 🎙️', 
        `File size: ${fileSizeKB}KB\nDuration: ${recordingStartTime ? Math.round((Date.now() - recordingStartTime) / 1000) : '?'} seconds\n\nWould you like to play it back?`,
        [
          {
            text: 'Play Recording',
            onPress: () => playRecording(uri)
          },
          {
            text: 'Convert to Text',
            onPress: () => convertSpeechToText(uri)
          },
          {
            text: 'Cancel',
            style: 'cancel'
          }
        ]
      );
    } catch (error) {
      console.error('Error processing voice recording:', error);
    }
  };

  const playRecording = async (uri: string) => {
    try {
      console.log('Playing recording from:', uri);
      
      // Configure audio mode for playback
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: false,
        playsInSilentModeIOS: true,
        shouldDuckAndroid: true,
      });

      // Create and load the sound
      const { sound } = await Audio.Sound.createAsync(
        { uri },
        { shouldPlay: true } // Auto-play when loaded
      );

      // Show playback controls
      Alert.alert(
        'Playing Recording 🔊',
        'Audio is now playing...',
        [
          {
            text: 'Stop',
            onPress: async () => {
              try {
                await sound.stopAsync();
                await sound.unloadAsync();
                console.log('Playback stopped');
              } catch (stopError) {
                console.error('Error stopping playback:', stopError);
              }
            }
          }
        ]
      );

      // Auto-cleanup when playback finishes
      sound.setOnPlaybackStatusUpdate((status) => {
        if (status.isLoaded && status.didJustFinish) {
          sound.unloadAsync();
          console.log('Playback finished');
        }
      });

    } catch (error) {
      console.error('Error playing recording:', error);
      Alert.alert('Playback Error', 'Could not play the recording. The file might be corrupted.');
    }
  };

  const convertSpeechToText = async (uri: string) => {
    try {
      console.log('Converting speech to text from:', uri);
      
      // Show loading state
      setIsLoading(true);
      
      // Create FormData to send the audio file
      const formData = new FormData();
      formData.append('audio', {
        uri: uri,
        type: 'audio/m4a',
        name: 'recording.m4a',
      } as any);

      // Send to your backend for speech-to-text conversion
      const response = await axios.post(`${API_BASE_URL}/speech-to-text`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 30000, // 30 second timeout for processing
      });

      if (response.data && response.data.text) {
        const transcribedText = response.data.text.trim();
        console.log('Transcribed text:', transcribedText);
        
        // Set the transcribed text as input and send it
        setInputText(transcribedText);
        
        // Auto-send the message after a brief delay
        setTimeout(() => {
          if (transcribedText) {
            sendMessageWithText(transcribedText);
          }
        }, 500);
        
        Alert.alert(
          'Speech Converted! 🎯',
          `Transcribed: "${transcribedText}"\n\nSending message...`,
          [{ text: 'OK' }]
        );
      } else {
        Alert.alert('Conversion Error', 'Could not convert speech to text. Please try again.');
      }

    } catch (error: any) {
      console.error('Error converting speech to text:', error);
      
      if (error.code === 'ECONNABORTED') {
        Alert.alert('Timeout Error', 'Speech conversion took too long. Please try a shorter recording.');
      } else if (error.response?.status === 404) {
        Alert.alert('Backend Error', 'Speech-to-text endpoint not found. Please set up the backend first.');
      } else {
        Alert.alert('Conversion Error', 'Failed to convert speech to text. Please check your connection and try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Helper function to send message with specific text
  const sendMessageWithText = async (text: string) => {
    if (!text.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: text.trim(),
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prevMessages => [...prevMessages, userMessage]);
    setInputText(''); // Clear input after sending

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        message: userMessage.text,
        thread_id: 'mobile_user',
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.data.response,
        sender: 'assistant',
        timestamp: new Date(),
      };

      setMessages(prevMessages => [...prevMessages, assistantMessage]);

    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error connecting to the server. Please try again.',
        sender: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
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
                  <Ionicons name="stop" size={20} color="white" />
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
    backgroundColor: '#232a30',  // Light gray background like Google Messages
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
    borderRadius: 28,            // Larger radius to match mic button
    width: 56,                   // Increased to match textbox visual height
    height: 56,                  // Increased to match textbox visual height
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
    borderRadius: 28,           // Larger radius for bigger button
    width: 56,                  // Increased to match textbox visual height
    height: 56,                 // Increased to match textbox visual height
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 4,               // Reduced from 8 to 4
  },
  voiceButtonRecording: {
    backgroundColor: '#FF3B30', // Red for recording
    borderRadius: 28,           // Match other buttons
    width: 56,                  // Match textbox visual height
    height: 56,                 // Match textbox visual height
    justifyContent: 'center',
    alignItems: 'center',
  },
  recordingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f0f0f0',
    borderRadius: 25,
    paddingHorizontal: 6,        // Only horizontal padding for text
    paddingVertical: 0,          // No vertical padding so button can be full height
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

