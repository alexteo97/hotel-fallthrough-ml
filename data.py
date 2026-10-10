from pathlib import Path
import sqlite3
from urllib.request import urlretrieve

import pandas as pd


DATABASE_URL = (
    "https://techassessment.blob.core.windows.net/"
    "aiap25-assessment-data/hotel.db"
)

DEFAULT_DATABASE_PATH = (
    Path("data") / "hotel.db"
)


def resolve_database_path(
    db_path: str | Path | None = None,
) -> Path:
    """
    Resolve the SQLite database location.

    Priority:
    1. Explicitly supplied path.
    2. ./data/hotel.db
    3. ./hotel.db
    4. Download the official assessment database
       to ./data/hotel.db if it is not available locally.

    The database itself is excluded from Git.
    """

    if db_path is not None:
        path = Path(db_path)

        if path.exists():
            return path

        raise FileNotFoundError(
            "Database not found at supplied path: "
            f"{path}"
        )

    candidate_paths = [
        DEFAULT_DATABASE_PATH,
        Path("hotel.db"),
    ]

    for path in candidate_paths:
        if path.exists():
            return path

    print(
        "hotel.db not found locally."
    )

    print(
        "Downloading official assessment "
        "database..."
    )

    DEFAULT_DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    urlretrieve(
        DATABASE_URL,
        DEFAULT_DATABASE_PATH,
    )

    print(
        "Database downloaded successfully to:",
        DEFAULT_DATABASE_PATH,
    )

    return DEFAULT_DATABASE_PATH


def load_sqlite_table(
    db_path: str | Path,
    table_name: str,
) -> pd.DataFrame:
    """
    Load a SQLite table into a pandas DataFrame.
    """

    db_path = Path(db_path)

    with sqlite3.connect(
        db_path
    ) as connection:
        dataframe = pd.read_sql_query(
            f'SELECT * FROM "{table_name}"',
            connection,
        )

    return dataframe


def load_bookings(
    db_path: str | Path | None = None,
) -> pd.DataFrame:
    """
    Load the bookings table.
    """

    resolved_path = (
        resolve_database_path(
            db_path
        )
    )

    return load_sqlite_table(
        resolved_path,
        "bookings",
    )


def remove_exact_duplicates(
    bookings: pd.DataFrame,
) -> pd.DataFrame:
    """
    Remove exact duplicate booking records.
    """

    return (
        bookings
        .drop_duplicates()
        .reset_index(drop=True)
    )


def load_and_prepare_source_data(
    db_path: str | Path | None = None,
) -> pd.DataFrame:
    """
    Load raw bookings and remove exact
    duplicate source rows.
    """

    bookings = load_bookings(
        db_path
    )

    raw_rows = len(
        bookings
    )

    bookings = (
        remove_exact_duplicates(
            bookings
        )
    )

    deduplicated_rows = len(
        bookings
    )

    print(
        "Database loaded successfully."
    )

    print(
        f"Raw booking rows: "
        f"{raw_rows:,}"
    )

    print(
        "Exact duplicate rows removed: "
        f"{raw_rows - deduplicated_rows:,}"
    )

    print(
        "Booking rows after deduplication: "
        f"{deduplicated_rows:,}"
    )

    return bookings


if __name__ == "__main__":
    bookings = (
        load_and_prepare_source_data()
    )

    print(
        f"Columns loaded: "
        f"{bookings.shape[1]}"
    )