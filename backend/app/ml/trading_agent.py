"""
AI Trading Signals Agent.

Generates intelligent trading recommendations by combining:
- Price predictions from neural networks
- Sentiment analysis
- Anomaly detection
- Risk assessment
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np

from .price_predictor import PricePredictor
from .sentiment_analyzer import SentimentAnalyzer
from .anomaly_detector import AnomalyDetector

logger = logging.getLogger(__name__)


class TradingAgent:
    """
    AI-powered trading signals agent.
    
    Combines multiple AI models to generate trading recommendations:
    1. Price prediction (neural network)
    2. Sentiment analysis (NLP)
    3. Anomaly detection (Isolation Forest)
    4. Risk assessment (multi-factor analysis)
    """
    
    def __init__(self):
        """Initialize the trading agent with all AI models."""
        self.price_predictor = PricePredictor()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.anomaly_detector = AnomalyDetector()
        
        logger.info("Trading Agent initialized with all AI models")
    
    def generate_signal(self, market_data: Dict, historical_data: Optional[List[Dict]] = None) -> Dict:
        """
        Generate comprehensive trading signal for a market.
        
        Args:
            market_data: Current market data including price, volume, etc.
            historical_data: Historical market data for context
        
        Returns:
            Dictionary with trading recommendation and analysis
        """
        try:
            # 1. Price Prediction
            price_prediction = self.price_predictor.predict(market_data)
            
            # 2. Sentiment Analysis
            market_text = market_data.get('question', '') + ' ' + market_data.get('description', '')
            sentiment = self.sentiment_analyzer.analyze(market_text, market_data)
            
            # 3. Anomaly Detection
            anomaly = self.anomaly_detector.detect(market_data, historical_data)
            
            # 4. Generate Trading Signal
            signal = self._generate_trading_signal(
                market_data,
                price_prediction,
                sentiment,
                anomaly
            )
            
            # 5. Calculate Confidence and Risk
            confidence = self._calculate_signal_confidence(
                price_prediction,
                sentiment,
                anomaly,
                market_data
            )
            
            risk_level = self._assess_risk(market_data, anomaly, sentiment)
            
            # 6. Generate Recommendation
            recommendation = self._generate_recommendation(
                signal,
                confidence,
                risk_level,
                market_data
            )
            
            return {
                'signal': signal,
                'confidence': confidence,
                'risk_level': risk_level,
                'recommendation': recommendation,
                'price_prediction': price_prediction,
                'sentiment_analysis': sentiment,
                'anomaly_detection': anomaly,
                'reasoning': self._explain_reasoning(
                    signal, price_prediction, sentiment, anomaly, market_data
                ),
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error generating trading signal: {e}")
            return self._fallback_signal(market_data)
    
    def _generate_trading_signal(
        self,
        market_data: Dict,
        price_prediction: Dict,
        sentiment: Dict,
        anomaly: Dict
    ) -> str:
        """
        Generate trading signal: BUY, SELL, or HOLD.
        
        Decision logic:
        - BUY: Predicted price increase + positive sentiment + no major anomalies
        - SELL: Predicted price decrease + negative sentiment + possible anomalies
        - HOLD: Mixed signals or high uncertainty
        """
        score = 0.0
        
        # Price prediction contribution (40%)
        predicted_change = price_prediction.get('predicted_change', 0)
        if predicted_change > 0.05:
            score += 0.4
        elif predicted_change < -0.05:
            score -= 0.4
        else:
            score += predicted_change * 4  # Scale small changes
        
        # Sentiment contribution (30%)
        sentiment_score = sentiment.get('sentiment_score', 0.5)
        if sentiment.get('sentiment') == 'POSITIVE':
            score += (sentiment_score - 0.5) * 0.6
        elif sentiment.get('sentiment') == 'NEGATIVE':
            score -= (0.5 - sentiment_score) * 0.6
        
        # Anomaly contribution (30%)
        if anomaly.get('is_anomaly'):
            anomaly_score = anomaly.get('anomaly_score', 0)
            if anomaly_score > 0.7:
                score -= 0.3  # High anomaly = risk, lean toward SELL/HOLD
            else:
                score -= anomaly_score * 0.3
        
        # Current market position adjustment
        current_prob = market_data.get('probability', 0.5)
        if current_prob > 0.9:
            score -= 0.2  # Already very high, risky to buy
        elif current_prob < 0.1:
            score += 0.2  # Very low, might be opportunity
        
        # Generate signal based on score
        if score > 0.3:
            return 'BUY'
        elif score < -0.3:
            return 'SELL'
        else:
            return 'HOLD'
    
    def _calculate_signal_confidence(
        self,
        price_prediction: Dict,
        sentiment: Dict,
        anomaly: Dict,
        market_data: Dict
    ) -> float:
        """Calculate confidence in the trading signal."""
        confidence_factors = []
        
        # Price prediction confidence
        pred_confidence = price_prediction.get('confidence', 0.5)
        confidence_factors.append(pred_confidence)
        
        # Sentiment confidence
        sent_confidence = sentiment.get('confidence', 0.5)
        confidence_factors.append(sent_confidence)
        
        # Market data quality
        volume = market_data.get('volume_24h', 0)
        liquidity = market_data.get('liquidity', 0)
        
        data_quality = 0.5
        if volume > 10000:
            data_quality += 0.2
        if liquidity > 50000:
            data_quality += 0.2
        if market_data.get('num_trades', 0) > 100:
            data_quality += 0.1
        
        confidence_factors.append(min(data_quality, 1.0))
        
        # Reduce confidence if anomaly detected
        if anomaly.get('is_anomaly'):
            anomaly_penalty = anomaly.get('anomaly_score', 0) * 0.3
            confidence_factors.append(1.0 - anomaly_penalty)
        
        # Average confidence
        overall_confidence = np.mean(confidence_factors)
        
        return float(np.clip(overall_confidence, 0.1, 0.95))
    
    def _assess_risk(self, market_data: Dict, anomaly: Dict, sentiment: Dict) -> str:
        """
        Assess risk level: LOW, MEDIUM, HIGH, CRITICAL.
        """
        risk_score = 0
        
        # Liquidity risk
        liquidity = market_data.get('liquidity', 0)
        if liquidity < 5000:
            risk_score += 3
        elif liquidity < 20000:
            risk_score += 2
        elif liquidity < 50000:
            risk_score += 1
        
        # Spread risk
        spread = market_data.get('spread', 0.1)
        if spread > 0.15:
            risk_score += 3
        elif spread > 0.1:
            risk_score += 2
        elif spread > 0.05:
            risk_score += 1
        
        # Anomaly risk
        if anomaly.get('is_anomaly'):
            severity = anomaly.get('severity', 'low')
            if severity == 'critical':
                risk_score += 4
            elif severity == 'high':
                risk_score += 3
            elif severity == 'medium':
                risk_score += 2
            else:
                risk_score += 1
        
        # Volume risk (too low or suspiciously high)
        volume = market_data.get('volume_24h', 0)
        if volume < 1000:
            risk_score += 2
        
        # Uncertainty risk
        uncertainty = sentiment.get('uncertainty_level', 'medium')
        if uncertainty == 'high':
            risk_score += 2
        elif uncertainty == 'medium':
            risk_score += 1
        
        # Classify risk level
        if risk_score >= 8:
            return 'CRITICAL'
        elif risk_score >= 5:
            return 'HIGH'
        elif risk_score >= 3:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_recommendation(
        self,
        signal: str,
        confidence: float,
        risk_level: str,
        market_data: Dict
    ) -> Dict:
        """Generate detailed trading recommendation."""
        current_prob = market_data.get('probability', 0.5)
        
        # Base recommendation
        recommendation = {
            'action': signal,
            'confidence_level': self._confidence_to_level(confidence),
            'risk_level': risk_level,
            'suggested_position_size': self._calculate_position_size(confidence, risk_level),
            'entry_price': None,
            'stop_loss': None,
            'take_profit': None,
            'warnings': []
        }
        
        # Calculate entry points and targets
        if signal == 'BUY':
            recommendation['entry_price'] = current_prob
            recommendation['stop_loss'] = max(current_prob - 0.15, 0.01)
            recommendation['take_profit'] = min(current_prob + 0.20, 0.99)
        elif signal == 'SELL':
            recommendation['entry_price'] = current_prob
            recommendation['stop_loss'] = min(current_prob + 0.15, 0.99)
            recommendation['take_profit'] = max(current_prob - 0.20, 0.01)
        
        # Add warnings
        if risk_level in ['HIGH', 'CRITICAL']:
            recommendation['warnings'].append(
                f"{risk_level} risk detected. Consider reducing position size or avoiding this market."
            )
        
        if market_data.get('liquidity', 0) < 10000:
            recommendation['warnings'].append(
                "Low liquidity may result in slippage and difficulty exiting positions."
            )
        
        if market_data.get('spread', 0) > 0.1:
            recommendation['warnings'].append(
                "Wide spread detected. Entry and exit costs may be high."
            )
        
        if confidence < 0.5:
            recommendation['warnings'].append(
                "Low confidence signal. Consider waiting for better opportunities."
            )
        
        return recommendation
    
    def _confidence_to_level(self, confidence: float) -> str:
        """Convert confidence score to categorical level."""
        if confidence >= 0.8:
            return 'VERY_HIGH'
        elif confidence >= 0.65:
            return 'HIGH'
        elif confidence >= 0.5:
            return 'MEDIUM'
        elif confidence >= 0.35:
            return 'LOW'
        else:
            return 'VERY_LOW'
    
    def _calculate_position_size(self, confidence: float, risk_level: str) -> str:
        """
        Calculate suggested position size as percentage of portfolio.
        
        Returns a recommendation like "SMALL (1-3%)", "MEDIUM (3-7%)", etc.
        """
        # Start with confidence-based sizing
        if confidence >= 0.8:
            base_size = 'LARGE'
        elif confidence >= 0.65:
            base_size = 'MEDIUM'
        elif confidence >= 0.5:
            base_size = 'SMALL'
        else:
            base_size = 'VERY_SMALL'
        
        # Adjust for risk
        risk_penalties = {
            'LOW': 0,
            'MEDIUM': 1,
            'HIGH': 2,
            'CRITICAL': 3
        }
        
        penalty = risk_penalties.get(risk_level, 1)
        
        # Size mapping
        size_map = {
            'LARGE': ['MEDIUM (5-10%)', 'SMALL (3-5%)', 'VERY_SMALL (1-3%)', 'MINIMAL (<1%)'],
            'MEDIUM': ['SMALL (3-5%)', 'VERY_SMALL (1-3%)', 'MINIMAL (<1%)', 'AVOID'],
            'SMALL': ['VERY_SMALL (1-3%)', 'MINIMAL (<1%)', 'AVOID', 'AVOID'],
            'VERY_SMALL': ['MINIMAL (<1%)', 'AVOID', 'AVOID', 'AVOID']
        }
        
        return size_map[base_size][min(penalty, 3)]
    
    def _explain_reasoning(
        self,
        signal: str,
        price_prediction: Dict,
        sentiment: Dict,
        anomaly: Dict,
        market_data: Dict
    ) -> List[str]:
        """Generate human-readable explanation of the trading signal."""
        reasoning = []
        
        # Price prediction reasoning
        predicted_change = price_prediction.get('predicted_change', 0)
        if abs(predicted_change) > 0.05:
            direction = "increase" if predicted_change > 0 else "decrease"
            reasoning.append(
                f"ML model predicts {abs(predicted_change)*100:.1f}% price {direction} "
                f"(confidence: {price_prediction.get('confidence', 0)*100:.0f}%)"
            )
        
        # Sentiment reasoning
        sent = sentiment.get('sentiment', 'NEUTRAL')
        if sent != 'NEUTRAL':
            reasoning.append(
                f"Market sentiment is {sent.lower()} "
                f"(score: {sentiment.get('sentiment_score', 0.5):.2f})"
            )
        
        # Anomaly reasoning
        if anomaly.get('is_anomaly'):
            types = ', '.join(anomaly.get('anomaly_types', []))
            reasoning.append(
                f"Anomaly detected: {types} "
                f"(severity: {anomaly.get('severity', 'unknown')})"
            )
        
        # Market conditions
        liquidity = market_data.get('liquidity', 0)
        volume = market_data.get('volume_24h', 0)
        
        if liquidity > 100000 and volume > 50000:
            reasoning.append("Strong market fundamentals with high liquidity and volume")
        elif liquidity < 10000 or volume < 1000:
            reasoning.append("Weak market fundamentals - low liquidity or volume")
        
        # Current price position
        prob = market_data.get('probability', 0.5)
        if prob > 0.9:
            reasoning.append("Market already priced very high - limited upside potential")
        elif prob < 0.1:
            reasoning.append("Market priced very low - potential for significant gains")
        
        return reasoning
    
    def _fallback_signal(self, market_data: Dict) -> Dict:
        """Generate fallback signal when AI models fail."""
        return {
            'signal': 'HOLD',
            'confidence': 0.3,
            'risk_level': 'HIGH',
            'recommendation': {
                'action': 'HOLD',
                'confidence_level': 'LOW',
                'risk_level': 'HIGH',
                'suggested_position_size': 'AVOID',
                'warnings': ['AI models unavailable. Recommendation based on limited data.']
            },
            'reasoning': ['Unable to generate AI-powered analysis. Suggesting caution.'],
            'timestamp': datetime.now().isoformat()
        }
    
    def batch_generate_signals(self, markets_data: List[Dict]) -> List[Dict]:
        """Generate trading signals for multiple markets."""
        signals = []
        
        for market_data in markets_data:
            signal = self.generate_signal(market_data)
            signal['market_id'] = market_data.get('id', 'unknown')
            signal['market_question'] = market_data.get('question', 'Unknown')
            signals.append(signal)
        
        return signals
    
    def get_top_opportunities(self, markets_data: List[Dict], limit: int = 10) -> List[Dict]:
        """
        Find top trading opportunities from a list of markets.
        
        Ranks by confidence and filters by acceptable risk levels.
        """
        signals = self.batch_generate_signals(markets_data)
        
        # Filter out critical risk and very low confidence
        filtered = [
            s for s in signals
            if s['risk_level'] != 'CRITICAL' and s['confidence'] >= 0.4
        ]
        
        # Sort by confidence (descending)
        sorted_signals = sorted(filtered, key=lambda x: x['confidence'], reverse=True)
        
        return sorted_signals[:limit]
    
    def get_agent_status(self) -> Dict:
        """Get status of all AI models in the agent."""
        return {
            'price_predictor': self.price_predictor.get_model_info(),
            'sentiment_analyzer': self.sentiment_analyzer.get_model_info(),
            'anomaly_detector': self.anomaly_detector.get_statistics(),
            'agent_ready': True
        }
