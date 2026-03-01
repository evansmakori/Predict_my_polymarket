"""
ML Price Prediction Model using Neural Networks.

This module implements a deep learning model trained on DigitalOcean GPU
to predict market outcome probabilities and price movements.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta
import pickle
import os

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available. Using fallback prediction.")

logger = logging.getLogger(__name__)


class MarketPriceDataset(Dataset):
    """Dataset for market price prediction."""
    
    def __init__(self, features: np.ndarray, targets: np.ndarray):
        self.features = torch.FloatTensor(features)
        self.targets = torch.FloatTensor(targets)
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        return self.features[idx], self.targets[idx]


class PricePredictionNetwork(nn.Module):
    """
    Neural network for price prediction.
    
    Architecture:
    - Input layer: Market features (volume, liquidity, spread, etc.)
    - Hidden layers: 3 layers with dropout for regularization
    - Output layer: Predicted probability change
    """
    
    def __init__(self, input_size: int = 15, hidden_sizes: List[int] = [128, 64, 32]):
        super(PricePredictionNetwork, self).__init__()
        
        layers = []
        prev_size = input_size
        
        for hidden_size in hidden_sizes:
            layers.extend([
                nn.Linear(prev_size, hidden_size),
                nn.ReLU(),
                nn.BatchNorm1d(hidden_size),
                nn.Dropout(0.3)
            ])
            prev_size = hidden_size
        
        # Output layer - predicts price change
        layers.append(nn.Linear(prev_size, 1))
        layers.append(nn.Tanh())  # Output between -1 and 1
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.network(x)


class PricePredictor:
    """
    ML-powered price prediction system.
    
    Uses neural networks to predict market price movements based on:
    - Historical price data
    - Volume patterns
    - Liquidity metrics
    - Market sentiment
    - Time-based features
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or "models/price_predictor.pth"
        self.model = None
        self.scaler_path = "models/price_scaler.pkl"
        self.feature_scaler = None
        self.target_scaler = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        if TORCH_AVAILABLE:
            self._load_or_initialize_model()
        
        logger.info(f"PricePredictor initialized. Device: {self.device if TORCH_AVAILABLE else 'CPU (fallback)'}")
    
    def _load_or_initialize_model(self):
        """Load existing model or initialize new one."""
        if os.path.exists(self.model_path) and TORCH_AVAILABLE:
            try:
                self.model = PricePredictionNetwork()
                self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
                self.model.to(self.device)
                self.model.eval()
                
                # Load scalers
                if os.path.exists(self.scaler_path):
                    with open(self.scaler_path, 'rb') as f:
                        scalers = pickle.load(f)
                        self.feature_scaler = scalers['feature_scaler']
                        self.target_scaler = scalers['target_scaler']
                
                logger.info("Loaded existing price prediction model")
            except Exception as e:
                logger.error(f"Error loading model: {e}")
                self.model = None
        else:
            if TORCH_AVAILABLE:
                self.model = PricePredictionNetwork()
                self.model.to(self.device)
                logger.info("Initialized new price prediction model")
    
    def extract_features(self, market_data: Dict) -> np.ndarray:
        """
        Extract features from market data for prediction.
        
        Features include:
        - Current probability
        - Volume metrics (24h, normalized)
        - Liquidity indicators
        - Spread metrics
        - Time-based features
        - Market age
        - Volatility indicators
        """
        features = []
        
        # Price features
        current_price = market_data.get('probability', 0.5)
        features.append(current_price)
        features.append(current_price ** 2)  # Non-linear price feature
        features.append(abs(current_price - 0.5))  # Distance from 50%
        
        # Volume features
        volume_24h = market_data.get('volume_24h', 0)
        features.append(np.log1p(volume_24h))  # Log-scaled volume
        features.append(volume_24h / max(market_data.get('liquidity', 1), 1))  # Volume/liquidity ratio
        
        # Liquidity features
        liquidity = market_data.get('liquidity', 0)
        features.append(np.log1p(liquidity))
        
        # Spread features
        spread = market_data.get('spread', 0.1)
        features.append(spread)
        features.append(1 / max(spread, 0.001))  # Inverse spread
        
        # Time features
        end_date = market_data.get('end_date')
        if end_date:
            try:
                if isinstance(end_date, str):
                    end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                else:
                    end_dt = end_date
                days_until_end = (end_dt - datetime.now()).days
                features.append(max(days_until_end, 0))
                features.append(np.log1p(max(days_until_end, 0)))
            except:
                features.extend([0, 0])
        else:
            features.extend([0, 0])
        
        # Market age
        created_at = market_data.get('created_at')
        if created_at:
            try:
                if isinstance(created_at, str):
                    created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                else:
                    created_dt = created_at
                market_age_days = (datetime.now() - created_dt).days
                features.append(market_age_days)
                features.append(np.log1p(market_age_days))
            except:
                features.extend([0, 0])
        else:
            features.extend([0, 0])
        
        # Volatility proxy (if available)
        volatility = market_data.get('volatility', 0.1)
        features.append(volatility)
        
        # Additional market metrics
        features.append(market_data.get('num_trades', 0))
        
        return np.array(features, dtype=np.float32)
    
    def predict(self, market_data: Dict) -> Dict:
        """
        Predict price movement for a market.
        
        Returns:
            Dictionary with prediction results including:
            - predicted_change: Expected price change (-1 to 1)
            - confidence: Model confidence (0 to 1)
            - predicted_probability: New predicted probability
            - prediction_horizon: Time horizon for prediction
        """
        try:
            features = self.extract_features(market_data)
            
            if not TORCH_AVAILABLE or self.model is None:
                # Fallback: Simple heuristic prediction
                return self._fallback_prediction(market_data, features)
            
            # Scale features if scaler is available
            if self.feature_scaler:
                features = self.feature_scaler.transform(features.reshape(1, -1)).flatten()
            
            # Make prediction
            self.model.eval()
            with torch.no_grad():
                features_tensor = torch.FloatTensor(features).unsqueeze(0).to(self.device)
                prediction = self.model(features_tensor).cpu().numpy()[0][0]
            
            # Scale back if needed
            if self.target_scaler:
                prediction = self.target_scaler.inverse_transform([[prediction]])[0][0]
            
            current_prob = market_data.get('probability', 0.5)
            predicted_prob = np.clip(current_prob + prediction, 0.01, 0.99)
            
            # Calculate confidence based on feature quality
            confidence = self._calculate_confidence(market_data, features)
            
            return {
                'predicted_change': float(prediction),
                'confidence': float(confidence),
                'predicted_probability': float(predicted_prob),
                'current_probability': float(current_prob),
                'prediction_horizon': '24h',
                'model_type': 'neural_network',
                'features_used': len(features)
            }
        
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return self._fallback_prediction(market_data, features)
    
    def _fallback_prediction(self, market_data: Dict, features: np.ndarray) -> Dict:
        """Fallback prediction using heuristics when ML model is unavailable."""
        current_prob = market_data.get('probability', 0.5)
        volume = market_data.get('volume_24h', 0)
        liquidity = market_data.get('liquidity', 0)
        
        # Simple heuristic: higher volume and liquidity suggest trend continuation
        momentum = np.tanh((volume / max(liquidity, 1)) * 0.1)
        direction = 1 if current_prob > 0.5 else -1
        predicted_change = momentum * direction * 0.05
        
        predicted_prob = np.clip(current_prob + predicted_change, 0.01, 0.99)
        
        return {
            'predicted_change': float(predicted_change),
            'confidence': 0.5,
            'predicted_probability': float(predicted_prob),
            'current_probability': float(current_prob),
            'prediction_horizon': '24h',
            'model_type': 'heuristic_fallback',
            'features_used': len(features)
        }
    
    def _calculate_confidence(self, market_data: Dict, features: np.ndarray) -> float:
        """Calculate prediction confidence based on data quality."""
        confidence = 0.7  # Base confidence
        
        # Adjust based on data quality
        if market_data.get('volume_24h', 0) > 10000:
            confidence += 0.1
        if market_data.get('liquidity', 0) > 50000:
            confidence += 0.1
        if market_data.get('num_trades', 0) > 100:
            confidence += 0.1
        
        return min(confidence, 0.95)
    
    def train(self, training_data: List[Dict], epochs: int = 100, batch_size: int = 32):
        """
        Train the price prediction model.
        
        This method is designed to run on DigitalOcean GPU instances for faster training.
        
        Args:
            training_data: List of market data with historical prices
            epochs: Number of training epochs
            batch_size: Batch size for training
        """
        if not TORCH_AVAILABLE:
            logger.error("PyTorch not available. Cannot train model.")
            return
        
        logger.info(f"Training price prediction model with {len(training_data)} samples")
        
        # Prepare training data
        features_list = []
        targets_list = []
        
        for data in training_data:
            features = self.extract_features(data)
            # Target is the actual price change (if available in data)
            target = data.get('actual_change', 0.0)
            
            features_list.append(features)
            targets_list.append(target)
        
        X = np.array(features_list)
        y = np.array(targets_list).reshape(-1, 1)
        
        # Normalize features
        from sklearn.preprocessing import StandardScaler
        self.feature_scaler = StandardScaler()
        self.target_scaler = StandardScaler()
        
        X_scaled = self.feature_scaler.fit_transform(X)
        y_scaled = self.target_scaler.fit_transform(y)
        
        # Create dataset and dataloader
        dataset = MarketPriceDataset(X_scaled, y_scaled)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        # Initialize model
        self.model = PricePredictionNetwork(input_size=X.shape[1])
        self.model.to(self.device)
        
        # Training setup
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=0.001, weight_decay=1e-5)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=10)
        
        # Training loop
        self.model.train()
        for epoch in range(epochs):
            total_loss = 0
            for batch_features, batch_targets in dataloader:
                batch_features = batch_features.to(self.device)
                batch_targets = batch_targets.to(self.device)
                
                optimizer.zero_grad()
                predictions = self.model(batch_features)
                loss = criterion(predictions, batch_targets)
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            avg_loss = total_loss / len(dataloader)
            scheduler.step(avg_loss)
            
            if (epoch + 1) % 10 == 0:
                logger.info(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.6f}")
        
        # Save model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        torch.save(self.model.state_dict(), self.model_path)
        
        # Save scalers
        with open(self.scaler_path, 'wb') as f:
            pickle.dump({
                'feature_scaler': self.feature_scaler,
                'target_scaler': self.target_scaler
            }, f)
        
        logger.info(f"Model trained and saved to {self.model_path}")
    
    def get_model_info(self) -> Dict:
        """Get information about the current model."""
        return {
            'model_loaded': self.model is not None,
            'device': str(self.device) if TORCH_AVAILABLE else 'CPU',
            'torch_available': TORCH_AVAILABLE,
            'gpu_available': torch.cuda.is_available() if TORCH_AVAILABLE else False,
            'model_path': self.model_path
        }
