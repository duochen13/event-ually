import React from 'react';
import './ConversationList.css';

function ConversationList({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
}) {
  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = (now - date) / (1000 * 60 * 60);

    if (diffInHours < 24) {
      return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
      });
    } else if (diffInHours < 168) {
      return date.toLocaleDateString('en-US', { weekday: 'short' });
    } else {
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      });
    }
  };

  return (
    <div className="conversation-list">
      <div className="conversation-list-header">
        <h2>Conversations</h2>
        <button className="new-conversation-btn" onClick={onNewConversation} title="New Conversation">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
        </button>
      </div>

      <div className="conversations">
        {conversations.length === 0 ? (
          <div className="no-conversations">
            <p>No conversations yet</p>
            <p className="hint">Click + to start</p>
          </div>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.id}
              className={`conversation-item ${
                conv.id === activeConversationId ? 'active' : ''
              }`}
              onClick={() => onSelectConversation(conv.id)}
            >
              <div className="conversation-content">
                <div className="conversation-title">{conv.title}</div>
                <div className="conversation-meta">
                  <span className="message-count">{conv.message_count} messages</span>
                  <span className="conversation-date">{formatDate(conv.updated_at)}</span>
                </div>
              </div>
              <button
                className="delete-conversation-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  if (window.confirm('Delete this conversation?')) {
                    onDeleteConversation(conv.id);
                  }
                }}
                title="Delete conversation"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default ConversationList;
