import uuid

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PlayerSeasonStat(Base):
    __tablename__ = "player_season_stats"
    __table_args__ = (
        UniqueConstraint("player_id", "season", name="uq_player_season_stats_player_season"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    player_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    season: Mapped[int] = mapped_column(Integer, nullable=False)
    games_played: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stats: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    player: Mapped["Player"] = relationship(back_populates="season_stats")
