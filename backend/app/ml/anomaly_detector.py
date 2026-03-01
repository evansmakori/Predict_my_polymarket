"""
ML-based Anomaly Detection for Market Patterns.

Detects unusual patterns in market behavior including:
- Price anomalies
- Volume spikes
- Liquidity drops
- Trading pattern changes
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta
from collections import deque

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available. Using rule-based anomaly detection.")

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    ML-powered anomaly detection for prediction markets.
    
    Uses Isolation Forest algorithm to detect:
    - Unusual price movements
    - Volume anomalies
    - Liquidity changes
    - Spread abnormalities
    - Trading pattern shifts
    """
    
    def __init__(self, contamination: float = 0.1):
        """
        Initialize anomaly detector.
        
        Args:
            contamination: Expected proportion of outliers (0.0 to 0.5)
        """
        self.contamination = contamination
        self.model = None
        self.scaler = None
        self.historical_data = deque(maxlen=1000)  # Keep last 1000 data points
        
        if SKLEARN_AVAILABLE:
            self.model = IsolationForest(
                contamination=contamination,
                random_state=42,
                n_estimators=100
            )
            self.scaler = StandardScaler()
            logger.info("Anomaly detector initialized with Isolation Forest")
        else:
            logger.warning("Using rule-based anomaly detection")
        
        # Statistical thresholds for rule-based detection
        self.thresholds = {
            'price_change': 0.15,  # 15% change threshold
            'volume_spike': 3.0,   # 3x average volume
            'liquidity_drop': 0.5,  # 50% drop
            'spread_spike': 2.0     # 2x normal spread
        }
    
    def extract_features(self, market_data: Dict) -> np.ndarray:
        """
        Extract features for anomaly detection.
        
        Features:
        - Price level and change
        - Volume (raw and normalized)
        - Liquidity
        - Spread
        - Trade frequency
        - Time-based features
        """
        features = []
        
        # Price features
        price = market_data.get('probability', 0.5)
        features.append(price)
        features.append(abs(price - 0.5))  # Distance from 50%
        
        # Volume features
        volume = market_data.get('volume_24h', 0)
        features.append(np.log1p(volume))
        
        # Liquidity features
        liquidity = market_data.get('liquidity', 0)
        features.append(np.log1p(liquidity))
        
        # Spread features
        spread = market_data.get('spread', 0.1)
        features.append(spread)
        features.append(1 / max(spread, 0.001))
        
        # Volume to liquidity ratio
        vol_liq_ratio = volume / max(liquidity, 1)
        features.append(vol_liq_ratio)
        
        # Trade frequency
        num_trades = market_data.get('num_trades', 0)
        features.append(np.log1p(num_trades))
        
        # Trade size (volume per trade)
        avg_trade_size = volume / max(num_trades, 1)
        features.append(np.log1p(avg_trade_size))
        
        # Volatility
        volatility = market_data.get('volatility', 0)
        features.append(volatility)
        
        return np.array(features, dtype=np.float32)
    
    def detect(self, market_data: Dict, historical_context: Optional[List[Dict]] = None) -> Dict:
        """
        Detect anomalies in market data.
        
        Args:
            market_data: Current market data
            historical_context: Historical data for context
        
        Returns:
            Dictionary with anomaly detection results
        """
        features = self.extract_features(market_data)
        
        # Add to historical data
        self.historical_data.append(features)
        
        # ML-based detection if available and enough data
        if SKLEARN_AVAILABLE and self.model and len(self.historical_data) >= 50:
            ml_result = self._ml_anomaly_detection(features)
        else:
            ml_result = None
        
        # Rule-based detection (always run)
        rule_result = self._rule_based_detection(market_data, historical_context)
        
        # Combine results
        is_anomaly = ml_result['is_anomaly'] if ml_result else rule_result['is_anomaly']
        anomaly_score = ml_result['anomaly_score'] if ml_result else rule_result['anomaly_score']
        
        # Detect specific anomaly types
        anomaly_types = self._detect_anomaly_types(market_data, historical_context)
        
        return {
            'is_anomaly': is_anomaly,
            'anomaly_score': float(anomaly_score),
            'anomaly_types': anomaly_types,
            'severity': self._calculate_severity(anomaly_score, anomaly_types),
            'detection_method': ml_result['method'] if ml_result else 'rule_based',
            'confidence': ml_result['confidence'] if ml_result else rule_result['confidence'],
            'details': {
                'price': market_data.get('probability'),
                'volume_24h': market_data.get('volume_24h'),
                'liquidity': market_data.get('liquidity'),
                'spread': market_data.get('spread')
            }
        }
    
    def _ml_anomaly_detection(self, features: np.ndarray) -> Dict:
        """ML-based anomaly detection using Isolation Forest."""
        try:
            # Fit model on historical data if we have enough samples
            if len(self.historical_data) >= 50:
                X = np.array(list(self.historical_data))
                
                # Fit scaler and model
                X_scaled = self.scaler.fit_transform(X)
                self.model.fit(X_scaled)
                
                # Predict on current features
                features_scaled = self.scaler.transform(features.reshape(1, -1))
                prediction = self.model.predict(features_scaled)[0]
                anomaly_score = -self.model.score_samples(features_scaled)[0]
                
                is_anomaly = prediction == -1
                
                # Normalize score to 0-1 range
                normalized_score = min(max(anomaly_score / 2, 0), 1)
                
                return {
                    'is_anomaly': bool(is_anomaly),
                    'anomaly_score': normalized_score,
                    'method': 'isolation_forest',
                    'confidence': 0.85
                }
        
        except Exception as e:
            logger.error(f"ML anomaly detection error: {e}")
        
        return None
    
    def _rule_based_detection(self, market_data: Dict, historical_context: Optional[List[Dict]]) -> Dict:
        """Rule-based anomaly detection."""
        anomaly_score = 0.0
        anomaly_count = 0
        
        # Price anomaly
        price = market_data.get('probability', 0.5)
        if abs(price - 0.5) > 0.45:  # Very close to 0 or 1
            anomaly_score += 0.3
            anomaly_count += 1
        
        # Volume anomaly
        volume = market_data.get('volume_24h', 0)
        if historical_context and len(historical_context) > 0:
            avg_volume = np.mean([m.get('volume_24h', 0) for m in historical_context])
            if volume > avg_volume * self.thresholds['volume_spike']:
                anomaly_score += 0.4
                anomaly_count += 1
        
        # Spread anomaly
        spread = market_data.get('spread', 0.1)
        if spread > 0.2:  # Very wide spread
            anomaly_score += 0.3
            anomaly_count += 1
        
        # Liquidity anomaly
        liquidity = market_data.get('liquidity', 0)
        if liquidity < 1000:  # Very low liquidity
            anomaly_score += 0.2
            anomaly_count += 1
        
        is_anomaly = anomaly_count >= 2 or anomaly_score > 0.6
        
        return {
            'is_anomaly': is_anomaly,
            'anomaly_score': min(anomaly_score, 1.0),
            'confidence': 0.7
        }
    
    def _detect_anomaly_types(self, market_data: Dict, historical_context: Optional[List[Dict]]) -> List[str]:
        """Detect specific types of anomalies."""
        anomaly_types = []
        
        price = market_data.get('probability', 0.5)
        volume = market_data.get('volume_24h', 0)
        liquidity = market_data.get('liquidity', 0)
        spread = market_data.get('spread', 0.1)
        
        # Price anomalies
        if price < 0.05 or price > 0.95:
            anomaly_types.append('extreme_price')
        
        # Volume anomalies
        if historical_context and len(historical_context) > 0:
            avg_volume = np.mean([m.get('volume_24h', 0) for m in historical_context[-10:]])
            if volume > avg_volume * 3:
                anomaly_types.append('volume_spike')
            elif volume < avg_volume * 0.1 and avg_volume > 0:
                anomaly_types.append('volume_drop')
        
        # Liquidity anomalies
        if liquidity < 1000:
            anomaly_types.append('low_liquidity')
        
        # Spread anomalies
        if spread > 0.2:
            anomaly_types.append('wide_spread')
        elif spread < 0.01:
            anomaly_types.append('narrow_spread')
        
        # Combined anomalies
        if volume > 0 and liquidity > 0:
            vol_liq_ratio = volume / liquidity
            if vol_liq_ratio > 2:
                anomaly_types.append('unusual_trading_activity')
        
        return anomaly_types
    
    def _calculate_severity(self, anomaly_score: float, anomaly_types: List[str]) -> str:
        """Calculate severity level of detected anomalies."""
        if anomaly_score > 0.8 or len(anomaly_types) >= 3:
            return 'critical'
        elif anomaly_score > 0.6 or len(anomaly_types) >= 2:
            return 'high'
        elif anomaly_score > 0.4 or len(anomaly_types) >= 1:
            return 'medium'
        else:
            return 'low'
    
    def batch_detect(self, markets_data: List[Dict]) -> List[Dict]:
        """Detect anomalies in multiple markets."""
        results = []
        for market_data in markets_data:
            result = self.detect(market_data)
            result['market_id'] = market_data.get('id', 'unknown')
            results.append(result)
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get statistics about detected anomalies."""
        if len(self.historical_data) == 0:
            return {
                'total_samples': 0,
                'model_trained': False
            }
        
        X = np.array(list(self.historical_data))
        
        return {
            'total_samples': len(self.historical_data),
            'model_trained': self.model is not None and SKLEARN_AVAILABLE,
            'feature_dimensions': X.shape[1],
            'contamination_rate': self.contamination,
            'detection_method': 'isolation_forest' if SKLEARN_AVAILABLE else 'rule_based'
        }
    
    def reset(self):
        """Reset the detector and clear historical data."""
        self.historical_data.clear()
        if SKLEARN_AVAILABLE:
            self.model = IsolationForest(
                contamination=self.contamination,
                random_state=42,
                n_estimators=100
            )
            self.scaler = StandardScaler()
        
        logger.info("Anomaly detector reset")
