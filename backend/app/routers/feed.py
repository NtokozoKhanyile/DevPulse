import asyncio

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.dependencies.auth import get_current_user
from app.dependencies.pagination import PageParams
from app.models import User
from app.schemas.project import ProjectResponse
from app.services.feed_service import get_feed, subscribe_to_feed
from app.websocket.manager import manager

from jose import JWTError

router = APIRouter(tags=["feed"])


@router.get("/", response_model=list[ProjectResponse])
async def http_feed(
    pagination: PageParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list:
    return await get_feed(db, pagination)


@router.websocket("/ws")
async def websocket_feed(
    websocket: WebSocket,
    token: str = Query(...),
) -> None:
    # Authenticate via query param — WebSocket handshake cannot carry headers
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            await websocket.close(code=4001)
            return
    except (JWTError, Exception):
        await websocket.close(code=4001)
        return

    await manager.connect(websocket)

    try:
        # Keep the connection alive — client can send pings, we just receive
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(websocket)