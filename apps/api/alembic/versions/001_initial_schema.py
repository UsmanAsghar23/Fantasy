"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-25

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sports",
        sa.Column("id", sa.SmallInteger(), nullable=False),
        sa.Column("code", sa.String(length=10), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("oauth_provider", sa.String(length=50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "teams",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sport_id", sa.SmallInteger(), nullable=False),
        sa.Column("external_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("abbreviation", sa.String(length=10), nullable=False),
        sa.ForeignKeyConstraint(["sport_id"], ["sports.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sport_id", "external_id", name="uq_teams_sport_external_id"),
    )
    op.create_index(op.f("ix_teams_sport_id"), "teams", ["sport_id"], unique=False)

    op.create_table(
        "players",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sport_id", sa.SmallInteger(), nullable=False),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("external_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("position", sa.String(length=20), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(["sport_id"], ["sports.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sport_id", "external_id", name="uq_players_sport_external_id"),
    )
    op.create_index(op.f("ix_players_sport_id"), "players", ["sport_id"], unique=False)
    op.create_index(op.f("ix_players_team_id"), "players", ["team_id"], unique=False)
    op.create_index(
        "ix_players_sport_id_name",
        "players",
        ["sport_id", "name"],
        unique=False,
    )

    op.create_table(
        "player_season_stats",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("player_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("season", sa.Integer(), nullable=False),
        sa.Column("games_played", sa.Integer(), nullable=False),
        sa.Column("stats", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "player_id",
            "season",
            name="uq_player_season_stats_player_season",
        ),
    )
    op.create_index(
        op.f("ix_player_season_stats_player_id"),
        "player_season_stats",
        ["player_id"],
        unique=False,
    )

    op.create_table(
        "player_game_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("player_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("game_date", sa.Date(), nullable=False),
        sa.Column("opponent_team_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("opponent_abbreviation", sa.String(length=10), nullable=True),
        sa.Column("stats", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["opponent_team_id"], ["teams.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_player_game_logs_game_date"),
        "player_game_logs",
        ["game_date"],
        unique=False,
    )
    op.create_index(
        op.f("ix_player_game_logs_player_id"),
        "player_game_logs",
        ["player_id"],
        unique=False,
    )
    op.create_index(
        "ix_player_game_logs_player_id_game_date",
        "player_game_logs",
        ["player_id", "game_date"],
        unique=False,
    )

    op.create_table(
        "user_watchlists",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("player_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "player_id", name="uq_user_watchlists_user_player"),
    )
    op.create_index(
        op.f("ix_user_watchlists_player_id"),
        "user_watchlists",
        ["player_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_watchlists_user_id"),
        "user_watchlists",
        ["user_id"],
        unique=False,
    )

    op.execute(
        sa.text(
            "INSERT INTO sports (id, code, name) VALUES "
            "(1, 'nfl', 'NFL'), (2, 'nba', 'NBA')"
        )
    )


def downgrade() -> None:
    op.drop_table("user_watchlists")
    op.drop_table("player_game_logs")
    op.drop_table("player_season_stats")
    op.drop_table("players")
    op.drop_table("teams")
    op.drop_table("users")
    op.drop_table("sports")
