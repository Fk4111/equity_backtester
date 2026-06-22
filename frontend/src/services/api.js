import axios from 'axios'

// Base URL for all API calls
// In development, Vite proxies /api to http://localhost:8000
const api = axios.create({
  baseURL: '/api',
  timeout: 120000, // 2 minutes timeout for backtest runs
  headers: {
    'Content-Type': 'application/json',
  },
})

// ---- Stock API Calls ----

export const fetchAllStocks = () => api.get('/stocks/')

export const fetchStockData = (symbol) => api.get(`/stocks/${symbol}`)

export const triggerDataFetch = () => api.post('/stocks/fetch')

export const getStockCount = () => api.get('/stocks/count/total')

// ---- Backtest API Calls ----

export const runBacktest = (payload) => api.post('/backtest/run', payload)

export const getBacktestById = (id) => api.get(`/backtest/${id}`)

export const getAllBacktests = () => api.get('/backtest/history/all')

export const exportBacktestCSV = (id) => {
  // Open CSV download directly in browser
  window.open(`/api/backtest/${id}/export/csv`, '_blank')
}

export default api
