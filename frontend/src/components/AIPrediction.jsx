import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Minus, Brain, Zap } from 'lucide-react';
import { getPricePrediction } from '../services/api';

const AIPrediction = ({ marketId }) => {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (marketId) {
      loadPrediction();
    }
  }, [marketId]);

  const loadPrediction = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getPricePrediction(marketId);
      setPrediction(data.prediction);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-gradient-to-br from-purple-50 to-blue-50 p-6 rounded-lg shadow">
        <div className="flex items-center space-x-2 mb-4">
          <Brain className="w-5 h-5 text-purple-600 animate-pulse" />
          <h3 className="text-lg font-semibold text-gray-800">AI Price Prediction</h3>
        </div>
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 p-6 rounded-lg shadow">
        <p className="text-red-600">Error loading prediction: {error}</p>
      </div>
    );
  }

  if (!prediction) return null;

  const predictedChange = prediction.predicted_change || 0;
  const confidence = prediction.confidence || 0;
  const isIncrease = predictedChange > 0;
  const isSignificant = Math.abs(predictedChange) > 0.05;

  const getSignalColor = () => {
    if (!isSignificant) return 'text-gray-600';
    return isIncrease ? 'text-green-600' : 'text-red-600';
  };

  const getSignalIcon = () => {
    if (!isSignificant) return <Minus className="w-6 h-6" />;
    return isIncrease ? <TrendingUp className="w-6 h-6" /> : <TrendingDown className="w-6 h-6" />;
  };

  return (
    <div className="bg-gradient-to-br from-purple-50 to-blue-50 p-6 rounded-lg shadow-lg border border-purple-200">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Brain className="w-5 h-5 text-purple-600" />
          <h3 className="text-lg font-semibold text-gray-800">AI Price Prediction</h3>
          <Zap className="w-4 h-4 text-yellow-500" title="Powered by DigitalOcean GPU" />
        </div>
        <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">
          {prediction.model_type || 'Neural Network'}
        </span>
      </div>

      <div className="space-y-4">
        {/* Prediction Direction */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={getSignalColor()}>
              {getSignalIcon()}
            </div>
            <div>
              <p className="text-sm text-gray-600">Predicted Change</p>
              <p className={`text-2xl font-bold ${getSignalColor()}`}>
                {isIncrease ? '+' : ''}{(predictedChange * 100).toFixed(2)}%
              </p>
            </div>
          </div>
          
          <div className="text-right">
            <p className="text-sm text-gray-600">New Probability</p>
            <p className="text-2xl font-bold text-gray-800">
              {(prediction.predicted_probability * 100).toFixed(1)}%
            </p>
          </div>
        </div>

        {/* Confidence Meter */}
        <div>
          <div className="flex justify-between items-center mb-1">
            <p className="text-sm text-gray-600">Model Confidence</p>
            <p className="text-sm font-semibold text-gray-800">
              {(confidence * 100).toFixed(0)}%
            </p>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${
                confidence > 0.7 ? 'bg-green-500' :
                confidence > 0.5 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${confidence * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Metadata */}
        <div className="grid grid-cols-2 gap-2 text-xs text-gray-600 pt-3 border-t border-purple-200">
          <div>
            <p className="font-medium">Time Horizon</p>
            <p>{prediction.prediction_horizon || '24h'}</p>
          </div>
          <div>
            <p className="font-medium">Features Used</p>
            <p>{prediction.features_used || 'N/A'}</p>
          </div>
        </div>

        {/* Current vs Predicted */}
        <div className="bg-white/50 p-3 rounded text-xs space-y-1">
          <div className="flex justify-between">
            <span className="text-gray-600">Current Probability:</span>
            <span className="font-semibold">{(prediction.current_probability * 100).toFixed(1)}%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Predicted Probability:</span>
            <span className="font-semibold">{(prediction.predicted_probability * 100).toFixed(1)}%</span>
          </div>
        </div>

        {/* GPU Badge */}
        <div className="flex items-center justify-center space-x-2 text-xs text-purple-600 bg-purple-100 py-2 rounded">
          <Zap className="w-3 h-3" />
          <span>Powered by DigitalOcean Gradient™ AI</span>
        </div>
      </div>
    </div>
  );
};

export default AIPrediction;
