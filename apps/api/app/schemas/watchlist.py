from pydantic import BaseModel

from app.schemas.player import PlayerSummary


class WatchlistResponse(BaseModel):
    items: list[PlayerSummary]
