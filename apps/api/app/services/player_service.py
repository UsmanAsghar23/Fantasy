from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.player import Player
from app.models.player_game_log import PlayerGameLog
from app.models.player_season_stat import PlayerSeasonStat
from app.models.sport import Sport
from app.schemas.player import PlayerDetail, PlayerListResponse, PlayerSummary


def _to_summary(player: Player) -> PlayerSummary:
    return PlayerSummary(
        id=player.id,
        name=player.name,
        position=player.position,
        sport=player.sport.code,
        team_abbreviation=player.team.abbreviation if player.team else None,
        status=player.status,
    )


def list_players(
    db: Session,
    *,
    sport: str | None,
    q: str | None,
    page: int,
    page_size: int,
) -> PlayerListResponse:
    filters = []
    if sport:
        filters.append(Sport.code == sport.lower())
    if q:
        filters.append(Player.name.ilike(f"%{q.strip()}%"))

    base = (
        select(Player)
        .join(Sport, Player.sport_id == Sport.id)
        .options(joinedload(Player.team), joinedload(Player.sport))
        .where(*filters)
        .order_by(Player.name)
    )

    total = db.scalar(
        select(func.count())
        .select_from(Player)
        .join(Sport, Player.sport_id == Sport.id)
        .where(*filters)
    )
    total = total or 0

    offset = (page - 1) * page_size
    players = db.scalars(base.offset(offset).limit(page_size)).all()

    return PlayerListResponse(
        items=[_to_summary(p) for p in players],
        total=total,
        page=page,
        page_size=page_size,
    )


def get_player_detail(
    db: Session,
    player_id: UUID,
    *,
    game_log_limit: int = 10,
) -> PlayerDetail:
    player = db.scalar(
        select(Player)
        .options(
            joinedload(Player.team),
            joinedload(Player.sport),
        )
        .where(Player.id == player_id)
    )
    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")

    season_stats = db.scalars(
        select(PlayerSeasonStat)
        .where(PlayerSeasonStat.player_id == player_id)
        .order_by(PlayerSeasonStat.season.desc())
    ).all()

    game_logs = db.scalars(
        select(PlayerGameLog)
        .where(PlayerGameLog.player_id == player_id)
        .order_by(PlayerGameLog.game_date.desc())
        .limit(game_log_limit)
    ).all()

    summary = _to_summary(player)
    return PlayerDetail(
        **summary.model_dump(),
        external_id=player.external_id,
        season_stats=list(season_stats),
        recent_game_logs=list(game_logs),
    )
