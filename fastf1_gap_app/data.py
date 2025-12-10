# Loads and processes F1 session data using FastF1

import os
import fastf1
import pandas as pd

# Enable FastF1 cache so that data is saved locally
# The cache folder should exist at the project root: ./fastf1_cache
CACHE_DIR = "fastf1_cache"
os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)


def load_session(year: int, event_name: str, session_type: str):
    session = fastf1.get_session(year, event_name, session_type)
    session.load()
    return session

def get_classification_table(session, session_type: str) -> pd.DataFrame:
    results = session.results.copy()

    # Common base columns
    base_cols = ["Position", "Abbreviation", "FullName", "TeamName", "Status"]

    if session_type == "Q":
        # Qualifying: use the best of Q1/Q2/Q3 as the driver's reference time
        quali_time_cols = [c for c in ["Q1", "Q2", "Q3"] if c in results.columns]

        cleaned = results[base_cols + quali_time_cols].copy()

        # Compute best quali time across Q1/Q2/Q3 (ignoring NaT)
        cleaned["race_time"] = cleaned[quali_time_cols].min(axis=1)

    else:
        # Race or other sessions: use 'Time' directly if available
        if "Time" not in results.columns:
            raise KeyError("Expected 'Time' column in session results for non-qualifying session.")

        cleaned = results[base_cols + ["Time"]].copy()
        cleaned = cleaned.rename(columns={"Time": "race_time"})

    # Standardize column names
    cleaned = cleaned.rename(
        columns={
            "Position": "position",
            "Abbreviation": "driver_code",
            "FullName": "driver_name",
            "TeamName": "team_name",
            "Status": "classification_status",
        }
    )

    return cleaned

def add_gap_column(table: pd.DataFrame, session_type: str | None = None) -> pd.DataFrame:
    table = table.copy()

    if session_type == "Q":
        secs = table["race_time"].dt.total_seconds()
        base = secs.min()
        table["gap_to_winner_s"] = secs - base
    else:
        table["gap_to_winner_s"] = table["race_time"].dt.total_seconds()

    table.loc[table["position"] == 1, "gap_to_winner_s"] = 0.0

    table["status"] = table["gap_to_winner_s"].apply(
        lambda x: "DNF" if pd.isna(x) else "FINISHED"
    )

    table = table.sort_values("position")
    return table

def get_race_gap_data(year: int, event_name: str, session_type: str) -> pd.DataFrame:
    session = load_session(year, event_name, session_type)
    table = get_classification_table(session, session_type=session_type)
    table = add_gap_column(table, session_type=session_type)
    return table
