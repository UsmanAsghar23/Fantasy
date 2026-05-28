import uuid
from datetime import date
from typing import Any

import nflreadpy as nfl
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.sports import SPORT_NFL_ID
from app.models.player import Player
from app.models.player_game_log import PlayerGameLog
from app.models.team import Team
from app.services.sync.common import (
    clear_game_logs_for_sport,
    row_to_dict,
    upsert_player,
    upsert_season_stat,
    upsert_team,
)


def _rows(df: Any) -> list[dict[str, Any]]:
    return df.to_dicts()


def _team_lookup(db: Session) -> dict[str, Team]:
    teams = db.scalars(select(Team).where(Team.sport_id == SPORT_NFL_ID)).all()
    return {t.abbreviation.upper(): t for t in teams}


def sync_nfl(db: Session, season: int) -> dict[str, int]:
    """Sync NFL teams, players, season stats, and weekly game logs via nflverse."""
    teams_df = nfl.load_teams(seasons=[season])
    for row in _rows(teams_df):
        abbr = str(row.get("team_abbr") or row.get("team") or "").upper()
        if not abbr:
            continue
        upsert_team(
            db,
            sport_id=SPORT_NFL_ID,
            external_id=abbr,
            name=str(row.get("team_name") or row.get("team_nick") or abbr),
            abbreviation=abbr,
        )
    db.commit()

    team_by_abbr = _team_lookup(db)
    players_df = nfl.load_players()
    player_by_external: dict[str, Player] = {}

    for row in _rows(players_df):
        external_id = str(row.get("gsis_id") or row.get("player_id") or "")
        if not external_id:
            continue
        display_name = str(row.get("display_name") or row.get("player_name") or "")
        if not display_name:
            continue
        abbr = str(row.get("team") or row.get("recent_team") or "").upper() or None
        team = team_by_abbr.get(abbr) if abbr else None
        player = upsert_player(
            db,
            sport_id=SPORT_NFL_ID,
            external_id=external_id,
            name=display_name,
            position=_optional_str(row.get("position")),
            status=_optional_str(row.get("status")),
            team=team,
        )
        player_by_external[external_id] = player
        alt_id = str(row.get("player_id") or "")
        if alt_id and alt_id != external_id:
            player_by_external[alt_id] = player
    db.commit()

    stat_exclude = {
        "player_id",
        "player_name",
        "player_display_name",
        "season",
        "week",
        "season_type",
        "team",
        "opponent_team",
        "game_id",
    }

    season_df = nfl.load_player_stats(seasons=[season], summary_level="reg")
    for row in _rows(season_df):
        external_id = str(row.get("player_id") or "")
        player = player_by_external.get(external_id)
        if not player:
            continue
        games = int(row.get("games") or row.get("games_played") or 0)
        stats = row_to_dict(row, stat_exclude)
        upsert_season_stat(
            db,
            player=player,
            season=season,
            games_played=games,
            stats=stats,
        )
    db.commit()

    clear_game_logs_for_sport(db, SPORT_NFL_ID)
    weekly_df = nfl.load_player_stats(seasons=[season], summary_level="week")
    for row in _rows(weekly_df):
        external_id = str(row.get("player_id") or "")
        player = player_by_external.get(external_id)
        if not player:
            continue
        week = row.get("week")
        if week is None:
            continue
        game_date = _week_to_date(season, int(week))
        opponent = _optional_str(row.get("opponent_team"))
        stats = row_to_dict(row, stat_exclude | {"recent_team"})
        db.add(
            PlayerGameLog(
                id=uuid.uuid4(),
                player_id=player.id,
                game_date=game_date,
                opponent_team_id=team_by_abbr.get(opponent.upper()).id
                if opponent and opponent.upper() in team_by_abbr
                else None,
                opponent_abbreviation=opponent.upper() if opponent else None,
                stats=stats,
            )
        )
    db.commit()

    return {
        "teams": len(team_by_abbr),
        "players": len(player_by_external),
    }


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _week_to_date(season: int, week: int) -> date:
    """Approximate game log date from season year and week number."""
    from datetime import timedelta

    # NFL regular season typically starts early September
    start = date(season, 9, 1)
    return start + timedelta(weeks=max(week - 1, 0))
