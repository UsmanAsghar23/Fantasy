import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PlayerGameLog(Base):
    __tablename__ = "player_game_logs"

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
    game_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    opponent_team_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("teams.id", ondelete="SET NULL"),
        nullable=True,
    )
    opponent_abbreviation: Mapped[str | None] = mapped_column(String(10), nullable=True)
    stats: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    player: Mapped["Player"] = relationship(back_populates="game_logs")
