"""Market API endpoints."""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any

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
