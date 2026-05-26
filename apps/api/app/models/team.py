import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Team(Base):
    __tablename__ = "teams"
    __table_args__ = (
        UniqueConstraint("sport_id", "external_id", name="uq_teams_sport_external_id"),
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
    external_id: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    abbreviation: Mapped[str] = mapped_column(String(10), nullable=False)

    sport: Mapped["Sport"] = relationship(back_populates="teams")
    players: Mapped[list["Player"]] = relationship(back_populates="team")
