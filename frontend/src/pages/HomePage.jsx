import { Link } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { getStockCount } from '../services/api'

function HomePage() {
  const [stockCount, setStockCount] = useState(null)

  useEffect(() => {
    getStockCount()
      .then((res) => setStockCount(res.data.total_stocks))
      .catch(() => setStockCount('—'))
  }, [])

  const features = [
    {
      icon: '🔍',
      title: 'Filter Stocks',
      desc: 'Filter by Market Cap, ROCE, and positive PAT to narrow down your universe.',
    },
    {
      icon: '📊',
      title: 'Rank & Select',
      desc: 'Rank stocks by ROE, PE ratio, or a composite score. Pick your top N.',
    },
    {
      icon: '⚖️',
      title: 'Equal Weight',
      desc: 'Allocate equal capital to each stock in the portfolio.',
    },
    {
      icon: '🔄',
      title: 'Rebalance',
      desc: 'Rebalance monthly, quarterly, or yearly. No future data leakage.',
    },
    {
      icon: '📈',
      title: 'Equity Curve',
      desc: 'Visualize your portfolio value growing over time.',
    },
    {
      icon: '📉',
      title: 'Drawdown Chart',
      desc: 'See your worst peak-to-trough declines clearly.',
    },
  ]

  return (
    <div className="max-w-5xl mx-auto">
      {/* Hero */}
      <div className="text-center py-16">
        <h1 className="text-5xl font-bold text-white mb-4">
          Indian Equity{' '}
          <span className="text-blue-400">Backtester</span>
        </h1>
        <p className="text-gray-400 text-xl max-w-2xl mx-auto mb-8">
          Test fundamental investing strategies on 100+ NSE-listed stocks.
          Define filters, rank by metrics, and see how your strategy performed.
        </p>
        <div className="flex items-center justify-center gap-4">
          <Link
            to="/backtest"
            className="bg-blue-600 hover:bg-blue-500 text-white px-8 py-3 rounded-lg font-semibold transition-colors"
          >
            Run a Backtest →
          </Link>
          <Link
            to="/stocks"
            className="bg-gray-800 hover:bg-gray-700 text-gray-300 px-8 py-3 rounded-lg font-semibold transition-colors"
          >
            Browse Stocks
          </Link>
        </div>
      </div>

      {/* Stats bar */}
      <div className="grid grid-cols-3 gap-4 mb-16">
        {[
          { label: 'Stocks in Database', value: stockCount ?? '...', color: 'text-blue-400' },
          { label: 'Data Source', value: 'NSE / Yahoo Finance', color: 'text-green-400' },
          { label: 'Strategy Type', value: 'Fundamental', color: 'text-purple-400' },
        ].map((stat) => (
          <div
            key={stat.label}
            className="bg-gray-900 border border-gray-800 rounded-xl p-6 text-center"
          >
            <p className={`text-3xl font-bold ${stat.color}`}>{stat.value}</p>
            <p className="text-gray-400 text-sm mt-1">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Feature grid */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-6">What you can do</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map((f) => (
            <div
              key={f.title}
              className="bg-gray-900 border border-gray-800 rounded-xl p-5 hover:border-blue-800 transition-colors"
            >
              <span className="text-2xl">{f.icon}</span>
              <h3 className="text-white font-semibold mt-3 mb-1">{f.title}</h3>
              <p className="text-gray-400 text-sm">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* How it works */}
      <div className="mt-16 bg-gray-900 border border-gray-800 rounded-xl p-8">
        <h2 className="text-2xl font-bold text-white mb-4">How it works</h2>
        <ol className="space-y-3 text-gray-400">
          <li className="flex gap-3">
            <span className="text-blue-400 font-bold">1.</span>
            Set your backtest date range, starting capital, and portfolio size.
          </li>
          <li className="flex gap-3">
            <span className="text-blue-400 font-bold">2.</span>
            Apply stock filters: market cap range, minimum ROCE, and positive PAT.
          </li>
          <li className="flex gap-3">
            <span className="text-blue-400 font-bold">3.</span>
            Stocks are ranked by ROE and PE ratio (composite rank). Top N are selected.
          </li>
          <li className="flex gap-3">
            <span className="text-blue-400 font-bold">4.</span>
            Capital is equally distributed among selected stocks.
          </li>
          <li className="flex gap-3">
            <span className="text-blue-400 font-bold">5.</span>
            Portfolio rebalances on your chosen frequency using historical prices only (no lookahead).
          </li>
          <li className="flex gap-3">
            <span className="text-blue-400 font-bold">6.</span>
            View CAGR, Sharpe Ratio, Max Drawdown, equity curve, and download results as CSV.
          </li>
        </ol>
      </div>
    </div>
  )
}

export default HomePage
