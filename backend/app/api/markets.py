"""Market API endpoints."""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import List, Dict, Any, Optional

from ..models.market import (
    MarketListItem,
    MarketStats,
    MarketFilter,
    ExtractRequest,
    ExtractResponse,
)
from ..services.market_service import MarketService
from ..core.extractor import extract_from_url

router = APIRouter(prefix="/api/markets", tags=["markets"])


@router.get("/", response_model=List[Dict[str, Any]])
async def list_markets(
    category: str = None,
    min_liquidity: float = None,
    max_liquidity: float = None,
    min_volume: float = None,
    max_volume: float = None,
    trade_signal: str = None,
    active_only: bool = True,
    limit: int = 50,
    offset: int = 0,
):
    """
    List markets with optional filters.
    
    - **category**: Filter by category
    - **min_liquidity**: Minimum liquidity
    - **max_liquidity**: Maximum liquidity
    - **min_volume**: Minimum volume
    - **max_volume**: Maximum volume
    - **trade_signal**: Filter by trading signal (long/short/no-trade)
    - **active_only**: Show only active markets (default: true)
    - **limit**: Maximum number of results (default: 50, max: 500)
    - **offset**: Pagination offset (default: 0)
    """
    filters = MarketFilter(
        category=category,
        min_liquidity=min_liquidity,
        max_liquidity=max_liquidity,
        min_volume=min_volume,
        max_volume=max_volume,
        trade_signal=trade_signal,
        active_only=active_only,
        limit=min(limit, 500),
        offset=offset,
    )
    
    markets = MarketService.get_markets(filters)
    return markets


@router.get("/categories", response_model=List[str])
async def get_categories():
    """Get list of all unique market categories."""
    return MarketService.get_categories()


@router.get("/count", response_model=Dict[str, int])
async def get_market_count():
    """Get total number of unique markets in database."""
    count = MarketService.get_market_count()
    return {"count": count}


@router.get("/{market_id}", response_model=Dict[str, Any])
async def get_market(market_id: str):
    """
    Get detailed market information by ID.
    
    Returns the latest snapshot of market statistics.
    """
    market = MarketService.get_market_by_id(market_id)
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")
    return market


@router.get("/{market_id}/stats", response_model=Dict[str, Any])
async def get_market_stats(market_id: str):
    """
    Get market statistics (alias for get_market).
    """
    return await get_market(market_id)


@router.get("/{market_id}/history", response_model=List[Dict[str, Any]])
async def get_market_history(
    market_id: str,
    interval: str = "1w",
    limit: int = 1000,
):
    """
    Get price history for a market.
    
    - **interval**: Time interval (1w, 1m, etc.)
    - **limit**: Maximum number of data points
    """
    history = MarketService.get_market_history(market_id, interval, limit)
    return history


@router.get("/{market_id}/orderbook", response_model=Dict[str, Any])
async def get_market_orderbook(market_id: str):
    """
    Get current orderbook for a market.
    
    Returns bids and asks for both YES and NO tokens.
    """
    orderbook = MarketService.get_market_orderbook(market_id)
    return orderbook


@router.post("/extract", response_model=ExtractResponse)
async def extract_market_data(
    request: ExtractRequest,
    background_tasks: BackgroundTasks,
):
    """
    Extract market data from a Polymarket URL.
    
    This endpoint fetches data from Polymarket APIs and stores it in the database.
    The extraction runs in the foreground for immediate feedback.
    
    - **url**: Polymarket event or market URL
    - **depth**: Orderbook depth per side (default: 10)
    - **intervals**: Price history intervals (default: ["1w", "1m"])
    - **fidelity_min**: Price history fidelity in minutes (default: 60)
    - **base_rate**: Base rate for fair value calculation (default: 0.50)
    """
    try:
        result = extract_from_url(
            url=request.url,
            depth=request.depth,
            intervals=request.intervals,
            fidelity_min=request.fidelity_min,
            base_rate=request.base_rate,
        )
        return ExtractResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/ranked", response_model=List[Dict[str, Any]])
async def get_ranked_markets(
    category: Optional[str] = None,
    min_liquidity: Optional[float] = None,
    max_liquidity: Optional[float] = None,
    min_volume: Optional[float] = None,
    max_volume: Optional[float] = None,
    trade_signal: Optional[str] = None,
    active_only: bool = True,
    limit: int = 50,
    offset: int = 0,
):
    """
    Get markets ranked by predictive strength score.
    
    Returns markets sorted by their predictive strength score (highest first).
    Each market includes:
    - predictive_strength_score: Score from 0-100
    - score_category: Strong Buy / Moderate Opportunity / Neutral/Watchlist / Weak/Avoid
    - rank: Overall ranking position
    - score_breakdown: Detailed breakdown of normalized and weighted components
    
    Scoring is based on:
    - Expected Value (30%)
    - Kelly Fraction (20%)
    - Liquidity Score (15%)
    - Volatility (10%)
    - Orderbook Imbalance (10%)
    - Spread (5%)
    - Sentiment Momentum (10%)
    
    Query Parameters:
    - **category**: Filter by category
    - **min_liquidity**: Minimum liquidity
    - **max_liquidity**: Maximum liquidity
    - **min_volume**: Minimum volume
    - **max_volume**: Maximum volume
    - **trade_signal**: Filter by trading signal (long/short/no-trade)
    - **active_only**: Show only active markets (default: true)
    - **limit**: Maximum number of results (default: 50, max: 500)
    - **offset**: Pagination offset (default: 0)
    """
    filters = MarketFilter(
        category=category,
        min_liquidity=min_liquidity,
        max_liquidity=max_liquidity,
        min_volume=min_volume,
        max_volume=max_volume,
        trade_signal=trade_signal,
        active_only=active_only,
        limit=min(limit, 500),
        offset=offset,
    )
    
    ranked_markets = MarketService.get_ranked_markets(filters)
    return ranked_markets


