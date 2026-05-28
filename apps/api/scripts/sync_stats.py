"""CLI to sync NFL/NBA stats into PostgreSQL.

Usage (from apps/api with venv active):
  python -m scripts.sync_stats --sport nfl --season 2024
  python -m scripts.sync_stats --sport nba --season 2024
  python -m scripts.sync_stats --sport all --season 2024
"""

import argparse
import sys

from app.db.session import SessionLocal
from app.services.sync.nba_sync import sync_nba
from app.services.sync.nfl_sync import sync_nfl


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync player/team stats into the database")
    parser.add_argument(
        "--sport",
        required=True,
        choices=["nfl", "nba", "all"],
        help="Sport to sync",
    )
    parser.add_argument(
        "--season",
        type=int,
        default=2024,
        help="Season year (default: 2024)",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        sports = ["nfl", "nba"] if args.sport == "all" else [args.sport]
        for sport in sports:
            print(f"Syncing {sport.upper()} season {args.season}...")
            if sport == "nfl":
                counts = sync_nfl(db, args.season)
            else:
                counts = sync_nba(db, args.season)
            print(f"  teams={counts['teams']} players={counts['players']}")
        print("Done.")
    except Exception as exc:
        db.rollback()
        print(f"Sync failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    finally:
        db.close()


if __name__ == "__main__":
    main()
