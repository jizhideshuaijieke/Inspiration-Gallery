import asyncio
from collections import defaultdict

from fastapi import WebSocket


class TaskWebSocketManager:
    def __init__(self) -> None:
        self._connections: dict[int, set[WebSocket]] = defaultdict(set)
        self._task_base_urls: dict[int, str] = {}
        self._lock = asyncio.Lock()
        self._loop: asyncio.AbstractEventLoop | None = None

    def bind_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    def get_base_url(self, task_id: int) -> str | None:
        return self._task_base_urls.get(task_id)

    async def connect(self, task_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections[task_id].add(websocket)
            self._task_base_urls[task_id] = str(websocket.base_url).rstrip("/")

    async def disconnect(self, task_id: int, websocket: WebSocket) -> None:
        async with self._lock:
            sockets = self._connections.get(task_id)
            if not sockets:
                return

            sockets.discard(websocket)
            if sockets:
                return

            self._connections.pop(task_id, None)
            self._task_base_urls.pop(task_id, None)

    async def broadcast(self, task_id: int, payload: dict) -> None:
        async with self._lock:
            sockets = list(self._connections.get(task_id, ()))

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
            current = self._connections.get(task_id)
            if not current:
                return

            for websocket in stale_sockets:
                current.discard(websocket)

            if current:
                return

            self._connections.pop(task_id, None)
            self._task_base_urls.pop(task_id, None)

    def notify(self, task_id: int, payload: dict) -> None:
        if not self._loop:
            return

        asyncio.run_coroutine_threadsafe(self.broadcast(task_id, payload), self._loop)


task_ws_manager = TaskWebSocketManager()
