from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps.auth import get_current_user
from app.models.user import User
from app.schemas.player import PlayerSummary
from app.schemas.watchlist import WatchlistResponse
from app.services import watchlist_service

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@router.get("", response_model=WatchlistResponse)
def get_watchlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WatchlistResponse:
    return watchlist_service.list_watchlist(db, current_user)


@router.post("/{player_id}", response_model=PlayerSummary)
def add_watchlist_player(
    player_id: UUID,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PlayerSummary:
    summary, created = watchlist_service.add_to_watchlist(db, current_user, player_id)
    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return summary


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_watchlist_player(
    player_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    watchlist_service.remove_from_watchlist(db, current_user, player_id)
