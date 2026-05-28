from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class PlayerSummary(BaseModel):
    id: UUID
    name: str
    position: str | None
    sport: str
    team_abbreviation: str | None
    status: str | None

    model_config = {"from_attributes": True}


class SeasonStatOut(BaseModel):
    season: int
    games_played: int
    stats: dict

    model_config = {"from_attributes": True}


class GameLogOut(BaseModel):
    game_date: date
    opponent_abbreviation: str | None
    stats: dict

    model_config = {"from_attributes": True}


class PlayerDetail(PlayerSummary):
    external_id: str
    season_stats: list[SeasonStatOut]
    recent_game_logs: list[GameLogOut]


class PlayerListResponse(BaseModel):
    items: list[PlayerSummary]
    total: int
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
