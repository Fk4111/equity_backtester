// A simple card to display a single performance metric
function MetricCard({ label, value, subtitle, color = 'blue', prefix = '', suffix = '' }) {
  const colorMap = {
    blue: 'text-blue-400',
    green: 'text-green-400',
    red: 'text-red-400',
    yellow: 'text-yellow-400',
    purple: 'text-purple-400',
  }

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <p className="text-gray-400 text-sm mb-1">{label}</p>
      <p className={`text-2xl font-bold ${colorMap[color] || colorMap.blue}`}>
        {prefix}{value}{suffix}
      </p>
      {subtitle && (
        <p className="text-gray-500 text-xs mt-1">{subtitle}</p>
      )}
    </div>
  )
}

export default MetricCard
