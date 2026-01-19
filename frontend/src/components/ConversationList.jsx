import React, { useState } from 'react';
import BrowsingHistory from './BrowsingHistory';
import './ConversationList.css';

function ConversationList({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
  selectedHistoryDate,
  onSelectHistoryDate,
}) {
  const [activeTab, setActiveTab] = useState('conversations');

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
      {/* Tab Navigation */}
      <div className="sidebar-tabs">
        <button
          className={`tab-button ${activeTab === 'conversations' ? 'active' : ''}`}
          onClick={() => setActiveTab('conversations')}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
          <span>Conversations</span>
        </button>
        <button
          className={`tab-button ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
          <span>History</span>
        </button>
      </div>

      {/* Conversations View */}
      {activeTab === 'conversations' && (
        <>
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
        </>
      )}

      {/* Browsing History View */}
      {activeTab === 'history' && (
        <div className="history-tab-content">
          <BrowsingHistory
            selectedDate={selectedHistoryDate}
            onSelectDate={onSelectHistoryDate}
          />
        </div>
      )}
    </div>
  );
}

export default ConversationList;
