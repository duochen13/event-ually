import React from 'react';
import './ChatMessage.css';

function ChatMessage({ message }) {
  const { role, content, created_at } = message;
  const isUser = role === 'user';

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className={`chat-message ${isUser ? 'user-message' : 'assistant-message'}`}>
      <div className="message-header">
        <span className="message-role">{isUser ? 'You' : 'AI Assistant'}</span>
        <span className="message-time">{formatTime(created_at)}</span>
      </div>
      <div className="message-content">
        {content}
      </div>
    </div>
  );
}

export default ChatMessage;
