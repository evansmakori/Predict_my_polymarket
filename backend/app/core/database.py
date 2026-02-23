"""
Database operations using DuckDB
"""
import duckdb
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
from .config import settings


# Table names
TBL_OB = "polymarket_orderbook"
TBL_HIST = "polymarket_prices_history"
TBL_STATS = "polymarket_market_stats"


# -------------------------
# Schema Definitions
# -------------------------
DDL_ORDERBOOK = f"""
CREATE TABLE IF NOT EXISTS {TBL_OB} (
    token_id TEXT,
    snapshot_ts TIMESTAMP,
    side TEXT,
    level INTEGER,
    price DOUBLE,
    size DOUBLE,
    PRIMARY KEY (token_id, snapshot_ts, side, level)
);
"""

DDL_HISTORY = f"""
CREATE TABLE IF NOT EXISTS {TBL_HIST} (
    token_id TEXT,
    t TIMESTAMP,
    interval TEXT,
    fidelity_min INTEGER,
    price DOUBLE,
    PRIMARY KEY (token_id, t, interval, fidelity_min)
);
"""

DDL_STATS = f"""
CREATE TABLE IF NOT EXISTS {TBL_STATS} (
    market_id TEXT,
    snapshot_ts TIMESTAMP,

    title TEXT,
    category TEXT,

    yes_token_id TEXT,
    no_token_id TEXT,

    yes_price DOUBLE,
    no_price DOUBLE,

    yes_midpoint DOUBLE,
    no_midpoint DOUBLE,
    yes_last_trade DOUBLE,
    no_last_trade DOUBLE,
    yes_display_price DOUBLE,
    no_display_price DOUBLE,

    ui_yes_price DOUBLE,
    ui_no_price DOUBLE,

    token_mapping_source TEXT,
    token_mapping_ok BOOLEAN,
    token_mapping_warning TEXT,
    token_mapping_anomaly BOOLEAN,
    clob_last_trade_anomaly BOOLEAN,

    best_ask_yes DOUBLE,
    best_bid_yes DOUBLE,
    best_ask_no DOUBLE,
    best_bid_no DOUBLE,

    last_trade_price DOUBLE,

    volume DOUBLE,
    volume_clob DOUBLE,
    volume_1wk DOUBLE,
    volume_1mo DOUBLE,
    liquidity DOUBLE,
    liquidity_clob DOUBLE,

    spread DOUBLE,
    order_min_size DOUBLE,
    min_tick DOUBLE,

    price_change_1d DOUBLE,
    price_change_1wk DOUBLE,
    price_change_1mo DOUBLE,
    price_change_1yr DOUBLE,

    start_date TIMESTAMP,
    end_date TIMESTAMP,
    accepting_orders_since TIMESTAMP,

    active BOOLEAN,
    closed BOOLEAN,
    funded BOOLEAN,
    ready BOOLEAN,

    neg_risk BOOLEAN,
    neg_risk_other BOOLEAN,
    uma_resolution_status TEXT,
    automatically_resolved BOOLEAN,

    created_at TIMESTAMP,
    updated_at TIMESTAMP,

    volatility_1w DOUBLE,
    ma_short DOUBLE,
    ma_long DOUBLE,
    ema_slope DOUBLE,
    overreaction_flag BOOLEAN,

    orderbook_imbalance DOUBLE,
    slippage_notional_1k DOUBLE,
    slippage_notional_10k DOUBLE,

    fair_value DOUBLE,
    expected_value DOUBLE,
    kelly_fraction DOUBLE,
    trade_signal TEXT,
    late_overconfidence BOOLEAN,

    base_rate DOUBLE,
    base_rate_deviation DOUBLE,
    sentiment_momentum DOUBLE,
    liquidity_score DOUBLE,
    degen_risk DOUBLE,

    PRIMARY KEY (market_id, snapshot_ts)
);
"""


def get_connection() -> duckdb.DuckDBPyConnection:
    """Get a DuckDB connection."""
    return duckdb.connect(settings.DUCKDB_PATH)


def ensure_tables(con: duckdb.DuckDBPyConnection):
    """Create all tables if not exist."""
    con.execute(DDL_ORDERBOOK)
    con.execute(DDL_HISTORY)
    con.execute(DDL_STATS)


