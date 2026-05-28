import uuid
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.player import Player
from app.models.player_game_log import PlayerGameLog
from app.models.player_season_stat import PlayerSeasonStat
from app.models.team import Team


def upsert_team(
    db: Session,
    *,
    sport_id: int,
    external_id: str,
    name: str,
    abbreviation: str,
) -> Team:
    team = db.scalar(
        select(Team).where(
            Team.sport_id == sport_id,
            Team.external_id == external_id,
        )
    )
    if team:
        team.name = name
        team.abbreviation = abbreviation.upper()
    else:
        team = Team(
            id=uuid.uuid4(),
            sport_id=sport_id,
            external_id=external_id,
            name=name,
            abbreviation=abbreviation.upper(),
        )
        db.add(team)
    db.flush()
    return team


def upsert_player(
    db: Session,
    *,
    sport_id: int,
    external_id: str,
    name: str,
    position: str | None,
    status: str | None,
    team: Team | None,
) -> Player:
    player = db.scalar(
        select(Player).where(
            Player.sport_id == sport_id,
            Player.external_id == external_id,
        )
    )
    if player:
        player.name = name
        player.position = position
        player.status = status
        player.team_id = team.id if team else None
    else:
        player = Player(
            id=uuid.uuid4(),
            sport_id=sport_id,
            external_id=external_id,
            name=name,
            position=position,
            status=status,
            team_id=team.id if team else None,
        )
        db.add(player)
    db.flush()
    return player


def upsert_season_stat(
    db: Session,
    *,
    player: Player,
    season: int,
    games_played: int,
    stats: dict[str, Any],
) -> None:
    row = db.scalar(
        select(PlayerSeasonStat).where(
            PlayerSeasonStat.player_id == player.id,
            PlayerSeasonStat.season == season,
        )
    )
    if row:
        row.games_played = games_played
        row.stats = stats
    else:
        db.add(
            PlayerSeasonStat(
                id=uuid.uuid4(),
                player_id=player.id,
                season=season,
                games_played=games_played,
                stats=stats,
            )
        )


def clear_game_logs_for_sport(db: Session, sport_id: int) -> None:
    player_ids = select(Player.id).where(Player.sport_id == sport_id)
    db.execute(delete(PlayerGameLog).where(PlayerGameLog.player_id.in_(player_ids)))


def row_to_dict(row: dict[str, Any], exclude: set[str]) -> dict[str, Any]:
    return {k: v for k, v in row.items() if k not in exclude and v is not None}
