import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import HomePage from './pages/HomePage'
import BacktestPage from './pages/BacktestPage'
import ResultsPage from './pages/ResultsPage'
import StocksPage from './pages/StocksPage'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-950">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/backtest" element={<BacktestPage />} />
            <Route path="/results" element={<ResultsPage />} />
            <Route path="/stocks" element={<StocksPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
