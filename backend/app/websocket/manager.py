import asyncio

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._active: list[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._active.append(ws)

    async def disconnect(self, ws: WebSocket) -> None:
        async with self._lock:
            self._active = [c for c in self._active if c is not ws]

    async def broadcast(self, message: str) -> None:
        """Sends to all active connections. Silently removes dead ones."""
        dead: list[WebSocket] = []

        async with self._lock:
            connections = list(self._active)

        for ws in connections:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)

        for ws in dead:
            await self.disconnect(ws)


# Singleton — imported by feed.py router and any future WebSocket consumers
manager = ConnectionManager()