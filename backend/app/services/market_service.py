"""Market service for querying market data from DuckDB."""
from typing import List, Optional, Dict, Any
from datetime import datetime
import duckdb

from ..core.database import get_connection, TBL_STATS, TBL_HIST, TBL_OB
from ..models.market import MarketListItem, MarketStats, MarketFilter


class MarketService:
    """Service for market data operations."""
    
    @staticmethod
    def get_markets(filters: MarketFilter) -> List[Dict[str, Any]]:
        """Get list of markets with filters."""
        con = get_connection()
        try:
            # Build WHERE clause
            where_clauses = []
            params = {}
            
            if filters.category:
                where_clauses.append("category = $category")
                params["category"] = filters.category
            
            if filters.min_liquidity is not None:
                where_clauses.append("liquidity >= $min_liquidity")
                params["min_liquidity"] = filters.min_liquidity
            
            if filters.max_liquidity is not None:
                where_clauses.append("liquidity <= $max_liquidity")
                params["max_liquidity"] = filters.max_liquidity
            
            if filters.min_volume is not None:
                where_clauses.append("volume >= $min_volume")
                params["min_volume"] = filters.min_volume
            
            if filters.max_volume is not None:
                where_clauses.append("volume <= $max_volume")
                params["max_volume"] = filters.max_volume
            
            if filters.trade_signal:
                where_clauses.append("trade_signal = $trade_signal")
                params["trade_signal"] = filters.trade_signal
            
            if filters.active_only:
                where_clauses.append("active = true AND closed = false")
            
            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
            
            # Get latest snapshot for each market
            query = f"""
            WITH latest AS (
                SELECT market_id, MAX(snapshot_ts) as max_ts
                FROM {TBL_STATS}
                GROUP BY market_id
            )
            SELECT 
                s.market_id,
                s.title,
                s.category,
                s.yes_price,
                s.no_price,
                s.volume,
                s.liquidity,
                s.trade_signal,
                s.degen_risk,
                s.snapshot_ts
            FROM {TBL_STATS} s
            INNER JOIN latest l ON s.market_id = l.market_id AND s.snapshot_ts = l.max_ts
            WHERE {where_sql}
            ORDER BY s.liquidity DESC NULLS LAST
            LIMIT $limit OFFSET $offset
            """
            
            params["limit"] = filters.limit
            params["offset"] = filters.offset
            
            df = con.execute(query, params).fetchdf()
            return df.to_dict(orient="records")
        finally:
            con.close()
    
    @staticmethod
    def get_market_by_id(market_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed market stats by ID (latest snapshot)."""
        con = get_connection()
        try:
            query = f"""
            SELECT *
            FROM {TBL_STATS}
            WHERE market_id = $market_id
            ORDER BY snapshot_ts DESC
            LIMIT 1
            """
            
            df = con.execute(query, {"market_id": market_id}).fetchdf()
            if df.empty:
                return None
            return df.to_dict(orient="records")[0]
        finally:
            con.close()
    
    @staticmethod
    def get_market_history(
        market_id: str,
        interval: str = "1w",
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Get price history for a market."""
        con = get_connection()
        try:
            # First get token IDs
            token_query = f"""
            SELECT yes_token_id
            FROM {TBL_STATS}
            WHERE market_id = $market_id
            ORDER BY snapshot_ts DESC
            LIMIT 1
            """
            
            token_df = con.execute(token_query, {"market_id": market_id}).fetchdf()
            if token_df.empty or token_df["yes_token_id"].iloc[0] is None:
                return []
            
            yes_token_id = token_df["yes_token_id"].iloc[0]
            
            # Get history
            hist_query = f"""
            SELECT t, price
            FROM {TBL_HIST}
            WHERE token_id = $token_id AND interval = $interval
            ORDER BY t DESC
            LIMIT $limit
            """
            
            df = con.execute(hist_query, {
                "token_id": yes_token_id,
                "interval": interval,
                "limit": limit
            }).fetchdf()
            
            return df.to_dict(orient="records")
        finally:
            con.close()
    
    @staticmethod
    def get_market_orderbook(market_id: str) -> Dict[str, Any]:
        """Get latest orderbook for a market."""
        con = get_connection()
        try:
            # Get token IDs
            token_query = f"""
            SELECT yes_token_id, no_token_id
            FROM {TBL_STATS}
            WHERE market_id = $market_id
            ORDER BY snapshot_ts DESC
            LIMIT 1
            """
            
            token_df = con.execute(token_query, {"market_id": market_id}).fetchdf()
            if token_df.empty:
                return {"yes": {"bids": [], "asks": []}, "no": {"bids": [], "asks": []}}
            
            yes_token_id = token_df["yes_token_id"].iloc[0]
            no_token_id = token_df["no_token_id"].iloc[0]
            
            result = {"yes": {"bids": [], "asks": []}, "no": {"bids": [], "asks": []}}
            
            # Get latest orderbook snapshot
            if yes_token_id:
                ob_query = f"""
                SELECT side, level, price, size
                FROM {TBL_OB}
                WHERE token_id = $token_id
                  AND snapshot_ts = (
                      SELECT MAX(snapshot_ts) FROM {TBL_OB} WHERE token_id = $token_id
                  )
                ORDER BY side, level
                """
                
                df = con.execute(ob_query, {"token_id": yes_token_id}).fetchdf()
                if not df.empty:
                    bids = df[df["side"] == "bid"].to_dict(orient="records")
                    asks = df[df["side"] == "ask"].to_dict(orient="records")
                    result["yes"] = {"bids": bids, "asks": asks}
            
            if no_token_id:
                df = con.execute(ob_query, {"token_id": no_token_id}).fetchdf()
                if not df.empty:
                    bids = df[df["side"] == "bid"].to_dict(orient="records")
                    asks = df[df["side"] == "ask"].to_dict(orient="records")
                    result["no"] = {"bids": bids, "asks": asks}
            
            return result
        finally:
            con.close()
    
    @staticmethod
    def get_categories() -> List[str]:
        """Get list of unique categories."""
        con = get_connection()
        try:
            query = f"""
            SELECT DISTINCT category
            FROM {TBL_STATS}
            WHERE category IS NOT NULL
            ORDER BY category
            """
            
            df = con.execute(query).fetchdf()
            return df["category"].tolist()
        finally:
            con.close()
    
    @staticmethod
    def get_market_count() -> int:
        """Get total number of unique markets."""
        con = get_connection()
        try:
            query = f"""
            SELECT COUNT(DISTINCT market_id) as count
            FROM {TBL_STATS}
            """
            
            result = con.execute(query).fetchone()
            return result[0] if result else 0
        finally:
            con.close()
