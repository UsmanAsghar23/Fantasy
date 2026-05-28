import time
import uuid
from datetime import date
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.core.sports import SPORT_NBA_ID
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

BALLDONTLIE_BASE = "https://api.balldontlie.io/v1"
REQUEST_DELAY_SEC = 0.12


def sync_nba(db: Session, season: int) -> dict[str, int]:
    """Sync NBA teams, players, season averages, and game stats via balldontlie."""
    with httpx.Client(base_url=BALLDONTLIE_BASE, timeout=60.0) as client:
        team_by_external = _sync_teams(db, client)
        db.commit()

        player_by_external = _sync_players(db, client, team_by_external)
        db.commit()

        _sync_season_averages(db, client, season, player_by_external)
        db.commit()

        clear_game_logs_for_sport(db, SPORT_NBA_ID)
        _sync_game_stats(db, client, season, player_by_external, team_by_external)
        db.commit()

    return {
        "teams": len(team_by_external),
        "players": len(player_by_external),
    }


def _sync_teams(db: Session, client: httpx.Client) -> dict[str, Team]:
    team_by_external: dict[str, Team] = {}
    cursor: int | None = None

    while True:
        params: dict[str, Any] = {"per_page": 100}
        if cursor:
            params["cursor"] = cursor
        response = client.get("/teams", params=params)
        response.raise_for_status()
        payload = response.json()
        time.sleep(REQUEST_DELAY_SEC)

        for row in payload.get("data", []):
            external_id = str(row["id"])
            abbr = str(row.get("abbreviation") or external_id).upper()
            team = upsert_team(
                db,
                sport_id=SPORT_NBA_ID,
                external_id=external_id,
                name=str(row.get("full_name") or row.get("name") or abbr),
                abbreviation=abbr,
            )
            team_by_external[external_id] = team

        cursor = payload.get("meta", {}).get("next_cursor")
        if not cursor:
            break

    return team_by_external


def _sync_players(
    db: Session,
    client: httpx.Client,
    team_by_external: dict[str, Team],
) -> dict[str, Player]:
    player_by_external: dict[str, Player] = {}
    cursor: int | None = None

    while True:
        params: dict[str, Any] = {"per_page": 100}
        if cursor:
            params["cursor"] = cursor
        response = client.get("/players", params=params)
        response.raise_for_status()
        payload = response.json()
        time.sleep(REQUEST_DELAY_SEC)

        for row in payload.get("data", []):
            external_id = str(row["id"])
            team_data = row.get("team") or {}
            team_ext = str(team_data["id"]) if team_data.get("id") is not None else None
            team = team_by_external.get(team_ext) if team_ext else None
            first = row.get("first_name") or ""
            last = row.get("last_name") or ""
            name = f"{first} {last}".strip() or external_id
            player = upsert_player(
                db,
                sport_id=SPORT_NBA_ID,
                external_id=external_id,
                name=name,
                position=_optional_str(row.get("position")),
                status=None,
                team=team,
            )
            player_by_external[external_id] = player

        cursor = payload.get("meta", {}).get("next_cursor")
        if not cursor:
            break

    return player_by_external


def _sync_season_averages(
    db: Session,
    client: httpx.Client,
    season: int,
    player_by_external: dict[str, Player],
) -> None:
    cursor: int | None = None
    exclude = {"player", "season", "games_played", "id"}

    while True:
        params: dict[str, Any] = {"season": season, "per_page": 100}
        if cursor:
            params["cursor"] = cursor
        response = client.get("/season_averages", params=params)
        response.raise_for_status()
        payload = response.json()
        time.sleep(REQUEST_DELAY_SEC)

        for row in payload.get("data", []):
            player_data = row.get("player") or {}
            external_id = str(player_data.get("id") or "")
            player = player_by_external.get(external_id)
            if not player:
                continue
            games = int(row.get("games_played") or 0)
            stats = row_to_dict(row, exclude)
            upsert_season_stat(
                db,
                player=player,
                season=season,
                games_played=games,
                stats=stats,
            )

        cursor = payload.get("meta", {}).get("next_cursor")
        if not cursor:
            break


def _sync_game_stats(
    db: Session,
    client: httpx.Client,
    season: int,
    player_by_external: dict[str, Player],
    team_by_external: dict[str, Team],
) -> None:
    cursor: int | None = None
    exclude = {"player", "team", "game", "id", "season", "postseason"}
    abbr_to_team = {t.abbreviation: t for t in team_by_external.values()}

    while True:
        params: dict[str, Any] = {"seasons[]": season, "per_page": 100}
        if cursor:
            params["cursor"] = cursor
        response = client.get("/stats", params=params)
        response.raise_for_status()
        payload = response.json()
        time.sleep(REQUEST_DELAY_SEC)

        for row in payload.get("data", []):
            player_data = row.get("player") or {}
            external_id = str(player_data.get("id") or "")
            player = player_by_external.get(external_id)
            if not player:
                continue
            game = row.get("game") or {}
            game_date = _parse_game_date(game.get("date"))
            if not game_date:
                continue
            opponent_abbr = _opponent_abbreviation(game, player_data)
            opponent_team = abbr_to_team.get(opponent_abbr) if opponent_abbr else None
            stats = row_to_dict(row, exclude)
            db.add(
                PlayerGameLog(
                    id=uuid.uuid4(),
                    player_id=player.id,
                    game_date=game_date,
                    opponent_team_id=opponent_team.id if opponent_team else None,
                    opponent_abbreviation=opponent_abbr,
                    stats=stats,
                )
            )

        cursor = payload.get("meta", {}).get("next_cursor")
        if not cursor:
            break


def _parse_game_date(value: Any) -> date | None:
    if not value:
        return None
    text = str(value)[:10]
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def _opponent_abbreviation(game: dict[str, Any], player_data: dict[str, Any]) -> str | None:
    home = game.get("home_team") or {}
    visitor = game.get("visitor_team") or {}
    player_team = player_data.get("team") or {}
    player_team_id = player_team.get("id")
    if player_team_id == home.get("id"):
        return _optional_str(visitor.get("abbreviation"))
    if player_team_id == visitor.get("id"):
        return _optional_str(home.get("abbreviation"))
    return None


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
