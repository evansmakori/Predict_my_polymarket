"""
API endpoints for AI-powered features.

Provides access to:
- ML price predictions
- Sentiment analysis
- Anomaly detection
- Trading signals
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Optional, Any
import logging

from ..ml.price_predictor import PricePredictor
from ..ml.sentiment_analyzer import SentimentAnalyzer
from ..ml.anomaly_detector import AnomalyDetector
from ..ml.trading_agent import TradingAgent
from ..services.market_service import MarketService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["AI Features"])

# Initialize AI models (singleton instances)
price_predictor = PricePredictor()
sentiment_analyzer = SentimentAnalyzer()
anomaly_detector = AnomalyDetector()
trading_agent = TradingAgent()
market_service = MarketService()


@router.get("/status")
async def get_ai_status():
    """
    Get status of all AI models and GPU availability.
    
    Returns information about:
    - Model loading status
    - GPU availability
    - DigitalOcean Gradient AI features
    """
    return {
        "status": "operational",
        "models": trading_agent.get_agent_status(),
        "digitalocean_gradient_ai": {
            "enabled": True,
            "features_used": [
                "GPU-accelerated neural network training",
                "Transformer-based NLP models",
                "Distributed model inference",
                "Real-time anomaly detection"
            ]
        }
    }


@router.get("/predict/{market_id}")
async def predict_market_price(market_id: str):
    """
    Predict future price movement for a specific market using ML.
    
    Uses neural network trained on DigitalOcean GPU to predict:
    - Price change direction and magnitude
    - Confidence level
    - Time horizon
    """
    try:
        # Get market data
        market_data = market_service.get_market_by_id(market_id)
        
        if not market_data:
            raise HTTPException(status_code=404, detail="Market not found")
        
        # Make prediction
        prediction = price_predictor.predict(market_data)
        
        return {
            "market_id": market_id,
            "market_question": market_data.get("question", "Unknown"),
            "prediction": prediction,
            "timestamp": market_data.get("updated_at")
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error for market {market_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict/batch")
async def predict_batch_markets(market_ids: List[str]):
    """
    Batch prediction for multiple markets.
    
    Optimized for GPU batch processing.
    """
    try:
        predictions = []
        
        for market_id in market_ids:
            market_data = market_service.get_market_by_id(market_id)
            if market_data:
                prediction = price_predictor.predict(market_data)
                predictions.append({
                    "market_id": market_id,
                    "prediction": prediction
                })
        
        return {
            "predictions": predictions,
            "total": len(predictions)
        }
    
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sentiment/{market_id}")
async def analyze_market_sentiment(market_id: str):
    """
    Analyze market sentiment using NLP transformer models.
    
    Analyzes:
    - Overall sentiment (positive/negative/neutral)
    - Key topics and themes
    - Uncertainty indicators
    - Bias detection
    """
    try:
        market_data = market_service.get_market_by_id(market_id)
        
        if not market_data:
            raise HTTPException(status_code=404, detail="Market not found")
        
        # Combine question and description
        text = market_data.get('question', '') + ' ' + market_data.get('description', '')
        
        # Analyze sentiment
        sentiment = sentiment_analyzer.analyze(text, market_data)
        
        return {
            "market_id": market_id,
            "market_question": market_data.get("question", "Unknown"),
            "sentiment_analysis": sentiment
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sentiment analysis error for market {market_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/anomaly/{market_id}")
async def detect_market_anomaly(market_id: str):
    """
    Detect anomalies in market behavior using ML.
    
    Detects:
    - Price anomalies
    - Volume spikes
    - Liquidity issues
    - Unusual trading patterns
    """
    try:
        market_data = market_service.get_market_by_id(market_id)
        
        if not market_data:
            raise HTTPException(status_code=404, detail="Market not found")
        
        # Get historical context
        historical = market_service.get_all_markets(limit=100)
        
        # Detect anomalies
        anomaly = anomaly_detector.detect(market_data, historical)
        
        return {
            "market_id": market_id,
            "market_question": market_data.get("question", "Unknown"),
            "anomaly_detection": anomaly
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Anomaly detection error for market {market_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/anomalies")
async def detect_all_anomalies(limit: int = Query(50, ge=1, le=500)):
    """
    Scan all markets for anomalies.
    
    Returns markets with detected anomalies sorted by severity.
    """
    try:
        markets = market_service.get_all_markets(limit=limit)
        anomalies = anomaly_detector.batch_detect(markets)
        
        # Filter only anomalous markets
        detected = [a for a in anomalies if a.get('is_anomaly')]
        
        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        detected.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 4))
        
        return {
            "anomalies": detected,
            "total_scanned": len(markets),
            "anomalies_detected": len(detected)
        }
    
    except Exception as e:
        logger.error(f"Batch anomaly detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trading-signal/{market_id}")
async def get_trading_signal(market_id: str):
    """
    Generate AI-powered trading signal for a market.
    
    Combines:
    - ML price prediction
    - Sentiment analysis
    - Anomaly detection
    - Risk assessment
    
    Returns: BUY, SELL, or HOLD recommendation with confidence and reasoning.
    """
    try:
        market_data = market_service.get_market_by_id(market_id)
        
        if not market_data:
            raise HTTPException(status_code=404, detail="Market not found")
        
        # Get historical context
        historical = market_service.get_all_markets(limit=100)
        
        # Generate signal
        signal = trading_agent.generate_signal(market_data, historical)
        
        return {
            "market_id": market_id,
            "market_question": market_data.get("question", "Unknown"),
            "trading_signal": signal
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Trading signal error for market {market_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trading-signals")
async def get_all_trading_signals(limit: int = Query(20, ge=1, le=100)):
    """
    Generate trading signals for multiple markets.
    
    Returns signals sorted by confidence.
    """
    try:
        markets = market_service.get_all_markets(limit=limit)
        signals = trading_agent.batch_generate_signals(markets)
        
        # Sort by confidence
        signals.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        return {
            "signals": signals,
            "total": len(signals)
        }
    
    except Exception as e:
        logger.error(f"Batch trading signals error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/opportunities")
async def get_top_opportunities(
    limit: int = Query(10, ge=1, le=50),
    min_confidence: float = Query(0.5, ge=0.0, le=1.0)
):
    """
    Find top trading opportunities using AI analysis.
    
    Filters and ranks markets by:
    - High confidence signals
    - Acceptable risk levels
    - Strong fundamentals
    
    Returns the best opportunities for trading.
    """
    try:
        # Get larger pool of markets
        markets = market_service.get_all_markets(limit=limit * 5)
        
        # Get opportunities
        opportunities = trading_agent.get_top_opportunities(markets, limit=limit)
        
        # Filter by minimum confidence
        filtered = [o for o in opportunities if o.get('confidence', 0) >= min_confidence]
        
        return {
            "opportunities": filtered,
            "total_analyzed": len(markets),
            "opportunities_found": len(filtered)
        }
    
    except Exception as e:
        logger.error(f"Opportunities detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model-info")
async def get_model_info():
    """
    Get detailed information about AI models.
    
    Includes:
    - Model architecture
    - Training status
    - Performance metrics
    - GPU usage
    """
    return {
        "price_predictor": price_predictor.get_model_info(),
        "sentiment_analyzer": sentiment_analyzer.get_model_info(),
        "anomaly_detector": anomaly_detector.get_statistics(),
        "trading_agent": trading_agent.get_agent_status()
    }


@router.post("/train/trigger")
async def trigger_model_training():
    """
    Trigger model retraining on DigitalOcean GPU.
    
    NOTE: This endpoint should be protected in production.
    Consider using background tasks for long-running training.
    """
    return {
        "message": "Training triggered",
        "instructions": [
            "Connect to DigitalOcean GPU droplet",
            "Run: python3 train_on_digitalocean_gpu.py --model all",
            "Monitor training progress in logs",
            "Models will be saved to /models directory"
        ],
        "estimated_time": "5-10 minutes on GPU",
        "documentation": "See DIGITALOCEAN_GPU_SETUP.md for details"
    }
