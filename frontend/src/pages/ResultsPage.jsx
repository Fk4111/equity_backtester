import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import MetricCard from '../components/MetricCard'
import EquityChart from '../components/EquityChart'
import DrawdownChart from '../components/DrawdownChart'
import PortfolioLogsTable from '../components/PortfolioLogsTable'
import { exportBacktestCSV } from '../services/api'

function ResultsPage() {
  const [result, setResult] = useState(null)
  const [activeTab, setActiveTab] = useState('overview')
  const navigate = useNavigate()

  useEffect(() => {
    // Load result from sessionStorage (set by BacktestPage after a successful run)
    const stored = sessionStorage.getItem('backtestResult')
    if (!stored) {
      // If no result, send user back to the form
      navigate('/backtest')
      return
    }
    setResult(JSON.parse(stored))
  }, [navigate])

  if (!result) {
    return (
      <div className="text-center py-20 text-gray-400">
        Loading results...
      </div>
    )
  }

  // Format number as Indian rupees
  const formatINR = (val) =>
    `₹${Number(val).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`

  const tabs = ['overview', 'charts', 'portfolio']

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Backtest Results</h1>
          <p className="text-gray-400 mt-1">
            {result.start_date} → {result.end_date} · Backtest #{result.backtest_id}
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => exportBacktestCSV(result.backtest_id)}
            className="bg-gray-800 hover:bg-gray-700 text-gray-300 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            ⬇ Export CSV
          </button>
          <Link
            to="/backtest"
            className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            Run Another →
          </Link>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-1 mb-6 bg-gray-900 border border-gray-800 rounded-lg p-1 w-fit">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-5 py-2 rounded-md text-sm font-medium capitalize transition-colors ${
              activeTab === tab
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Capital summary */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Initial Capital</p>
              <p className="text-2xl font-bold text-white">{formatINR(result.initial_capital)}</p>
            </div>
            <div className="text-4xl text-gray-600">→</div>
            <div>
              <p className="text-gray-400 text-sm">Final Value</p>
              <p className="text-2xl font-bold text-green-400">{formatINR(result.final_value)}</p>
            </div>
            <div className="text-right">
              <p className="text-gray-400 text-sm">Profit / Loss</p>
              <p className={`text-2xl font-bold ${result.final_value >= result.initial_capital ? 'text-green-400' : 'text-red-400'}`}>
                {formatINR(result.final_value - result.initial_capital)}
              </p>
            </div>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MetricCard
              label="CAGR"
              value={result.cagr}
              suffix="%"
              color={result.cagr >= 0 ? 'green' : 'red'}
              subtitle="Compounded Annual Growth Rate"
            />
            <MetricCard
              label="Total Return"
              value={result.total_return}
              suffix="%"
              color={result.total_return >= 0 ? 'green' : 'red'}
              subtitle="Absolute return over period"
            />
            <MetricCard
              label="Sharpe Ratio"
              value={result.sharpe_ratio}
              color={result.sharpe_ratio >= 1 ? 'green' : result.sharpe_ratio >= 0 ? 'yellow' : 'red'}
              subtitle="Risk-adjusted return (>1 is good)"
            />
            <MetricCard
              label="Max Drawdown"
              value={result.max_drawdown}
              suffix="%"
              color="red"
              subtitle="Worst peak-to-trough decline"
            />
          </div>

          {/* Winners and Losers */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Top Winners */}
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <h3 className="text-white font-semibold mb-4">🏆 Top Winners</h3>
              <div className="space-y-2">
                {result.top_winners.length === 0 && (
                  <p className="text-gray-500 text-sm">No data</p>
                )}
                {result.top_winners.map((stock, i) => (
                  <div key={i} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-gray-500 text-sm w-5">{i + 1}</span>
                      <span className="text-white text-sm font-medium">{stock.symbol}</span>
                    </div>
                    <span className="text-green-400 font-medium text-sm">
                      +{stock.return_percent?.toFixed(2)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Top Losers */}
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <h3 className="text-white font-semibold mb-4">📉 Top Losers</h3>
              <div className="space-y-2">
                {result.top_losers.length === 0 && (
                  <p className="text-gray-500 text-sm">No data</p>
                )}
                {result.top_losers.map((stock, i) => (
                  <div key={i} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-gray-500 text-sm w-5">{i + 1}</span>
                      <span className="text-white text-sm font-medium">{stock.symbol}</span>
                    </div>
                    <span className="text-red-400 font-medium text-sm">
                      {stock.return_percent?.toFixed(2)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Charts Tab */}
      {activeTab === 'charts' && (
        <div className="space-y-6">
          <EquityChart data={result.equity_curve} />
          <DrawdownChart data={result.drawdown_series} />
        </div>
      )}

      {/* Portfolio Logs Tab */}
      {activeTab === 'portfolio' && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl">
          <div className="flex items-center justify-between p-5 border-b border-gray-800">
            <h3 className="text-white font-semibold">Portfolio Logs</h3>
            <span className="text-gray-500 text-sm">
              {result.portfolio_logs?.length || 0} entries
            </span>
          </div>
          <PortfolioLogsTable logs={result.portfolio_logs} />
        </div>
      )}
    </div>
  )
}

export default ResultsPage