def upsert_orderbook(con: duckdb.DuckDBPyConnection, ob_rows: List[Dict[str, Any]], asof: datetime):
    """MERGE upsert for orderbook; adds snapshot_ts column."""
    if not ob_rows:
        return
    df = pd.DataFrame(ob_rows)
    if df.empty:
        return
    df["snapshot_ts"] = asof

    con.register("ob_src", df)
    ensure_tables(con)
    con.execute(f"""
        MERGE INTO {TBL_OB} AS t
        USING (
            SELECT token_id, snapshot_ts, side, level, price, size
            FROM ob_src
        ) AS s
        ON  t.token_id    = s.token_id
        AND t.snapshot_ts = s.snapshot_ts
        AND t.side        = s.side
        AND t.level       = s.level
        WHEN MATCHED THEN UPDATE SET
            price = s.price,
            size  = s.size
        WHEN NOT MATCHED THEN INSERT (
            token_id, snapshot_ts, side, level, price, size
        ) VALUES (
            s.token_id, s.snapshot_ts, s.side, s.level, s.price, s.size
        );
    """)


def upsert_history(con: duckdb.DuckDBPyConnection, hist_rows: List[Dict[str, Any]]):
    """MERGE upsert for history bars."""
    if not hist_rows:
        return
    df = pd.DataFrame(hist_rows)
    if df.empty:
        return
    con.register("hist_src", df)
    ensure_tables(con)
    con.execute(f"""
        MERGE INTO {TBL_HIST} AS t
        USING (
            SELECT token_id, t, interval, fidelity_min, price
            FROM hist_src
        ) AS s
        ON t.token_id = s.token_id
       AND t.t = s.t
       AND t.interval = s.interval
       AND t.fidelity_min = s.fidelity_min
        WHEN MATCHED THEN UPDATE SET
            price = s.price
        WHEN NOT MATCHED THEN INSERT (token_id, t, interval, fidelity_min, price)
        VALUES (s.token_id, s.t, s.interval, s.fidelity_min, s.price);
    """)


