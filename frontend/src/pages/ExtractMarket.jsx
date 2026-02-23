import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Download, Loader2, CheckCircle, XCircle } from 'lucide-react'
import { marketsApi } from '../services/api'

function ExtractMarket() {
  const [url, setUrl] = useState('')
  const [depth, setDepth] = useState(10)
  const [fidelity, setFidelity] = useState(60)
  const [baseRate, setBaseRate] = useState(0.50)

  const mutation = useMutation({
    mutationFn: (data) => marketsApi.extractMarket(data),
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    mutation.mutate({
      url,
      depth,
      intervals: ['1w', '1m'],
      fidelity_min: fidelity,
      base_rate: baseRate,
    })
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Extract Market Data
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Fetch and analyze data from Polymarket URLs
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="card space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Polymarket URL *
          </label>
          <input
            type="url"
            required
            placeholder="https://polymarket.com/event/..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="input w-full"
          />
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
            Enter a Polymarket event or market URL
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Orderbook Depth
            </label>
            <input
              type="number"
              min="1"
              max="50"
              value={depth}
              onChange={(e) => setDepth(parseInt(e.target.value))}
              className="input w-full"
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Levels per side (1-50)
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Fidelity (minutes)
            </label>
            <input
              type="number"
              min="1"
              value={fidelity}
              onChange={(e) => setFidelity(parseInt(e.target.value))}
              className="input w-full"
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Price history granularity
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Base Rate
            </label>
            <input
              type="number"
              min="0"
              max="1"
              step="0.01"
              value={baseRate}
              onChange={(e) => setBaseRate(parseFloat(e.target.value))}
              className="input w-full"
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Prior probability (0-1)
            </p>
          </div>
        </div>

        <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            This will fetch orderbook, price history, and compute analytics
          </p>
          <button
            type="submit"
            disabled={mutation.isPending || !url}
            className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {mutation.isPending ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Extracting...</span>
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                <span>Extract Data</span>
              </>
            )}
          </button>
        </div>
      </form>

      {/* Success Result */}
      {mutation.isSuccess && (
        <div className="card bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
          <div className="flex items-start space-x-3">
            <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold text-green-900 dark:text-green-100 mb-2">
                Successfully extracted {mutation.data.markets_processed} market(s)!
              </h3>
              <p className="text-sm text-green-800 dark:text-green-300 mb-3">
                {mutation.data.message}
              </p>
              {mutation.data.market_ids && mutation.data.market_ids.length > 0 && (
                <div className="space-y-2">
                  <p className="text-sm font-medium text-green-900 dark:text-green-100">
                    View markets:
                  </p>
                  <div className="space-y-1">
                    {mutation.data.market_ids.map((id) => (
                      <Link
                        key={id}
                        to={`/market/${id}`}
                        className="block text-sm text-green-700 dark:text-green-300 hover:underline"
                      >
                        Market ID: {id}
                      </Link>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Error Result */}
      {mutation.isError && (
        <div className="card bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
          <div className="flex items-start space-x-3">
            <XCircle className="w-6 h-6 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-red-900 dark:text-red-100 mb-1">
                Extraction failed
              </h3>
              <p className="text-sm text-red-800 dark:text-red-300">
                {mutation.error.message}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="card bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
        <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-3">
          How to use
        </h3>
        <ol className="space-y-2 text-sm text-blue-800 dark:text-blue-300">
          <li className="flex items-start">
            <span className="font-bold mr-2">1.</span>
            <span>Copy a Polymarket event or market URL (e.g., https://polymarket.com/event/...)</span>
          </li>
          <li className="flex items-start">
            <span className="font-bold mr-2">2.</span>
            <span>Paste the URL in the field above</span>
          </li>
          <li className="flex items-start">
            <span className="font-bold mr-2">3.</span>
            <span>Adjust extraction parameters if needed</span>
          </li>
          <li className="flex items-start">
            <span className="font-bold mr-2">4.</span>
            <span>Click "Extract Data" to fetch and analyze the market(s)</span>
          </li>
          <li className="flex items-start">
            <span className="font-bold mr-2">5.</span>
            <span>View the extracted markets in the dashboard or click the links above</span>
          </li>
        </ol>
      </div>
    </div>
  )
}

export default ExtractMarket
