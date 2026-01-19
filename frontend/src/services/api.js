import axios from 'axios';

// Use environment variable for API URL, fallback to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatAPI = {
  // ============ Conversation Operations ============

  // GET all conversations
  getAllConversations: async () => {
    const response = await api.get('/conversations');
    return response.data;
  },

  // GET single conversation with messages
  getConversation: async (id) => {
    const response = await api.get(`/conversations/${id}`);
    return response.data;
  },

  // POST create conversation
  createConversation: async (title) => {
    const response = await api.post('/conversations', { title });
    return response.data;
  },

  // DELETE conversation
  deleteConversation: async (id) => {
    const response = await api.delete(`/conversations/${id}`);
    return response.data;
  },

  // PUT update conversation title
  updateConversationTitle: async (id, title) => {
    const response = await api.put(`/conversations/${id}/title`, { title });
    return response.data;
  },

  // ============ Message Operations ============

  // POST send message and get AI response
  sendMessage: async (conversationId, content, metadata = {}) => {
    const response = await api.post(`/conversations/${conversationId}/messages`, {
      content,
      metadata,
    });
    return response.data;
  },

  // ============ Data Source Operations ============

  // GET all data sources
  getAllDataSources: async () => {
    const response = await api.get('/data-sources');
    return response.data;
  },

  // POST create data source
  createDataSource: async (dataSourceData) => {
    const response = await api.post('/data-sources', dataSourceData);
    return response.data;
  },

  // PUT update data source
  updateDataSource: async (id, dataSourceData) => {
    const response = await api.put(`/data-sources/${id}`, dataSourceData);
    return response.data;
  },

  // DELETE data source
  deleteDataSource: async (id) => {
    const response = await api.delete(`/data-sources/${id}`);
    return response.data;
  },

  // POST add context to data source
  addContext: async (dataSourceId, content, summary = null) => {
    const response = await api.post(`/data-sources/${dataSourceId}/contexts`, {
      content,
      summary,
    });
    return response.data;
  },

  // ============ Browsing History Stats ============

  // GET daily browsing stats
  getDailyBrowsingStats: async (days = 7) => {
    const response = await api.get(`/browsing-history/daily?days=${days}`);
    return response.data;
  },

  // GET weekly browsing summary
  getWeeklyBrowsingSummary: async () => {
    const response = await api.get('/browsing-history/weekly');
    return response.data;
  },

  // ============ Health Check ============

  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
