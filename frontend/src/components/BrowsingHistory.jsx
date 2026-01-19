import React, { useState, useEffect } from 'react';
import { chatAPI } from '../services/api';
import './BrowsingHistory.css';

function BrowsingHistory() {
  const [dailyStats, setDailyStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchBrowsingHistory();
  }, []);

  const fetchBrowsingHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await chatAPI.getDailyBrowsingStats(7);
      setDailyStats(data.daily_stats || []);
    } catch (err) {
      setError('Failed to load browsing history');
      console.error('Error fetching browsing history:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDuration = (seconds) => {
    if (seconds === 0) return '0m';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.round((seconds % 3600) / 60);

    if (hours > 0) {
      return minutes > 0 ? `${hours}h ${minutes}m` : `${hours}h`;
    }
    return `${minutes}m`;
  };

  const isToday = (dateStr) => {
    const today = new Date().toISOString().split('T')[0];
    return dateStr === today;
  };

  const isYesterday = (dateStr) => {
    const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];
    return dateStr === yesterday;
  };

  const formatDate = (dateStr, dayName) => {
    if (isToday(dateStr)) return 'Today';
    if (isYesterday(dateStr)) return 'Yesterday';
    return dayName;
  };

  if (loading) {
    return (
      <div className="browsing-history">
        <div className="history-loading">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="browsing-history">
        <div className="history-error">{error}</div>
      </div>
    );
  }

  return (
    <div className="browsing-history">
      <div className="history-content">
        {dailyStats.length === 0 ? (
          <div className="no-history">No browsing data available</div>
        ) : (
          <div className="history-list">
            {dailyStats.map((day, index) => (
              <div
                key={index}
                className={`history-item ${day.total_visits === 0 ? 'no-data' : ''}`}
              >
                <div className="history-date">
                  <span className="day-label">{formatDate(day.date, day.day_name)}</span>
                  <span className="date-label">{day.date.slice(5)}</span>
                </div>

                {day.total_visits > 0 ? (
                  <>
                    <div className="history-stats">
                      <div className="stat">
                        <span className="stat-icon">🕒</span>
                        <span className="stat-value">{formatDuration(day.total_time)}</span>
                      </div>
                      <div className="stat">
                        <span className="stat-icon">🌐</span>
                        <span className="stat-value">{day.total_visits}</span>
                      </div>
                    </div>

                    {day.top_category && (
                      <div className="top-category">
                        <span className="category-badge">
                          {day.top_category.name}
                        </span>
                        <span className="category-percent">
                          {day.top_category.percentage}%
                        </span>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="no-activity">No activity</div>
                )}
              </div>
            ))}
          </div>
        )}

        <button className="refresh-button" onClick={fetchBrowsingHistory}>
          ↻ Refresh
        </button>
      </div>
    </div>
  );
}

export default BrowsingHistory;
