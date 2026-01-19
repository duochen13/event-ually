import React, { useState, useEffect } from 'react';
import { chatAPI } from '../services/api';
import BrowsingChart from './BrowsingChart';
import ReactMarkdown from 'react-markdown';
import './BrowsingHistoryDetail.css';

function BrowsingHistoryDetail({ selectedDate }) {
  const [loading, setLoading] = useState(true);
  const [reportData, setReportData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (selectedDate) {
      fetchDayDetail();
    }
  }, [selectedDate]);

  const fetchDayDetail = async () => {
    try {
      setLoading(true);
      setError(null);

      // Calculate how many days ago this date was
      const targetDate = new Date(selectedDate);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      targetDate.setHours(0, 0, 0, 0);

      const diffTime = today - targetDate;
      const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

      // Fetch data for that number of days
      const days = diffDays + 1;
      const data = await chatAPI.getDailyBrowsingStats(days);

      // Find the specific day's data
      const dayData = data.daily_stats.find(d => d.date === selectedDate);

      if (dayData) {
        // Generate report-like data for display
        setReportData(dayData);
      } else {
        setError('No data found for this date');
      }
    } catch (err) {
      setError('Failed to load day details');
      console.error('Error fetching day detail:', err);
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

  const generateChartData = (categories) => {
    if (!categories) return null;

    const chartItems = Object.entries(categories).map(([name, info]) => ({
      category: name,
      minutes: Math.round(info.time / 60),
      hours: Math.round((info.time / 3600) * 100) / 100,
      visits: info.visits
    }));

    // Sort by time descending
    chartItems.sort((a, b) => b.minutes - a.minutes);

    return {
      type: 'bar',
      title: 'Time Spent by Category',
      data: chartItems,
      xAxis: 'category',
      yAxis: 'minutes',
      yAxisLabel: 'Time (minutes)'
    };
  };

  if (loading) {
    return (
      <div className="history-detail">
        <div className="detail-loading">Loading day details...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="history-detail">
        <div className="detail-error">{error}</div>
      </div>
    );
  }

  if (!reportData) {
    return (
      <div className="history-detail">
        <div className="detail-empty">Select a date to view details</div>
      </div>
    );
  }

  const chartData = generateChartData(reportData.categories);

  return (
    <div className="history-detail">
      <div className="detail-header">
        <h1>Browsing Report - {reportData.day_name}, {reportData.date}</h1>
      </div>

      <div className="detail-content">
        {/* Chart */}
        {chartData && chartData.data.length > 0 && (
          <div className="detail-chart">
            <BrowsingChart chartData={chartData} />
          </div>
        )}

        {/* Summary */}
        <div className="detail-section">
          <h2>Summary</h2>
          <div className="summary-stats">
            <div className="summary-item">
              <span className="summary-label">Total Time</span>
              <span className="summary-value">{formatDuration(reportData.total_time)}</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Pages Visited</span>
              <span className="summary-value">{reportData.total_visits}</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Unique Sites</span>
              <span className="summary-value">{reportData.unique_sites}</span>
            </div>
            {reportData.top_category && (
              <div className="summary-item">
                <span className="summary-label">Top Category</span>
                <span className="summary-value">
                  {reportData.top_category.name} ({reportData.top_category.percentage}%)
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Category Breakdown */}
        {reportData.categories && Object.keys(reportData.categories).length > 0 && (
          <div className="detail-section">
            <h2>Time by Category</h2>
            <div className="category-list">
              {Object.entries(reportData.categories)
                .sort(([, a], [, b]) => b.time - a.time)
                .map(([name, info]) => (
                  <div key={name} className="category-item">
                    <div className="category-info">
                      <span className="category-name">{name}</span>
                      <span className="category-stats">
                        {formatDuration(info.time)} • {info.visits} visits • {info.percentage}%
                      </span>
                    </div>
                    <div className="category-bar">
                      <div
                        className="category-bar-fill"
                        style={{ width: `${info.percentage}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default BrowsingHistoryDetail;
