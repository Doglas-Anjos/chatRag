import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { PaperAirplaneIcon } from '@heroicons/react/24/solid';

// Define API base URL
const API_BASE_URL = 'http://localhost:8000/api';

// Define interfaces for our data types
interface Message {
  id: number;
  content: string;
  is_user: boolean;
  created_at: string;
}

interface Chat {
  id: number;
  title: string;
  messages: Message[];
}

function App() {
  const [chats, setChats] = useState<Chat[]>([]);
  const [currentChat, setCurrentChat] = useState<Chat | null>(null);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Configure axios defaults
  axios.defaults.baseURL = API_BASE_URL;

  useEffect(() => {
    fetchChats();
  }, []);

  const fetchChats = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await axios.get('/chats/');
      setChats(response.data);
    } catch (err) {
      console.error('Error fetching chats:', err);
      setError('Failed to fetch chats. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const createNewChat = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await axios.post('/chats/', {
        title: `New Chat ${chats.length + 1}`
      });
      const newChat = response.data;
      setChats(prevChats => [...prevChats, newChat]);
      setCurrentChat(newChat);
    } catch (err) {
      console.error('Error creating chat:', err);
      setError('Failed to create new chat. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || !currentChat || isLoading) return;

    setIsLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(
        `/chats/${currentChat.id}/send_message/`,
        { message: message.trim() }
      );

      // Update the current chat with new messages
      const updatedChat = {
        ...currentChat,
        messages: [
          ...currentChat.messages,
          {
            id: Date.now(),
            content: message,
            is_user: true,
            created_at: new Date().toISOString()
          },
          {
            id: Date.now() + 1,
            content: response.data.message,
            is_user: false,
            created_at: new Date().toISOString()
          }
        ]
      };

      setCurrentChat(updatedChat);
      setChats(prevChats =>
        prevChats.map(chat =>
          chat.id === currentChat.id ? updatedChat : chat
        )
      );
      setMessage('');
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to send message. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-lg">
        <div className="p-4">
          <button
            onClick={createNewChat}
            disabled={isLoading}
            className={`w-full py-2 px-4 rounded-lg transition-colors ${
              isLoading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-500 hover:bg-blue-600 text-white'
            }`}
          >
            {isLoading ? 'Creating...' : 'New Chat'}
          </button>
        </div>
        <div className="overflow-y-auto h-[calc(100vh-4rem)]">
          {chats.map((chat) => (
            <div
              key={chat.id}
              onClick={() => setCurrentChat(chat)}
              className={`p-4 cursor-pointer hover:bg-gray-100 ${
                currentChat?.id === chat.id ? 'bg-gray-100' : ''
              }`}
            >
              {chat.title}
            </div>
          ))}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {error && (
          <div className="p-4 bg-red-100 text-red-700 text-center">
            {error}
          </div>
        )}
        {currentChat ? (
          <>
            <div className="flex-1 overflow-y-auto p-4">
              {currentChat.messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`mb-4 ${
                    msg.is_user ? 'text-right' : 'text-left'
                  }`}
                >
                  <div
                    className={`inline-block p-3 rounded-lg ${
                      msg.is_user
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-200 text-gray-800'
                    }`}
                  >
                    {msg.content}
                  </div>
                </div>
              ))}
            </div>
            <form onSubmit={sendMessage} className="p-4 border-t">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Type your message..."
                  className="flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  disabled={isLoading || !message.trim()}
                  className={`p-2 rounded-lg transition-colors ${
                    isLoading || !message.trim()
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-blue-500 hover:bg-blue-600 text-white'
                  }`}
                >
                  <PaperAirplaneIcon className="h-6 w-6" />
                </button>
              </div>
            </form>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            Select a chat or create a new one
          </div>
        )}
      </div>
    </div>
  );
}

export default App; 