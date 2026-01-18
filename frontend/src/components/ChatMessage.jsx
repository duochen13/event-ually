import React from 'react';
import ReactMarkdown from 'react-markdown';
import BrowsingChart from './BrowsingChart';
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

  // Extract chart data if present
  const extractChartData = (text) => {
    const chartMatch = text.match(/```chart\n([\s\S]*?)\n```/);
    if (chartMatch) {
      try {
        const chartData = JSON.parse(chartMatch[1]);
        const contentWithoutChart = text.replace(/```chart\n[\s\S]*?\n```\n\n/, '');
        return { chartData, content: contentWithoutChart };
      } catch (e) {
        console.error('Failed to parse chart data:', e);
        return { chartData: null, content: text };
      }
    }
    return { chartData: null, content: text };
  };

  const { chartData, content: processedContent } = !isUser ? extractChartData(content) : { chartData: null, content };

  // Detect if content contains markdown (headers, lists, bold, etc.)
  const isMarkdown = !isUser && (
    processedContent.includes('\n## ') ||
    processedContent.includes('\n### ') ||
    processedContent.includes('\n- ') ||
    processedContent.includes('**') ||
    processedContent.includes('# Daily Browsing Review') ||
    processedContent.includes('# Available Commands') ||
    processedContent.includes('# Help:')
  );

  return (
    <div className={`chat-message ${isUser ? 'user-message' : 'assistant-message'}`}>
      <div className="message-header">
        <span className="message-role">{isUser ? 'You' : 'AI Assistant'}</span>
        <span className="message-time">{formatTime(created_at)}</span>
      </div>
      <div className="message-content">
        {chartData && <BrowsingChart chartData={chartData} />}
        {isMarkdown ? (
          <ReactMarkdown>{processedContent}</ReactMarkdown>
        ) : (
          processedContent
        )}
      </div>
    </div>
  );
}

export default ChatMessage;