def upsert_market_stats(con: duckdb.DuckDBPyConnection, stats_rows: List[Dict[str, Any]]):
    """MERGE upsert for market-level stats & signals."""
    if not stats_rows:
        return
    df = pd.DataFrame(stats_rows)
    if df.empty:
        return

    # Normalize timestamps
    for col in ["start_date", "end_date", "accepting_orders_since", "created_at", "updated_at", "snapshot_ts"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)

    con.register("stats_src", df)
    ensure_tables(con)

    con.execute(f"""
        MERGE INTO {TBL_STATS} AS t
        USING (
            SELECT * FROM stats_src
        ) AS s
        ON  t.market_id    = s.market_id
        AND t.snapshot_ts  = s.snapshot_ts

        WHEN MATCHED THEN UPDATE SET
            title = s.title,
            category = s.category,
            yes_token_id = s.yes_token_id,
            no_token_id = s.no_token_id,
            yes_price = s.yes_price,
            no_price = s.no_price,
            yes_midpoint = s.yes_midpoint,
            no_midpoint = s.no_midpoint,
            yes_last_trade = s.yes_last_trade,
            no_last_trade = s.no_last_trade,
            yes_display_price = s.yes_display_price,
            no_display_price = s.no_display_price,
            ui_yes_price = s.ui_yes_price,
            ui_no_price = s.ui_no_price,
            token_mapping_source = s.token_mapping_source,
            token_mapping_ok = s.token_mapping_ok,
            token_mapping_warning = s.token_mapping_warning,
            token_mapping_anomaly = s.token_mapping_anomaly,
            clob_last_trade_anomaly = s.clob_last_trade_anomaly,
            best_ask_yes = s.best_ask_yes,
            best_bid_yes = s.best_bid_yes,
            best_ask_no = s.best_ask_no,
            best_bid_no = s.best_bid_no,
            last_trade_price = s.last_trade_price,
            volume = s.volume,
            volume_clob = s.volume_clob,
            volume_1wk = s.volume_1wk,
            volume_1mo = s.volume_1mo,
            liquidity = s.liquidity,
            liquidity_clob = s.liquidity_clob,
            spread = s.spread,
            order_min_size = s.order_min_size,
            min_tick = s.min_tick,
            price_change_1d = s.price_change_1d,
            price_change_1wk = s.price_change_1wk,
            price_change_1mo = s.price_change_1mo,
            price_change_1yr = s.price_change_1yr,
            start_date = s.start_date,
            end_date = s.end_date,
            accepting_orders_since = s.accepting_orders_since,
            active = s.active,
            closed = s.closed,
            funded = s.funded,
            ready = s.ready,
            neg_risk = s.neg_risk,
            neg_risk_other = s.neg_risk_other,
            uma_resolution_status = s.uma_resolution_status,
            automatically_resolved = s.automatically_resolved,
            created_at = s.created_at,
            updated_at = s.updated_at,
            volatility_1w = s.volatility_1w,
            ma_short = s.ma_short,
            ma_long = s.ma_long,
            ema_slope = s.ema_slope,
            overreaction_flag = s.overreaction_flag,
            orderbook_imbalance = s.orderbook_imbalance,
            slippage_notional_1k = s.slippage_notional_1k,
            slippage_notional_10k = s.slippage_notional_10k,
            fair_value = s.fair_value,
            expected_value = s.expected_value,
            kelly_fraction = s.kelly_fraction,
            trade_signal = s.trade_signal,
            late_overconfidence = s.late_overconfidence,
            base_rate = s.base_rate,
            base_rate_deviation = s.base_rate_deviation,
            sentiment_momentum = s.sentiment_momentum,
            liquidity_score = s.liquidity_score,
            degen_risk = s.degen_risk

        WHEN NOT MATCHED THEN INSERT (
            market_id, snapshot_ts,
            title, category,
            yes_token_id, no_token_id,
            yes_price, no_price,
            yes_midpoint, no_midpoint,
            yes_last_trade, no_last_trade,
            yes_display_price, no_display_price,
            ui_yes_price, ui_no_price,
            token_mapping_source, token_mapping_ok, token_mapping_warning, token_mapping_anomaly,
            clob_last_trade_anomaly,
            best_ask_yes, best_bid_yes,
            best_ask_no, best_bid_no,
            last_trade_price,
            volume, volume_clob, volume_1wk, volume_1mo, liquidity, liquidity_clob,
            spread, order_min_size, min_tick,
            price_change_1d, price_change_1wk, price_change_1mo, price_change_1yr,
            start_date, end_date, accepting_orders_since,
            active, closed, funded, ready,
            neg_risk, neg_risk_other, uma_resolution_status, automatically_resolved,
            created_at, updated_at,
            volatility_1w, ma_short, ma_long, ema_slope,
            overreaction_flag, orderbook_imbalance,
            slippage_notional_1k, slippage_notional_10k,
            fair_value, expected_value, kelly_fraction, trade_signal, late_overconfidence,
            base_rate, base_rate_deviation, sentiment_momentum, liquidity_score, degen_risk
        ) VALUES (
            s.market_id, s.snapshot_ts,
            s.title, s.category,
            s.yes_token_id, s.no_token_id,
            s.yes_price, s.no_price,
            s.yes_midpoint, s.no_midpoint,
            s.yes_last_trade, s.no_last_trade,
            s.yes_display_price, s.no_display_price,
            s.ui_yes_price, s.ui_no_price,
            s.token_mapping_source, s.token_mapping_ok, s.token_mapping_warning, s.token_mapping_anomaly,
            s.clob_last_trade_anomaly,
            s.best_ask_yes, s.best_bid_yes,
            s.best_ask_no, s.best_bid_no,
            s.last_trade_price,
            s.volume, s.volume_clob, s.volume_1wk, s.volume_1mo, s.liquidity, s.liquidity_clob,
            s.spread, s.order_min_size, s.min_tick,
            s.price_change_1d, s.price_change_1wk, s.price_change_1mo, s.price_change_1yr,
            s.start_date, s.end_date, s.accepting_orders_since,
            s.active, s.closed, s.funded, s.ready,
            s.neg_risk, s.neg_risk_other, s.uma_resolution_status, s.automatically_resolved,
            s.created_at, s.updated_at,
            s.volatility_1w, s.ma_short, s.ma_long, s.ema_slope,
            s.overreaction_flag, s.orderbook_imbalance,
            s.slippage_notional_1k, s.slippage_notional_10k,
            s.fair_value, s.expected_value, s.kelly_fraction, s.trade_signal, s.late_overconfidence,
            s.base_rate, s.base_rate_deviation, s.sentiment_momentum, s.liquidity_score, s.degen_risk
        );
    """)