@router.get("/opportunities", response_model=List[Dict[str, Any]])
async def get_top_opportunities(
    limit: int = Query(default=20, le=100),
    min_score: float = Query(default=60.0, ge=0, le=100),
    active_only: bool = True,
):
    """
    Get top market opportunities based on predictive strength score.
    
    This is a convenience endpoint that returns the highest-scoring markets
    that meet a minimum score threshold.
    
    Query Parameters:
    - **limit**: Maximum number of opportunities to return (default: 20, max: 100)
    - **min_score**: Minimum predictive strength score (default: 60.0)
    - **active_only**: Show only active markets (default: true)
    
    Returns markets in the following categories:
    - Score 80-100: Strong Buy
    - Score 60-79: Moderate Opportunity
    """
    opportunities = MarketService.get_top_opportunities(
        limit=limit,
        min_score=min_score,
        active_only=active_only,
    )
    return opportunities


@router.get("/{market_id}/score", response_model=Dict[str, Any])
async def get_market_score(market_id: str):
    """
    Get detailed predictive strength score breakdown for a specific market.
    
    Returns:
    - score: Final predictive strength score (0-100)
    - category: Score category (Strong Buy, etc.)
    - breakdown: Detailed component scores
      - normalized_components: Each metric normalized to 0-1
      - weighted_components: Each metric's contribution to final score
    - metrics: Raw metric values used for scoring
    
    Useful for understanding why a market received a particular score.
    """
    score_data = MarketService.get_market_score(market_id)
    if not score_data:
        raise HTTPException(status_code=404, detail="Market not found")
    return score_data


@router.get("/{market_id}/score-history", response_model=List[Dict[str, Any]])
async def get_market_score_history(
    market_id: str,
    days: int = Query(default=30, ge=1, le=365),
    interval_hours: int = Query(default=24, ge=1, le=168),
):
    """
    Get historical score data for a market.
    
    Returns time series of predictive strength scores to track trends over time.
    
    Query Parameters:
    - **days**: Number of days to look back (default: 30, max: 365)
    - **interval_hours**: Sampling interval in hours (default: 24, max: 168)
    
    Returns:
    - List of historical scores with timestamps and metrics
    """
    from ..core.score_history import get_score_history
    
    history = get_score_history(market_id, days=days, interval_hours=interval_hours)
    if not history:
        raise HTTPException(status_code=404, detail="No score history found for this market")
    return history


@router.get("/{market_id}/score-trend", response_model=Dict[str, Any])
async def get_market_score_trend(
    market_id: str,
    days: int = Query(default=7, ge=1, le=90),
):
    """
    Get score trend analysis for a market.
    
    Analyzes how the market's score has changed over time.
    
    Query Parameters:
    - **days**: Number of days to analyze (default: 7, max: 90)
    
    Returns:
    - trend: up/down/flat
    - direction: improving/declining/stable
    - change: Absolute score change
    - change_percent: Percentage change
    - volatility: Score volatility (std dev)
    """
    from ..core.score_history import get_score_trend
    
    trend = get_score_trend(market_id, days=days)
    return trend


@router.get("/analytics/improving", response_model=List[Dict[str, Any]])
async def get_improving_markets(
    days: int = Query(default=7, ge=1, le=30),
    limit: int = Query(default=10, ge=1, le=50),
):
    """
    Get markets with the best score improvements.
    
    Identifies markets that are becoming better opportunities over time.
    
    Query Parameters:
    - **days**: Number of days to analyze (default: 7, max: 30)
    - **limit**: Maximum number of markets to return (default: 10, max: 50)
    
    Returns:
    - List of markets sorted by score improvement
    """
    from ..core.score_history import get_top_improving_markets
    
    improving = get_top_improving_markets(days=days, limit=limit)
    return improving


@router.get("/alerts", response_model=List[Dict[str, Any]])
async def get_alerts(
    min_score: float = Query(default=70.0, ge=0, le=100),
    score_increase_threshold: float = Query(default=15.0, ge=0),
    alert_type: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
):
    """
    Get current market alerts.
    
    Returns alerts for high-scoring opportunities and significant score changes.
    
    Query Parameters:
    - **min_score**: Minimum score for high-score alerts (default: 70)
    - **score_increase_threshold**: Min score increase for alerts (default: 15)
    - **alert_type**: Filter by type (high_score, score_increase, score_decrease, new_opportunity)
    - **priority**: Filter by priority (critical, high, medium, low)
    - **category**: Filter by market category
    
    Returns:
    - List of alerts sorted by priority and score
    """
    from ..core.alerts import get_all_alerts, filter_alerts, AlertConfig, AlertType, AlertPriority
    
    config = AlertConfig(
        min_score=min_score,
        score_increase_threshold=score_increase_threshold,
    )
    
    alerts = get_all_alerts(config)
    
    # Apply filters
    if alert_type or priority or category:
        alert_type_enum = AlertType(alert_type) if alert_type else None
        priority_enum = AlertPriority(priority) if priority else None
        alerts = filter_alerts(
            alerts,
            alert_type=alert_type_enum,
            min_priority=priority_enum,
            category=category,
        )
    
    return alerts
