"""WebSocket endpoints for real-time updates."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import asyncio
import json

from ..services.market_service import MarketService

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections and broadcasting."""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, market_id: str):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        if market_id not in self.active_connections:
            self.active_connections[market_id] = set()
        self.active_connections[market_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, market_id: str):
        """Remove a WebSocket connection."""
        if market_id in self.active_connections:
            self.active_connections[market_id].discard(websocket)
            if not self.active_connections[market_id]:
                del self.active_connections[market_id]
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket."""
        await websocket.send_json(message)
    
    async def broadcast(self, message: dict, market_id: str):
        """Broadcast a message to all connections watching a market."""
        if market_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[market_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.add(connection)
            
            # Clean up disconnected clients
            for connection in disconnected:
                self.active_connections[market_id].discard(connection)


manager = ConnectionManager()


@router.websocket("/ws/markets/{market_id}")
async def websocket_market_updates(websocket: WebSocket, market_id: str):
    """
    WebSocket endpoint for real-time market updates.
    
    Clients connect to this endpoint to receive live updates for a specific market.
    Updates are sent every 10 seconds (configurable).
    """
    await manager.connect(websocket, market_id)
    
    try:
        # Send initial data
        market_data = MarketService.get_market_by_id(market_id)
        if market_data:
            await manager.send_personal_message({
                "type": "initial",
                "data": market_data
            }, websocket)
        else:
            await manager.send_personal_message({
                "type": "error",
                "message": "Market not found"
            }, websocket)
            await websocket.close()
            return
        
        # Keep connection alive and send periodic updates
        while True:
            # Wait for client messages (ping/pong) or timeout
            try:
                # Set a timeout to send periodic updates
                await asyncio.wait_for(websocket.receive_text(), timeout=10.0)
            except asyncio.TimeoutError:
                # Send periodic update
                market_data = MarketService.get_market_by_id(market_id)
                if market_data:
                    await manager.send_personal_message({
                        "type": "update",
                        "data": market_data
                    }, websocket)
            except WebSocketDisconnect:
                break
    
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, market_id)


@router.websocket("/ws/markets")
async def websocket_all_markets(websocket: WebSocket):
    """
    WebSocket endpoint for updates on all markets.
    
    Sends periodic snapshots of all active markets.
    """
    await websocket.accept()
    
    try:
        while True:
            try:
                # Wait for ping or timeout
                await asyncio.wait_for(websocket.receive_text(), timeout=15.0)
            except asyncio.TimeoutError:
                # Send periodic update of all markets
                from ..models.market import MarketFilter
                markets = MarketService.get_markets(MarketFilter(limit=100))
                await websocket.send_json({
                    "type": "markets_update",
                    "data": markets
                })
            except WebSocketDisconnect:
                break
    
    except WebSocketDisconnect:
        pass
    finally:
        await websocket.close()
