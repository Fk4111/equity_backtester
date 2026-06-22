// Table showing stock-level portfolio logs per rebalance period
function PortfolioLogsTable({ logs }) {
  if (!logs || logs.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        No portfolio logs available
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-800">
            <th className="text-left text-gray-400 py-3 px-4">Symbol</th>
            <th className="text-left text-gray-400 py-3 px-4">Rebalance Date</th>
            <th className="text-right text-gray-400 py-3 px-4">Weight (%)</th>
            <th className="text-right text-gray-400 py-3 px-4">Return (%)</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log, index) => (
            <tr
              key={index}
              className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors"
            >
              <td className="py-2.5 px-4 font-medium text-white">{log.symbol}</td>
              <td className="py-2.5 px-4 text-gray-400">
                {log.rebalance_date
                  ? new Date(log.rebalance_date).toLocaleDateString('en-IN')
                  : '-'}
              </td>
              <td className="py-2.5 px-4 text-right text-gray-300">
                {log.weight?.toFixed(2)}%
              </td>
              <td
                className={`py-2.5 px-4 text-right font-medium ${
                  log.return_percent >= 0 ? 'text-green-400' : 'text-red-400'
                }`}
              >
                {log.return_percent >= 0 ? '+' : ''}{log.return_percent?.toFixed(2)}%
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default PortfolioLogsTable
