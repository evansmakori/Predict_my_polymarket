import React, { useState, useEffect } from 'react';
import { MessageSquare, ThumbsUp, ThumbsDown, Minus, AlertCircle, TrendingUp } from 'lucide-react';
import { getSentimentAnalysis } from '../services/api';

const AISentimentAnalysis = ({ marketId }) => {
  const [sentiment, setSentiment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (marketId) {
      loadSentiment();
    }
  }, [marketId]);

  const loadSentiment = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getSentimentAnalysis(marketId);
      setSentiment(data.sentiment_analysis);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  if (error) return null;
  if (!sentiment) return null;

  const getSentimentConfig = () => {
    switch (sentiment.sentiment) {
      case 'POSITIVE':
        return {
          icon: ThumbsUp,
          color: 'text-green-600',
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200'
        };
      case 'NEGATIVE':
        return {
          icon: ThumbsDown,
          color: 'text-red-600',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200'
        };
      default:
        return {
          icon: Minus,
          color: 'text-gray-600',
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200'
        };
    }
  };

  const config = getSentimentConfig();
  const SentimentIcon = config.icon;

  return (
    <div className={`${config.bgColor} p-6 rounded-lg shadow border ${config.borderColor}`}>
      <div className="flex items-center space-x-2 mb-4">
        <MessageSquare className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-semibold text-gray-800">AI Sentiment Analysis</h3>
      </div>

      <div className="space-y-4">
        {/* Sentiment Score */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <SentimentIcon className={`w-6 h-6 ${config.color}`} />
            <div>
              <p className="text-sm text-gray-600">Sentiment</p>
              <p className={`text-xl font-bold ${config.color}`}>
                {sentiment.sentiment}
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600">Score</p>
            <p className="text-xl font-bold text-gray-800">
              {sentiment.sentiment_score.toFixed(2)}
            </p>
          </div>
        </div>

        {/* Confidence */}
        <div>
          <div className="flex justify-between items-center mb-1">
            <p className="text-sm text-gray-600">Confidence</p>
            <p className="text-sm font-semibold">{(sentiment.confidence * 100).toFixed(0)}%</p>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="h-2 rounded-full bg-blue-500"
              style={{ width: `${sentiment.confidence * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Topics */}
        {sentiment.key_topics && sentiment.key_topics.length > 0 && (
          <div>
            <p className="text-sm text-gray-600 mb-2">Topics</p>
            <div className="flex flex-wrap gap-2">
              {sentiment.key_topics.map((topic, idx) => (
                <span
                  key={idx}
                  className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full"
                >
                  {topic}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Uncertainty */}
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Uncertainty Level</span>
          <span className={`font-semibold ${
            sentiment.uncertainty_level === 'high' ? 'text-red-600' :
            sentiment.uncertainty_level === 'medium' ? 'text-yellow-600' :
            'text-green-600'
          }`}>
            {sentiment.uncertainty_level?.toUpperCase()}
          </span>
        </div>

        {/* Metadata */}
        <div className="grid grid-cols-2 gap-2 text-xs text-gray-600 pt-3 border-t">
          <div>
            <p className="font-medium">Word Count</p>
            <p>{sentiment.word_count}</p>
          </div>
          <div>
            <p className="font-medium">Model Type</p>
            <p>{sentiment.model_type}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AISentimentAnalysis;
