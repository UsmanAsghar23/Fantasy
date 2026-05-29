import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.player import Player
from app.models.user import User
from app.models.user_watchlist import UserWatchlist
from app.schemas.player import PlayerSummary
from app.schemas.watchlist import WatchlistResponse
from app.services.player_service import _to_summary


def list_watchlist(db: Session, user: User) -> WatchlistResponse:
    entries = db.scalars(
        select(UserWatchlist)
        .where(UserWatchlist.user_id == user.id)
        .options(
            joinedload(UserWatchlist.player).joinedload(Player.team),
            joinedload(UserWatchlist.player).joinedload(Player.sport),
        )
        .order_by(UserWatchlist.created_at.desc())
    ).all()
    items = [_to_summary(entry.player) for entry in entries]
    return WatchlistResponse(items=items)


def add_to_watchlist(
    db: Session, user: User, player_id: uuid.UUID
) -> tuple[PlayerSummary, bool]:
    player = db.scalar(
        select(Player)
        .options(joinedload(Player.team), joinedload(Player.sport))
        .where(Player.id == player_id)
    )
    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")

    existing = db.scalar(
        select(UserWatchlist).where(
            UserWatchlist.user_id == user.id,
            UserWatchlist.player_id == player_id,
        )
    )
    if existing:
        return _to_summary(player), False

    db.add(
        UserWatchlist(
            id=uuid.uuid4(),
            user_id=user.id,
            player_id=player_id,
        )
    )
    db.commit()
    return _to_summary(player), True


def remove_from_watchlist(db: Session, user: User, player_id: uuid.UUID) -> None:
    entry = db.scalar(
        select(UserWatchlist).where(
            UserWatchlist.user_id == user.id,
            UserWatchlist.player_id == player_id,
        )
    )
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not on watchlist",
        )
    db.delete(entry)
    db.commit()
