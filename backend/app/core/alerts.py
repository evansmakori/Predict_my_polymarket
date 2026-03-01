"""
Alert system for high-scoring market opportunities.

Monitors markets and generates alerts for:
- New high-scoring opportunities (score >= threshold)
- Significant score improvements
- Category-specific alerts
- Custom user-defined criteria
"""
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum

from .database import get_connection, TBL_STATS
from .scoring import calculate_market_score
from .score_history import get_score_trend


class AlertType(str, Enum):
    """Alert type enumeration."""
    HIGH_SCORE = "high_score"
    SCORE_INCREASE = "score_increase"
    SCORE_DECREASE = "score_decrease"
    NEW_OPPORTUNITY = "new_opportunity"
    CATEGORY_ALERT = "category_alert"
    CUSTOM = "custom"


class AlertPriority(str, Enum):
    """Alert priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Alert:
    """Alert object."""
    
    def __init__(
        self,
        alert_type: AlertType,
        market_id: str,
        title: str,
        message: str,
        priority: AlertPriority,
        score: float,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.alert_type = alert_type
        self.market_id = market_id
        self.title = title
        self.message = message
        self.priority = priority
        self.score = score
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            "alert_type": self.alert_type,
            "market_id": self.market_id,
            "title": self.title,
            "message": self.message,
            "priority": self.priority,
            "score": self.score,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


class AlertConfig:
    """Configuration for alert generation."""
    
    def __init__(
        self,
        min_score: float = 70.0,
        score_increase_threshold: float = 15.0,
        score_decrease_threshold: float = -15.0,
        categories: Optional[List[str]] = None,
        min_liquidity: Optional[float] = None,
        check_interval_hours: int = 6,
    ):
        self.min_score = min_score
        self.score_increase_threshold = score_increase_threshold
        self.score_decrease_threshold = score_decrease_threshold
        self.categories = categories
        self.min_liquidity = min_liquidity
        self.check_interval_hours = check_interval_hours


def check_high_score_alerts(config: AlertConfig) -> List[Alert]:
    """
    Check for markets with high scores.
    
    Args:
        config: Alert configuration
        
    Returns:
        List of high score alerts
    """
    from ..services.market_service import MarketService
    from ..models.market import MarketFilter
    
    # Get top opportunities
    filters = MarketFilter(
        category=config.categories[0] if config.categories else None,
        min_liquidity=config.min_liquidity,
        active_only=True,
        limit=100,
    )
    
    markets = MarketService.get_ranked_markets(filters)
    
    alerts = []
    for market in markets:
        score = market.get("predictive_strength_score", 0)
        
        if score >= config.min_score:
            # Determine priority based on score
            if score >= 90:
                priority = AlertPriority.CRITICAL
            elif score >= 80:
                priority = AlertPriority.HIGH
            elif score >= 70:
                priority = AlertPriority.MEDIUM
            else:
                priority = AlertPriority.LOW
            
            alert = Alert(
                alert_type=AlertType.HIGH_SCORE,
                market_id=market["market_id"],
                title=market["title"],
                message=f"High-scoring opportunity detected: {score:.1f}/100 ({market.get('score_category', 'N/A')})",
                priority=priority,
                score=score,
                metadata={
                    "category": market.get("category"),
                    "liquidity": market.get("liquidity"),
                    "expected_value": market.get("expected_value"),
                    "kelly_fraction": market.get("kelly_fraction"),
                }
            )
            alerts.append(alert)
    
    return alerts


def check_score_change_alerts(config: AlertConfig) -> List[Alert]:
    """
    Check for significant score changes.
    
    Args:
        config: Alert configuration
        
    Returns:
        List of score change alerts
    """
    con = get_connection()
    try:
        # Get all active markets
        query = f"""
        SELECT DISTINCT market_id, title, category
        FROM {TBL_STATS}
        WHERE active = true
        AND snapshot_ts >= NOW() - INTERVAL '7 days'
        """
        
        df = con.execute(query).fetchdf()
        
        alerts = []
        for _, row in df.iterrows():
            market_id = row["market_id"]
            
            # Get score trend
            trend = get_score_trend(market_id, days=1)
            
            if trend["change"] >= config.score_increase_threshold:
                # Significant increase
                priority = AlertPriority.HIGH if trend["change"] >= 20 else AlertPriority.MEDIUM
                
                alert = Alert(
                    alert_type=AlertType.SCORE_INCREASE,
                    market_id=market_id,
                    title=row["title"],
                    message=f"Score increased by {trend['change']:.1f} points ({trend['change_percent']:.1f}%) to {trend['last_score']:.1f}",
                    priority=priority,
                    score=trend["last_score"],
                    metadata={
                        "change": trend["change"],
                        "change_percent": trend["change_percent"],
                        "previous_score": trend["first_score"],
                        "category": row.get("category"),
                    }
                )
                alerts.append(alert)
                
            elif trend["change"] <= config.score_decrease_threshold:
                # Significant decrease
                priority = AlertPriority.MEDIUM if trend["change"] <= -20 else AlertPriority.LOW
                
                alert = Alert(
                    alert_type=AlertType.SCORE_DECREASE,
                    market_id=market_id,
                    title=row["title"],
                    message=f"Score decreased by {abs(trend['change']):.1f} points ({trend['change_percent']:.1f}%) to {trend['last_score']:.1f}",
                    priority=priority,
                    score=trend["last_score"],
                    metadata={
                        "change": trend["change"],
                        "change_percent": trend["change_percent"],
                        "previous_score": trend["first_score"],
                        "category": row.get("category"),
                    }
                )
                alerts.append(alert)
        
        return alerts
        
    finally:
        con.close()


def check_new_opportunities(hours_back: int = 24, min_score: float = 70.0) -> List[Alert]:
    """
    Check for new market opportunities.
    
    Args:
        hours_back: How far back to check for new markets
        min_score: Minimum score for new opportunity
        
    Returns:
        List of new opportunity alerts
    """
    con = get_connection()
    try:
        # Get markets that appeared in the last N hours with high scores
        query = f"""
        WITH first_seen AS (
            SELECT market_id, MIN(snapshot_ts) as first_ts
            FROM {TBL_STATS}
            GROUP BY market_id
        )
        SELECT s.*, fs.first_ts
        FROM {TBL_STATS} s
        INNER JOIN first_seen fs ON s.market_id = fs.market_id
        WHERE fs.first_ts >= NOW() - INTERVAL '{hours_back} hours'
        AND s.snapshot_ts = fs.first_ts
        AND s.active = true
        """
        
        df = con.execute(query).fetchdf()
        
        alerts = []
        for _, row in df.iterrows():
            market_dict = row.to_dict()
            score_result = calculate_market_score(market_dict)
            score = score_result["score"]
            
            if score >= min_score:
                priority = AlertPriority.HIGH if score >= 80 else AlertPriority.MEDIUM
                
                alert = Alert(
                    alert_type=AlertType.NEW_OPPORTUNITY,
                    market_id=market_dict["market_id"],
                    title=market_dict["title"],
                    message=f"New market opportunity: {score:.1f}/100 ({score_result['category']})",
                    priority=priority,
                    score=score,
                    metadata={
                        "category": market_dict.get("category"),
                        "first_seen": market_dict["first_ts"],
                        "liquidity": market_dict.get("liquidity"),
                    }
                )
                alerts.append(alert)
        
        return alerts
        
    finally:
        con.close()


def get_all_alerts(config: Optional[AlertConfig] = None) -> List[Dict[str, Any]]:
    """
    Get all current alerts based on configuration.
    
    Args:
        config: Alert configuration (uses defaults if None)
        
    Returns:
        List of all alerts as dictionaries
    """
    if config is None:
        config = AlertConfig()
    
    all_alerts = []
    
    # Check high score alerts
    try:
        high_score_alerts = check_high_score_alerts(config)
        all_alerts.extend([a.to_dict() for a in high_score_alerts])
    except Exception as e:
        print(f"Error checking high score alerts: {e}")
    
    # Check score change alerts
    try:
        change_alerts = check_score_change_alerts(config)
        all_alerts.extend([a.to_dict() for a in change_alerts])
    except Exception as e:
        print(f"Error checking score change alerts: {e}")
    
    # Check new opportunities
    try:
        new_alerts = check_new_opportunities(
            hours_back=config.check_interval_hours,
            min_score=config.min_score
        )
        all_alerts.extend([a.to_dict() for a in new_alerts])
    except Exception as e:
        print(f"Error checking new opportunities: {e}")
    
    # Sort by priority and score
    priority_order = {
        AlertPriority.CRITICAL: 0,
        AlertPriority.HIGH: 1,
        AlertPriority.MEDIUM: 2,
        AlertPriority.LOW: 3,
    }
    
    all_alerts.sort(
        key=lambda x: (priority_order.get(x["priority"], 99), -x["score"])
    )
    
    return all_alerts


def filter_alerts(
    alerts: List[Dict[str, Any]],
    alert_type: Optional[AlertType] = None,
    min_priority: Optional[AlertPriority] = None,
    category: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Filter alerts by criteria.
    
    Args:
        alerts: List of alerts to filter
        alert_type: Filter by alert type
        min_priority: Minimum priority level
        category: Filter by market category
        
    Returns:
        Filtered list of alerts
    """
    filtered = alerts
    
    if alert_type:
        filtered = [a for a in filtered if a["alert_type"] == alert_type]
    
    if min_priority:
        priority_order = {
            AlertPriority.CRITICAL: 0,
            AlertPriority.HIGH: 1,
            AlertPriority.MEDIUM: 2,
            AlertPriority.LOW: 3,
        }
        min_level = priority_order[min_priority]
        filtered = [
            a for a in filtered 
            if priority_order.get(a["priority"], 99) <= min_level
        ]
    
    if category:
        filtered = [
            a for a in filtered 
            if a.get("metadata", {}).get("category") == category
        ]
    
    return filtered
