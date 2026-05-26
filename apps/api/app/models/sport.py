from sqlalchemy import SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Sport(Base):
    __tablename__ = "sports"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    teams: Mapped[list["Team"]] = relationship(back_populates="sport")
    players: Mapped[list["Player"]] = relationship(back_populates="sport")
