import os
import sys
import time

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://ops_platform:ops_platform@db:5432/ops_platform",
)
MAX_ATTEMPTS = int(os.environ.get("DB_WAIT_ATTEMPTS", "30"))
SLEEP_SECONDS = float(os.environ.get("DB_WAIT_SECONDS", "2"))


def main() -> int:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("select 1"))
            print("Database is ready.")
            return 0
        except SQLAlchemyError as exc:
            print(
                f"Database is not ready yet ({attempt}/{MAX_ATTEMPTS}): {exc}",
                file=sys.stderr,
            )
            time.sleep(SLEEP_SECONDS)

    print("Database did not become ready in time.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
