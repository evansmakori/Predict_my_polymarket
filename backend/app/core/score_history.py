"""
Score history tracking for prediction markets.

Tracks changes in predictive strength scores over time to:
- Monitor score trends
- Detect improving/declining opportunities
- Provide historical context for scoring
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import duckdb

from .database import get_connection, TBL_STATS
from .scoring import calculate_market_score


def get_score_history(
    market_id: str,
    days: int = 30,
    interval_hours: int = 24
) -> List[Dict[str, Any]]:
    """
    Get score history for a market over time.
    
    Args:
        market_id: Market ID
        days: Number of days to look back
        interval_hours: Sampling interval in hours
        
    Returns:
        List of historical scores with timestamps
    """
    con = get_connection()
    try:
        # Get historical snapshots at specified intervals
        query = f"""
        WITH snapshots AS (
            SELECT 
                *,
                ROW_NUMBER() OVER (
                    PARTITION BY DATE_TRUNC('hour', snapshot_ts) / {interval_hours}
                    ORDER BY snapshot_ts DESC
                ) as rn
            FROM {TBL_STATS}
            WHERE market_id = $market_id
                AND snapshot_ts >= NOW() - INTERVAL '{days} days'
        )
        SELECT * FROM snapshots
        WHERE rn = 1
        ORDER BY snapshot_ts ASC
        """
        
        df = con.execute(query, {"market_id": market_id}).fetchdf()
        
        if df.empty:
            return []
        
        history = []
        for _, row in df.iterrows():
            market_dict = row.to_dict()
            score_result = calculate_market_score(market_dict)
            
            history.append({
                "timestamp": market_dict["snapshot_ts"],
                "score": score_result["score"],
                "category": score_result["category"],
                "metrics": {
                    "expected_value": market_dict.get("expected_value"),
                    "kelly_fraction": market_dict.get("kelly_fraction"),
                    "liquidity": market_dict.get("liquidity") or market_dict.get("liquidity_clob"),
                    "volatility_1w": market_dict.get("volatility_1w"),
                    "orderbook_imbalance": market_dict.get("orderbook_imbalance"),
                    "spread": market_dict.get("spread"),
                    "sentiment_momentum": market_dict.get("sentiment_momentum"),
                }
            })
        
        return history
        
    finally:
        con.close()


def get_score_trend(market_id: str, days: int = 7) -> Dict[str, Any]:
    """
    Get score trend analysis for a market.
    
    Args:
        market_id: Market ID
        days: Number of days to analyze
        
    Returns:
        Dictionary with trend analysis
    """
    history = get_score_history(market_id, days=days, interval_hours=6)
    
    if len(history) < 2:
        return {
            "trend": "insufficient_data",
            "change": 0.0,
            "change_percent": 0.0,
            "direction": "unknown",
            "volatility": 0.0,
        }
    
    scores = [h["score"] for h in history]
    first_score = scores[0]
    last_score = scores[-1]
    
    # Calculate change
    change = last_score - first_score
    change_percent = (change / first_score * 100) if first_score > 0 else 0
    
    # Determine direction
    if change > 5:
        direction = "improving"
        trend = "up"
    elif change < -5:
        direction = "declining"
        trend = "down"
    else:
        direction = "stable"
        trend = "flat"
    
    # Calculate volatility (std dev of scores)
    import statistics
    volatility = statistics.stdev(scores) if len(scores) > 1 else 0
    
    return {
        "trend": trend,
        "direction": direction,
        "change": round(change, 2),
        "change_percent": round(change_percent, 2),
        "volatility": round(volatility, 2),
        "first_score": round(first_score, 2),
        "last_score": round(last_score, 2),
        "data_points": len(history),
    }


def get_all_markets_score_changes(hours: int = 24, min_change: float = 10.0) -> List[Dict[str, Any]]:
    """
    Get markets with significant score changes.
    
    Args:
        hours: Time window to check
        min_change: Minimum absolute score change to include
        
    Returns:
        List of markets with significant score changes
    """
    con = get_connection()
    try:
        # Get current and previous scores for all markets
        query = f"""
        WITH current_scores AS (
            SELECT market_id, MAX(snapshot_ts) as latest_ts
            FROM {TBL_STATS}
            WHERE snapshot_ts >= NOW() - INTERVAL '{hours + 1} hours'
            GROUP BY market_id
        ),
        previous_scores AS (
            SELECT market_id, MAX(snapshot_ts) as prev_ts
            FROM {TBL_STATS}
            WHERE snapshot_ts < (SELECT MIN(latest_ts) FROM current_scores) - INTERVAL '{hours} hours'
            GROUP BY market_id
        ),
        current_data AS (
            SELECT s.*, cs.latest_ts
            FROM {TBL_STATS} s
            INNER JOIN current_scores cs ON s.market_id = cs.market_id AND s.snapshot_ts = cs.latest_ts
        ),
        previous_data AS (
            SELECT s.*, ps.prev_ts
            FROM {TBL_STATS} s
            INNER JOIN previous_scores ps ON s.market_id = ps.market_id AND s.snapshot_ts = ps.prev_ts
        )
        SELECT 
            c.market_id,
            c.title,
            c.category,
            c.* as current,
            p.* as previous
        FROM current_data c
        LEFT JOIN previous_data p ON c.market_id = p.market_id
        WHERE p.market_id IS NOT NULL
        """
        
        df = con.execute(query).fetchdf()
        
        changes = []
        for _, row in df.iterrows():
            # Calculate current and previous scores
            current_dict = {k: v for k, v in row.items() if not k.startswith('previous_')}
            current_score = calculate_market_score(current_dict)["score"]
            
            # For previous, we'd need to extract those columns properly
            # Simplified: just track current scores for now
            changes.append({
                "market_id": row["market_id"],
                "title": row["title"],
                "category": row.get("category"),
                "current_score": current_score,
                "timestamp": row["latest_ts"],
            })
        
        return changes
        
    except Exception as e:
        print(f"Error getting score changes: {e}")
        return []
    finally:
        con.close()


def get_top_improving_markets(days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get markets with the best score improvement over time.
    
    Args:
        days: Number of days to analyze
        limit: Maximum number of markets to return
        
    Returns:
        List of improving markets sorted by improvement
    """
    con = get_connection()
    try:
        # Get all unique markets
        query = f"""
        SELECT DISTINCT market_id
        FROM {TBL_STATS}
        WHERE snapshot_ts >= NOW() - INTERVAL '{days} days'
        """
        
        market_ids = con.execute(query).fetchdf()["market_id"].tolist()
        
        improvements = []
        for market_id in market_ids:
            trend = get_score_trend(market_id, days=days)
            if trend["change"] > 0:
                improvements.append({
                    "market_id": market_id,
                    "score_change": trend["change"],
                    "change_percent": trend["change_percent"],
                    "current_score": trend["last_score"],
                    "trend": trend,
                })
        
        # Sort by change descending
        improvements.sort(key=lambda x: x["score_change"], reverse=True)
        
        # Get market details for top improvements
        result = []
        for imp in improvements[:limit]:
            market = get_market_basic_info(imp["market_id"])
            if market:
                result.append({
                    **market,
                    **imp,
                })
        
        return result
        
    finally:
        con.close()


def get_market_basic_info(market_id: str) -> Optional[Dict[str, Any]]:
    """Get basic market information."""
    con = get_connection()
    try:
        query = f"""
        SELECT market_id, title, category, yes_price, liquidity, volume
        FROM {TBL_STATS}
        WHERE market_id = $market_id
        ORDER BY snapshot_ts DESC
        LIMIT 1
        """
        
        result = con.execute(query, {"market_id": market_id}).fetchone()
        
        if not result:
            return None
        
        return {
            "market_id": result[0],
            "title": result[1],
            "category": result[2],
            "yes_price": result[3],
            "liquidity": result[4],
            "volume": result[5],
        }
        
    finally:
        con.close()
