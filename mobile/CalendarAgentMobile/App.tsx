import React, { useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { 
  StyleSheet, 
  Text, 
  View, 
  TextInput, 
  TouchableOpacity, 
  ScrollView 
} from 'react-native';

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

  return (
    <View style={styles.container}>
      <Text>Open up App.tsx to start working on your app!</Text>
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
});
