import { useState, useEffect } from 'react'
import { fetchAllStocks, triggerDataFetch } from '../services/api'

function StocksPage() {
  const [stocks, setStocks] = useState([])
  const [loading, setLoading] = useState(true)
  const [fetching, setFetching] = useState(false)
  const [search, setSearch] = useState('')
  const [message, setMessage] = useState(null)

  useEffect(() => {
    loadStocks()
  }, [])

  async function loadStocks() {
    setLoading(true)
    try {
      const res = await fetchAllStocks()
      setStocks(res.data)
    } catch (err) {
      console.error('Failed to load stocks:', err)
    } finally {
      setLoading(false)
    }
  }

  async function handleFetchData() {
    setFetching(true)
    setMessage(null)
    try {
      await triggerDataFetch()
      setMessage('Data fetch started! This runs in the background and may take 5–10 minutes. Refresh this page after a while.')
    } catch (err) {
      setMessage('Failed to start data fetch. Is the backend running?')
    } finally {
      setFetching(false)
    }
  }

  // Filter stocks based on search input
  const filtered = stocks.filter((s) =>
    s.symbol.toLowerCase().includes(search.toLowerCase()) ||
    (s.company_name || '').toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Stocks Database</h1>
          <p className="text-gray-400 mt-1">
            {stocks.length} stocks loaded from NSE via Yahoo Finance
          </p>
        </div>
        <button
          onClick={handleFetchData}
          disabled={fetching}
          className="bg-green-700 hover:bg-green-600 disabled:bg-green-900 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          {fetching ? 'Starting...' : '🔄 Fetch Fresh Data'}
        </button>
      </div>

      {/* Info Banner */}
      {message && (
        <div className="bg-blue-900/30 border border-blue-700 text-blue-300 rounded-lg p-4 mb-6 text-sm">
          ℹ️ {message}
        </div>
      )}

      {stocks.length === 0 && !loading && (
        <div className="bg-yellow-900/20 border border-yellow-700 text-yellow-300 rounded-lg p-5 mb-6 text-sm">
          <p className="font-medium">No stocks in the database yet.</p>
          <p className="mt-1 text-yellow-400">
            Click "Fetch Fresh Data" to download stock data from Yahoo Finance.
            This will take a few minutes.
          </p>
        </div>
      )}

      {/* Search */}
      <input
        type="text"
        placeholder="Search by symbol or company name..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full bg-gray-800 border border-gray-700 text-white placeholder-gray-500 rounded-lg px-4 py-2.5 mb-6 focus:outline-none focus:border-blue-500"
      />

      {/* Table */}
      {loading ? (
        <div className="text-center py-16 text-gray-400">Loading stocks...</div>
      ) : (
        <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800">
                <th className="text-left text-gray-400 py-3 px-4">Symbol</th>
                <th className="text-left text-gray-400 py-3 px-4">Company Name</th>
                <th className="text-left text-gray-400 py-3 px-4">Sector</th>
                <th className="text-right text-gray-400 py-3 px-4">Market Cap (₹ Cr)</th>
                <th className="text-right text-gray-400 py-3 px-4">PE Ratio</th>
                <th className="text-right text-gray-400 py-3 px-4">ROE (%)</th>
                <th className="text-right text-gray-400 py-3 px-4">ROCE (%)</th>
                <th className="text-right text-gray-400 py-3 px-4">PAT (₹ Cr)</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={8} className="text-center py-8 text-gray-500">
                    No stocks match your search.
                  </td>
                </tr>
              )}
              {filtered.map((stock) => {
                const f = stock.fundamentals?.[0] || {}
                return (
                  <tr
                    key={stock.id}
                    className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors"
                  >
                    <td className="py-2.5 px-4 font-bold text-blue-400">{stock.symbol}</td>
                    <td className="py-2.5 px-4 text-white">{stock.company_name || '—'}</td>
                    <td className="py-2.5 px-4 text-gray-400">{stock.sector || '—'}</td>
                    <td className="py-2.5 px-4 text-right text-gray-300">
                      {f.market_cap ? Number(f.market_cap).toLocaleString('en-IN') : '—'}
                    </td>
                    <td className="py-2.5 px-4 text-right text-gray-300">
                      {f.pe_ratio ? Number(f.pe_ratio).toFixed(1) : '—'}
                    </td>
                    <td className="py-2.5 px-4 text-right text-gray-300">
                      {f.roe ? `${Number(f.roe).toFixed(1)}%` : '—'}
                    </td>
                    <td className="py-2.5 px-4 text-right text-gray-300">
                      {f.roce ? `${Number(f.roce).toFixed(1)}%` : '—'}
                    </td>
                    <td className={`py-2.5 px-4 text-right font-medium ${
                      f.pat > 0 ? 'text-green-400' : f.pat < 0 ? 'text-red-400' : 'text-gray-500'
                    }`}>
                      {f.pat ? Number(f.pat).toLocaleString('en-IN', { maximumFractionDigits: 0 }) : '—'}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default StocksPage
