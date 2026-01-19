import React, { useState, useEffect, useRef } from 'react';
import { chatAPI } from '../services/api';
import './BrowsingHistory.css';

function BrowsingHistory() {
  const [dailyStats, setDailyStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingItems, setLoadingItems] = useState(new Set());
  const [error, setError] = useState(null);
  const isLoadingRef = useRef(false);

  useEffect(() => {
    fetchBrowsingHistoryProgressive();
  }, []);

  const fetchBrowsingHistoryProgressive = async () => {
    if (isLoadingRef.current) return;
    isLoadingRef.current = true;

    try {
      setLoading(true);
      setError(null);

      // Step 1: Load today's data first (fast)
      const todayData = await chatAPI.getDailyBrowsingStats(1);
      if (todayData.daily_stats && todayData.daily_stats.length > 0) {
        setDailyStats(todayData.daily_stats);
        setLoading(false);
      }

      // Step 2: Load remaining days in background
      const remainingDays = [2, 3, 4, 5, 6, 7];

      for (const dayCount of remainingDays) {
        setLoadingItems(prev => new Set([...prev, dayCount]));

        try {
          const data = await chatAPI.getDailyBrowsingStats(dayCount);

          if (data.daily_stats && data.daily_stats.length > 0) {
            // Get the new days (all except the first one which we already have)
            const newDays = data.daily_stats.slice(1);

            setDailyStats(prev => {
              // Merge new days, avoiding duplicates
              const existingDates = new Set(prev.map(d => d.date));
              const uniqueNewDays = newDays.filter(d => !existingDates.has(d.date));
              return [...prev, ...uniqueNewDays];
            });
          }
        } catch (err) {
          console.error(`Error loading day ${dayCount}:`, err);
        } finally {
          setLoadingItems(prev => {
            const newSet = new Set(prev);
            newSet.delete(dayCount);
            return newSet;
          });
        }
      }
    } catch (err) {
      setError('Failed to load browsing history');
      console.error('Error fetching browsing history:', err);
      setLoading(false);
    } finally {
      isLoadingRef.current = false;
    }
  };

  const fetchBrowsingHistory = async () => {
    // Fallback: load all at once
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

  const renderSkeletonItem = () => (
    <div className="history-item skeleton-item">
      <div className="skeleton-line skeleton-date"></div>
      <div className="skeleton-line skeleton-stats"></div>
      <div className="skeleton-line skeleton-category"></div>
    </div>
  );

  const totalDaysToShow = 7;
  const skeletonCount = Math.max(0, totalDaysToShow - dailyStats.length);

  return (
    <div className="browsing-history">
      <div className="history-content">
        {dailyStats.length === 0 && !loading ? (
          <div className="no-history">No browsing data available</div>
        ) : (
          <div className="history-list">
            {/* Show loaded items */}
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

            {/* Show skeleton loaders for items still loading */}
            {loadingItems.size > 0 && Array.from({ length: skeletonCount }).map((_, idx) => (
              <React.Fragment key={`skeleton-${idx}`}>
                {renderSkeletonItem()}
              </React.Fragment>
            ))}
          </div>
        )}

        <button
          className="refresh-button"
          onClick={fetchBrowsingHistoryProgressive}
          disabled={loading && dailyStats.length === 0}
        >
          ↻ Refresh
        </button>
      </div>
    </div>
  );
}

export default BrowsingHistory;
