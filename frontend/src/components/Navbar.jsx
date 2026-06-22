import { Link, useLocation } from 'react-router-dom'

function Navbar() {
  const location = useLocation()

  const navLinks = [
    { path: '/', label: 'Home' },
    { path: '/backtest', label: 'Run Backtest' },
    { path: '/stocks', label: 'Stocks' },
  ]

  return (
    <nav className="bg-gray-900 border-b border-gray-800 sticky top-0 z-50">
      <div className="container mx-auto px-4 flex items-center justify-between h-16">
        {/* Logo / Brand */}
        <Link to="/" className="flex items-center gap-2">
          <span className="text-2xl">📈</span>
          <span className="text-white font-bold text-lg">
            Equity <span className="text-blue-400">Backtester</span>
          </span>
        </Link>

        {/* Nav links */}
        <div className="flex items-center gap-1">
          {navLinks.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                location.pathname === link.path
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800'
              }`}
            >
              {link.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  )
}

export default Navbar
