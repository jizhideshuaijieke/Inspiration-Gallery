import asyncio
from collections import defaultdict

from fastapi import WebSocket


class NoticeWebSocketManager:
    def __init__(self) -> None:
        self._connections: dict[int, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()
        self._loop: asyncio.AbstractEventLoop | None = None

    def bind_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections[user_id].add(websocket)

    async def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        async with self._lock:
            sockets = self._connections.get(user_id)
            if not sockets:
                return

            sockets.discard(websocket)
            if sockets:
                return

            self._connections.pop(user_id, None)

    async def broadcast(self, user_id: int, payload: dict) -> None:
        async with self._lock:
            sockets = list(self._connections.get(user_id, ()))

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
            current = self._connections.get(user_id)
            if not current:
                return

            for websocket in stale_sockets:
                current.discard(websocket)

            if not current:
                self._connections.pop(user_id, None)

    def notify_refresh(self, user_id: int, reason: str) -> None:
        if not self._loop or not user_id:
            return

        payload = {
            "type": "notice_refresh",
            "reason": reason,
        }
        asyncio.run_coroutine_threadsafe(self.broadcast(user_id, payload), self._loop)


notice_ws_manager = NoticeWebSocketManager()
