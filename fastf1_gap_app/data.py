# Loads and processes F1 session data using FastF1

import fastf1
import pandas as pd

# Enable FastF1 cache so that data is saved locally
# The cache folder should exist at the project root: ./fastf1_cache
fastf1.Cache.enable_cache("fastf1_cache")


def load_session(year: int, event_name: str, session_type: str):
    session = fastf1.get_session(year, event_name, session_type)
    session.load()
    return session

def get_classification_table(session) -> pd.DataFrame:
    results = session.results.copy()

    cleaned = results[
        [
            "Position",
            "Abbreviation",
            "FullName",
            "TeamName",
            "Time",
            "Status",
        ]
    ]

    cleaned = cleaned.rename(
        columns={
            "Position": "position",
            "Abbreviation": "driver_code",
            "FullName": "driver_name",
            "TeamName": "team_name",
            "Time": "race_time",
            "Status": "classification_status",
        }
    )

    return cleaned

def add_gap_column(table: pd.DataFrame) -> pd.DataFrame:
    table = table.copy()

    # Convert race_time (timedelta) to seconds. DNFs will become NaN here.
    table["gap_to_winner_s"] = table["race_time"].dt.total_seconds()

    # Ensure winner is exactly 0.0
    winner_mask = table["position"] == 1
    table.loc[winner_mask, "gap_to_winner_s"] = 0.0

    # Mark DNFs vs finished based on the numeric gap
    table["status"] = table["gap_to_winner_s"].apply(
        lambda x: "DNF" if pd.isna(x) else "FINISHED"
    )

    # Keep rows ordered by position
    table = table.sort_values("position")

    return table

def get_race_gap_data(year: int, event_name: str, session_type: str) -> pd.DataFrame:
    session = load_session(year, event_name, session_type)
    table = get_classification_table(session)
    table = add_gap_column(table)
    return table
