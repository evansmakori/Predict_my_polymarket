import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Markets API
export const marketsApi = {
  // Get list of markets with filters
  getMarkets: async (filters = {}) => {
    const response = await api.get('/api/markets/', { params: filters })
    return response.data
  },

  // Get market by ID
  getMarket: async (marketId) => {
    const response = await api.get(`/api/markets/${marketId}`)
    return response.data
  },

  // Get market statistics
  getMarketStats: async (marketId) => {
    const response = await api.get(`/api/markets/${marketId}/stats`)
    return response.data
  },

  // Get market price history
  getMarketHistory: async (marketId, interval = '1w', limit = 1000) => {
    const response = await api.get(`/api/markets/${marketId}/history`, {
      params: { interval, limit }
    })
    return response.data
  },

  // Get market orderbook
  getMarketOrderbook: async (marketId) => {
    const response = await api.get(`/api/markets/${marketId}/orderbook`)
    return response.data
  },

  // Get categories
  getCategories: async () => {
    const response = await api.get('/api/markets/categories')
    return response.data
  },

  // Get market count
  getMarketCount: async () => {
    const response = await api.get('/api/markets/count')
    return response.data
  },

  // Extract market data from URL
  extractMarket: async (data) => {
    const response = await api.post('/api/markets/extract', data)
    return response.data
  },
}

// WebSocket connection helper
export const createWebSocket = (marketId) => {
  const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000'
  return new WebSocket(`${WS_BASE_URL}/ws/markets/${marketId}`)
}

export const createAllMarketsWebSocket = () => {
  const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000'
  return new WebSocket(`${WS_BASE_URL}/ws/markets`)
}

export default api
