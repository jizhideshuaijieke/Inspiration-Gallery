import asyncio
from collections import defaultdict

from fastapi import WebSocket


class ArtworkWebSocketManager:
    def __init__(self) -> None:
        self._connections: dict[int, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()
        self._loop: asyncio.AbstractEventLoop | None = None

    def bind_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    async def connect(self, artwork_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections[artwork_id].add(websocket)

    async def disconnect(self, artwork_id: int, websocket: WebSocket) -> None:
        async with self._lock:
            sockets = self._connections.get(artwork_id)
            if not sockets:
                return

            sockets.discard(websocket)
            if sockets:
                return

            self._connections.pop(artwork_id, None)

    async def broadcast(self, artwork_id: int, payload: dict) -> None:
        async with self._lock:
            sockets = list(self._connections.get(artwork_id, ()))

        if not sockets:
            return

        stale_sockets: list[WebSocket] = []
        for websocket in sockets:
            try:
                await websocket.send_json(payload)
            except Exception:
                stale_sockets.append(websocket)

        if not stale_sockets:
            return

        async with self._lock:
            current = self._connections.get(artwork_id)
            if not current:
                return

            for websocket in stale_sockets:
                current.discard(websocket)

            if not current:
                self._connections.pop(artwork_id, None)

    def notify_comments_refresh(
        self,
        artwork_id: int,
        reason: str,
        comment_count: int | None = None,
    ) -> None:
        if not self._loop or not artwork_id:
            return

        payload = {
            "type": "artwork_comments_refresh",
            "artwork_id": artwork_id,
            "reason": reason,
        }
        if comment_count is not None:
            payload["comment_count"] = comment_count

        asyncio.run_coroutine_threadsafe(self.broadcast(artwork_id, payload), self._loop)


artwork_ws_manager = ArtworkWebSocketManager()
