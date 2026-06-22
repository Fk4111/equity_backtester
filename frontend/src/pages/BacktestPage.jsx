import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { runBacktest } from '../services/api'

// Default form values
const defaultForm = {
  start_date: '2020-01-01',
  end_date: '2024-01-01',
  capital: 1000000,          // 10 Lakhs
  portfolio_size: 20,
  rebalance_frequency: 'quarterly',
  min_market_cap: '',
  max_market_cap: '',
  min_roce: '',
  pat_positive: true,
}

function BacktestPage() {
  const [form, setForm] = useState(defaultForm)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  // Generic handler for any form field change
  function handleChange(e) {
    const { name, value, type, checked } = e.target
    setForm((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      // Build payload - convert empty strings to null
      const payload = {
        start_date: form.start_date,
        end_date: form.end_date,
        capital: parseFloat(form.capital),
        portfolio_size: parseInt(form.portfolio_size),
        rebalance_frequency: form.rebalance_frequency,
        min_market_cap: form.min_market_cap ? parseFloat(form.min_market_cap) : null,
        max_market_cap: form.max_market_cap ? parseFloat(form.max_market_cap) : null,
        min_roce: form.min_roce ? parseFloat(form.min_roce) : null,
        pat_positive: form.pat_positive,
      }

      const response = await runBacktest(payload)

      // Store results in sessionStorage so ResultsPage can read them
      sessionStorage.setItem('backtestResult', JSON.stringify(response.data))

      // Navigate to results page
      navigate('/results')
    } catch (err) {
      const msg = err.response?.data?.detail || 'Something went wrong. Please try again.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold text-white mb-2">Configure Backtest</h1>
      <p className="text-gray-400 mb-8">
        Set your strategy parameters. The backtest will run on all NSE stocks in the database.
      </p>

      {error && (
        <div className="bg-red-900/30 border border-red-700 text-red-300 rounded-lg p-4 mb-6 text-sm">
          ⚠️ {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">

        {/* Date Range */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-white font-semibold mb-4">📅 Date Range</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-gray-400 text-sm block mb-1">Start Date</label>
              <input
                type="date"
                name="start_date"
                value={form.start_date}
                onChange={handleChange}
                required
                className="w-full bg-gray-800 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="text-gray-400 text-sm block mb-1">End Date</label>
              <input
                type="date"
                name="end_date"
                value={form.end_date}
                onChange={handleChange}
                required
                className="w-full bg-gray-800 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Portfolio Settings */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-white font-semibold mb-4">💰 Portfolio Settings</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-gray-400 text-sm block mb-1">
                Initial Capital (₹)
              </label>
              <input
                type="number"
                name="capital"
                value={form.capital}
                onChange={handleChange}
                min="10000"
                required
                className="w-full bg-gray-800 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="text-gray-400 text-sm block mb-1">
                Portfolio Size (# stocks)
              </label>
              <input
                type="number"
                name="portfolio_size"
                value={form.portfolio_size}
                onChange={handleChange}
                min="1"
                max="50"
                required
                className="w-full bg-gray-800 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          <div className="mt-4">
            <label className="text-gray-400 text-sm block mb-1">Rebalance Frequency</label>
            <select
              name="rebalance_frequency"
              value={form.rebalance_frequency}
              onChange={handleChange}
              className="w-full bg-gray-800 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
            >
              <option value="monthly">Monthly</option>
              <option value="quarterly">Quarterly</option>
              <option value="yearly">Yearly</option>
            </select>
          </div>
        </div>

        {/* Stock Filters */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-white font-semibold mb-4">🔍 Stock Filters</h2>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-gray-400 text-sm block mb-1">
                Min Market Cap (₹ Cr)
              </label>
              <input
                type="number"
                name="min_market_cap"
                value={form.min_market_cap}
                onChange={handleChange}
                placeholder="e.g. 1000"
                className="w-full bg-gray-800 border border-gray-700 text-white placeholder-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="text-gray-400 text-sm block mb-1">
                Max Market Cap (₹ Cr)
              </label>
              <input
                type="number"
                name="max_market_cap"
                value={form.max_market_cap}
                onChange={handleChange}
                placeholder="e.g. 50000"
                className="w-full bg-gray-800 border border-gray-700 text-white placeholder-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          <div className="mt-4">
            <label className="text-gray-400 text-sm block mb-1">
              Minimum ROCE (%)
            </label>
            <input
              type="number"
              name="min_roce"
              value={form.min_roce}
              onChange={handleChange}
              placeholder="e.g. 15"
              className="w-full bg-gray-800 border border-gray-700 text-white placeholder-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="mt-4 flex items-center gap-3">
            <input
              type="checkbox"
              id="pat_positive"
              name="pat_positive"
              checked={form.pat_positive}
              onChange={handleChange}
              className="w-4 h-4 accent-blue-500"
            />
            <label htmlFor="pat_positive" className="text-gray-300 text-sm">
              Only include stocks with positive PAT (Profit After Tax)
            </label>
          </div>
        </div>

        {/* Ranking Info */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-white font-semibold mb-2">🏆 Ranking Method</h2>
          <p className="text-gray-400 text-sm">
            Stocks are ranked using a composite score:
          </p>
          <ul className="mt-2 space-y-1 text-sm text-gray-400 list-disc list-inside">
            <li><span className="text-blue-300">ROE</span> — ranked descending (higher is better)</li>
            <li><span className="text-blue-300">PE Ratio</span> — ranked ascending (lower is cheaper)</li>
            <li>Final rank = average of both individual ranks</li>
          </ul>
          <p className="text-gray-500 text-xs mt-2">Top N stocks by composite rank are selected.</p>
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 disabled:cursor-not-allowed text-white py-3 rounded-xl font-semibold text-lg transition-colors"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Running Backtest...
            </span>
          ) : (
            'Run Backtest →'
          )}
        </button>
      </form>
    </div>
  )
}

export default BacktestPage
