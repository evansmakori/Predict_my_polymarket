import React, { useState, useEffect } from 'react';
import { ShoppingCart, TrendingDown, Pause, AlertTriangle, CheckCircle, Zap, Target } from 'lucide-react';
import { getTradingSignal } from '../services/api';

const AITradingSignal = ({ marketId }) => {
  const [signal, setSignal] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (marketId) {
      loadSignal();
    }
  }, [marketId]);

  const loadSignal = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getTradingSignal(marketId);
      setSignal(data.trading_signal);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-lg border-2 border-gray-200">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/2"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 p-6 rounded-lg shadow border-2 border-red-200">
        <p className="text-red-600">Error loading trading signal: {error}</p>
      </div>
    );
  }

  if (!signal) return null;

  const signalType = signal.signal;
  const recommendation = signal.recommendation || {};
  const riskLevel = signal.risk_level || 'UNKNOWN';

  const getSignalConfig = () => {
    switch (signalType) {
      case 'BUY':
        return {
          icon: ShoppingCart,
          color: 'green',
          bgColor: 'bg-green-50',
          borderColor: 'border-green-500',
          textColor: 'text-green-700',
          label: 'BUY Signal'
        };
      case 'SELL':
        return {
          icon: TrendingDown,
          color: 'red',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-500',
          textColor: 'text-red-700',
          label: 'SELL Signal'
        };
      case 'HOLD':
      default:
        return {
          icon: Pause,
          color: 'yellow',
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-500',
          textColor: 'text-yellow-700',
          label: 'HOLD Signal'
        };
    }
  };

  const getRiskColor = () => {
    switch (riskLevel) {
      case 'CRITICAL':
        return 'text-red-700 bg-red-100';
      case 'HIGH':
        return 'text-orange-700 bg-orange-100';
      case 'MEDIUM':
        return 'text-yellow-700 bg-yellow-100';
      case 'LOW':
        return 'text-green-700 bg-green-100';
      default:
        return 'text-gray-700 bg-gray-100';
    }
  };

  const config = getSignalConfig();
  const SignalIcon = config.icon;

  return (
    <div className={`${config.bgColor} p-6 rounded-lg shadow-lg border-2 ${config.borderColor}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-full bg-${config.color}-100`}>
            <SignalIcon className={`w-6 h-6 ${config.textColor}`} />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-800">{config.label}</h3>
            <p className="text-sm text-gray-600">AI-Generated Recommendation</p>
          </div>
        </div>
        <Zap className="w-5 h-5 text-purple-600" title="AI Powered" />
      </div>

      {/* Confidence & Risk */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-xs text-gray-600 mb-1">Confidence</p>
          <div className="flex items-center space-x-2">
            <div className="flex-1 bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full bg-${config.color}-500`}
                style={{ width: `${(signal.confidence || 0) * 100}%` }}
              ></div>
            </div>
            <span className="text-sm font-semibold">{((signal.confidence || 0) * 100).toFixed(0)}%</span>
          </div>
        </div>
        <div>
          <p className="text-xs text-gray-600 mb-1">Risk Level</p>
          <span className={`text-sm font-semibold px-3 py-1 rounded-full ${getRiskColor()}`}>
            {riskLevel}
          </span>
        </div>
      </div>

      {/* Recommendation Details */}
      {recommendation && (
        <div className="bg-white/70 p-4 rounded-lg space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Position Size</span>
            <span className="text-sm font-semibold text-gray-800">
              {recommendation.suggested_position_size || 'N/A'}
            </span>
          </div>

          {recommendation.entry_price !== null && (
            <>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Entry Price</span>
                <span className="text-sm font-semibold text-gray-800">
                  {(recommendation.entry_price * 100).toFixed(1)}%
                </span>
              </div>
              
              {recommendation.stop_loss !== null && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Stop Loss</span>
                  <span className="text-sm font-semibold text-red-600">
                    {(recommendation.stop_loss * 100).toFixed(1)}%
                  </span>
                </div>
              )}
              
              {recommendation.take_profit !== null && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Take Profit</span>
                  <span className="text-sm font-semibold text-green-600">
                    {(recommendation.take_profit * 100).toFixed(1)}%
                  </span>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* Reasoning */}
      {signal.reasoning && signal.reasoning.length > 0 && (
        <div className="mt-4">
          <p className="text-sm font-semibold text-gray-700 mb-2">AI Analysis:</p>
          <ul className="space-y-1">
            {signal.reasoning.map((reason, idx) => (
              <li key={idx} className="flex items-start space-x-2 text-xs text-gray-600">
                <CheckCircle className="w-3 h-3 mt-0.5 text-blue-500 flex-shrink-0" />
                <span>{reason}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Warnings */}
      {recommendation.warnings && recommendation.warnings.length > 0 && (
        <div className="mt-4 bg-yellow-50 p-3 rounded border border-yellow-200">
          <div className="flex items-center space-x-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-yellow-600" />
            <p className="text-sm font-semibold text-yellow-800">Warnings</p>
          </div>
          <ul className="space-y-1">
            {recommendation.warnings.map((warning, idx) => (
              <li key={idx} className="text-xs text-yellow-700">• {warning}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Footer */}
      <div className="mt-4 pt-4 border-t border-gray-300 flex items-center justify-between text-xs text-gray-500">
        <span>Generated: {new Date(signal.timestamp).toLocaleString()}</span>
        <div className="flex items-center space-x-1">
          <Target className="w-3 h-3" />
          <span>DigitalOcean AI</span>
        </div>
      </div>
    </div>
  );
};

export default AITradingSignal;
