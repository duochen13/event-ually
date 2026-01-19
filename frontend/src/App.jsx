import React, { useState, useEffect, useRef } from 'react';
import { chatAPI } from './services/api';
import ConversationList from './components/ConversationList';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import BrowsingHistoryDetail from './components/BrowsingHistoryDetail';
import './App.css';

function App() {
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const [healthStatus, setHealthStatus] = useState(null);
  const [selectedHistoryDate, setSelectedHistoryDate] = useState(null);

  const messagesEndRef = useRef(null);

  // Fetch conversations on component mount
  useEffect(() => {
    fetchConversations();
    checkHealth();
  }, []);

  // Fetch messages when active conversation changes
  useEffect(() => {
    if (activeConversationId) {
      fetchConversation(activeConversationId);
    } else {
      setMessages([]);
    }
  }, [activeConversationId]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const checkHealth = async () => {
    try {
      const health = await chatAPI.healthCheck();
      setHealthStatus(health);
    } catch (err) {
      console.error('Health check failed:', err);
    }
  };

  const fetchConversations = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await chatAPI.getAllConversations();
      setConversations(data);

      // If no active conversation and conversations exist, select the first one
      if (!activeConversationId && data.length > 0) {
        setActiveConversationId(data[0].id);
      }
    } catch (err) {
      setError('Failed to fetch conversations. Is the backend running?');
      console.error('Error fetching conversations:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchConversation = async (conversationId) => {
    try {
      setLoading(true);
      setError(null);
      const data = await chatAPI.getConversation(conversationId);
      setMessages(data.messages);
    } catch (err) {
      setError('Failed to fetch messages');
      console.error('Error fetching conversation:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleNewConversation = async () => {
    try {
      const newConv = await chatAPI.createConversation();
      setConversations([newConv, ...conversations]);
      setActiveConversationId(newConv.id);
      setMessages([]);
    } catch (err) {
      alert('Failed to create conversation');
      console.error('Error creating conversation:', err);
    }
  };

  const handleSelectConversation = (conversationId) => {
    setActiveConversationId(conversationId);
  };

  const handleDeleteConversation = async (conversationId) => {
    try {
      await chatAPI.deleteConversation(conversationId);
      setConversations(conversations.filter((conv) => conv.id !== conversationId));

      // If deleted conversation was active, clear selection
      if (conversationId === activeConversationId) {
        setActiveConversationId(null);
        setMessages([]);
      }
    } catch (err) {
      alert('Failed to delete conversation');
      console.error('Error deleting conversation:', err);
    }
  };

  const handleSendMessage = async (content) => {
    if (!activeConversationId) {
      alert('Please select or create a conversation first');
      return;
    }

    try {
      setSending(true);
      const response = await chatAPI.sendMessage(activeConversationId, content);

      // Add both user message and assistant response to the UI
      setMessages([...messages, response.user_message, response.assistant_message]);

      // Update conversation list to reflect new message count
      fetchConversations();
    } catch (err) {
      alert('Failed to send message');
      console.error('Error sending message:', err);
    } finally {
      setSending(false);
    }
  };

  const handleSelectHistoryDate = (date) => {
    setSelectedHistoryDate(date);
    // Clear active conversation when viewing history
    setActiveConversationId(null);
  };

  return (
    <div className="app">
      <ConversationList
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
        onDeleteConversation={handleDeleteConversation}
        selectedHistoryDate={selectedHistoryDate}
        onSelectHistoryDate={handleSelectHistoryDate}
      />

      <div className="chat-container">
        <header className="chat-header">
          <div>
            <h1>AI Assistant</h1>
            <p className="subtitle">
              Your highly customized AI powered by Claude
              {healthStatus && !healthStatus.anthropic_configured && (
                <span className="warning"> (API key not configured)</span>
              )}
            </p>
          </div>
        </header>

        <main className="chat-main">
          {selectedHistoryDate ? (
            <BrowsingHistoryDetail selectedDate={selectedHistoryDate} />
          ) : !activeConversationId ? (
            <div className="empty-state">
              <h2>Welcome to your AI Assistant</h2>
              <p>Select a conversation or create a new one to get started</p>
              <button className="primary-button" onClick={handleNewConversation}>
                Start New Conversation
              </button>
            </div>
          ) : (
            <>
              {loading && messages.length === 0 && (
                <div className="loading">Loading messages...</div>
              )}
              {error && <div className="error">{error}</div>}

              <div className="messages">
                {messages.length === 0 && !loading ? (
                  <div className="empty-messages">
                    <p>No messages yet. Start the conversation!</p>
                  </div>
                ) : (
                  messages.map((message) => (
                    <ChatMessage key={message.id} message={message} />
                  ))
                )}
                {sending && (
                  <div className="typing-indicator">
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </>
          )}
        </main>

        {activeConversationId && !selectedHistoryDate && (
          <ChatInput onSend={handleSendMessage} disabled={sending} />
        )}
      </div>
    </div>
  );
}

export default App;
