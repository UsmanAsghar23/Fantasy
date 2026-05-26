import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Player(Base):
    __tablename__ = "players"
    __table_args__ = (
        UniqueConstraint("sport_id", "external_id", name="uq_players_sport_external_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    sport_id: Mapped[int] = mapped_column(
        ForeignKey("sports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    team_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("teams.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    external_id: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    position: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)

    sport: Mapped["Sport"] = relationship(back_populates="players")
    team: Mapped["Team | None"] = relationship(back_populates="players")
    season_stats: Mapped[list["PlayerSeasonStat"]] = relationship(
        back_populates="player",
        cascade="all, delete-orphan",
    )
    game_logs: Mapped[list["PlayerGameLog"]] = relationship(
        back_populates="player",
        cascade="all, delete-orphan",
    )
    watchlist_entries: Mapped[list["UserWatchlist"]] = relationship(
        back_populates="player",
        cascade="all, delete-orphan",
    )
