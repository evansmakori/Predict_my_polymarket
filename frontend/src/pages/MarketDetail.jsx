import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, Loader2, TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react'
import { marketsApi, createWebSocket } from '../services/api'
import { formatPercent, formatDateTime, getSignalColor } from '../utils/formatters'
import StatsGrid from '../components/StatsGrid'
import PriceChart from '../components/PriceChart'
import OrderbookView from '../components/OrderbookView'

function MarketDetail() {
  const { marketId } = useParams()
  const [liveData, setLiveData] = useState(null)

  // Fetch market data
  const { data: market, isLoading, error } = useQuery({
    queryKey: ['market', marketId],
    queryFn: () => marketsApi.getMarket(marketId),
  })

  // Fetch price history
  const { data: history } = useQuery({
    queryKey: ['market-history', marketId],
    queryFn: () => marketsApi.getMarketHistory(marketId, '1w', 1000),
    enabled: !!market,
  })

  // Fetch orderbook
  const { data: orderbook } = useQuery({
    queryKey: ['market-orderbook', marketId],
    queryFn: () => marketsApi.getMarketOrderbook(marketId),
    enabled: !!market,
  })

  // WebSocket for live updates
  useEffect(() => {
    if (!marketId) return

    const ws = createWebSocket(marketId)

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data)
      if (message.type === 'initial' || message.type === 'update') {
        setLiveData(message.data)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    return () => {
      ws.close()
    }
  }, [marketId])

  // Use live data if available, otherwise use fetched data
  const displayData = liveData || market

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 text-primary-600 animate-spin" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="card bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
        <p className="text-red-800 dark:text-red-300">
          Error loading market: {error.message}
        </p>
      </div>
    )
  }

  if (!displayData) {
    return (
      <div className="card text-center py-12">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
          Market not found
        </h3>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <Link to="/" className="inline-flex items-center text-primary-600 hover:text-primary-700">
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Dashboard
      </Link>

      {/* Header */}
      <div className="card">
        <div className="space-y-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                {displayData.title}
              </h1>
              {displayData.category && (
                <span className="inline-block px-3 py-1 text-sm rounded-full bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                  {displayData.category}
                </span>
              )}
            </div>

            {/* Live Indicator */}
            {liveData && (
              <div className="flex items-center space-x-2 px-3 py-1 bg-green-100 dark:bg-green-900 rounded-full">
                <div className="w-2 h-2 bg-green-600 rounded-full animate-pulse"></div>
                <span className="text-xs font-medium text-green-800 dark:text-green-300">LIVE</span>
              </div>
            )}
          </div>

          {/* Prices */}
          <div className="grid grid-cols-2 gap-6">
            <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">YES</p>
              <p className="text-3xl font-bold text-green-600 dark:text-green-400">
                {formatPercent(displayData.ui_yes_price || displayData.yes_price)}
              </p>
              {displayData.best_bid_yes && displayData.best_ask_yes && (
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Bid: {formatPercent(displayData.best_bid_yes)} / Ask: {formatPercent(displayData.best_ask_yes)}
                </p>
              )}
            </div>
            <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">NO</p>
              <p className="text-3xl font-bold text-red-600 dark:text-red-400">
                {formatPercent(displayData.ui_no_price || displayData.no_price)}
              </p>
              {displayData.best_bid_no && displayData.best_ask_no && (
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Bid: {formatPercent(displayData.best_bid_no)} / Ask: {formatPercent(displayData.best_ask_no)}
                </p>
              )}
            </div>
          </div>

          {/* Trading Signal & Alerts */}
          <div className="flex flex-wrap gap-3">
            {displayData.trade_signal && (
              <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg ${getSignalColor(displayData.trade_signal)}`}>
                {displayData.trade_signal === 'long' && <TrendingUp className="w-4 h-4" />}
                {displayData.trade_signal === 'short' && <TrendingDown className="w-4 h-4" />}
                <span className="font-medium capitalize">Signal: {displayData.trade_signal}</span>
              </div>
            )}

            {displayData.late_overconfidence && (
              <div className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-300">
                <AlertTriangle className="w-4 h-4" />
                <span className="font-medium">Late Overconfidence</span>
              </div>
            )}

            {displayData.overreaction_flag && (
              <div className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-300">
                <AlertTriangle className="w-4 h-4" />
                <span className="font-medium">Overreaction Detected</span>
              </div>
            )}
          </div>

          {/* Timestamps */}
          <div className="text-xs text-gray-500 dark:text-gray-400 border-t border-gray-200 dark:border-gray-700 pt-3">
            Last updated: {formatDateTime(displayData.snapshot_ts)}
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <StatsGrid market={displayData} />

      {/* Analytics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Fair Value & Expected Value */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Valuation</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-400">Fair Value</span>
              <span className="font-semibold text-gray-900 dark:text-white">
                {formatPercent(displayData.fair_value)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-400">Expected Value</span>
              <span className={`font-semibold ${displayData.expected_value > 0 ? 'text-green-600' : 'text-red-600'}`}>
                {displayData.expected_value !== null ? `${(displayData.expected_value * 10000).toFixed(0)} bps` : 'N/A'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-400">Kelly Fraction</span>
              <span className="font-semibold text-gray-900 dark:text-white">
                {displayData.kelly_fraction !== null ? formatPercent(displayData.kelly_fraction) : 'N/A'}
              </span>
            </div>
          </div>
        </div>

        {/* Risk Metrics */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Risk Metrics</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-400">Volatility (1w)</span>
              <span className="font-semibold text-gray-900 dark:text-white">
                {displayData.volatility_1w !== null ? formatPercent(displayData.volatility_1w) : 'N/A'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-400">Orderbook Imbalance</span>
              <span className="font-semibold text-gray-900 dark:text-white">
                {displayData.orderbook_imbalance !== null ? formatPercent(displayData.orderbook_imbalance) : 'N/A'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-400">Slippage ($1k)</span>
              <span className="font-semibold text-gray-900 dark:text-white">
                {displayData.slippage_notional_1k !== null ? `${displayData.slippage_notional_1k.toFixed(0)} bps` : 'N/A'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Price Chart */}
      {history && <PriceChart data={history} />}

      {/* Orderbook */}
      {orderbook && <OrderbookView orderbook={orderbook} />}
    </div>
  )
}

export default MarketDetail
