from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.player import PlayerDetail, PlayerListResponse
from app.services import player_service

router = APIRouter(prefix="/players", tags=["players"])


@router.get("", response_model=PlayerListResponse)
def search_players(
    sport: str | None = Query(default=None, description="Sport code: nfl or nba"),
    q: str | None = Query(default=None, description="Search player name"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PlayerListResponse:
    if sport and sport.lower() not in ("nfl", "nba"):
        raise HTTPException(status_code=400, detail="sport must be nfl or nba")
    return player_service.list_players(
        db,
        sport=sport,
        q=q,
        page=page,
        page_size=page_size,
    )


@router.get("/{player_id}", response_model=PlayerDetail)
def get_player(
    player_id: UUID,
    game_log_limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> PlayerDetail:
    return player_service.get_player_detail(db, player_id, game_log_limit=game_log_limit)
