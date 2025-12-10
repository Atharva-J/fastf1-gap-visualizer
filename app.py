# app.py
# Streamlit web app for your F1 gap visualizer

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import fastf1

from fastf1_gap_app.data import get_race_gap_data

# Config 

# Years to offer in the dropdown
YEARS = list(range(2018, 2025))

SESSION_OPTIONS = {
    "Race": "R",
    "Qualifying": "Q",
    "Sprint": "S",
    "Practice 1": "FP1",
    "Practice 2": "FP2",
    "Practice 3": "FP3",
}

TEAM_COLOR_MAP = {
    "Red Bull Racing": "#3671C6",   # Blue
    "Ferrari": "#E8002D",           # Red
    "Mercedes": "#00D2BE",          # Teal
    "McLaren": "#FF8000",           # Papaya orange
    "Aston Martin": "#006F62",      # Green
    "Kick Sauber": "#00E701",       # Neon green
    "Haas F1 Team": "#B6BABD",      # Grey/silver
    "RB": "#6692FF",                # Racing Bulls blue
    "Williams": "#00AEEF",          # Light blue
    "Alpine": "#0090FF",            # Alpine blue
}


# Helpers 

@st.cache_data(show_spinner=False)
def get_events_for_year(year: int):
    schedule = fastf1.get_event_schedule(year)
    # Use EventName (e.g. "Bahrain Grand Prix", "Italian Grand Prix")
    return schedule["EventName"].tolist()

def build_gap_figure(df: pd.DataFrame, year: int, event_name: str, session_code: str):
    # Finished drivers for bar chart
    finished = df[df["status"] == "FINISHED"].copy()
    finished = finished.sort_values("position")

    driver_labels = finished["driver_code"].tolist()
    gaps = finished["gap_to_winner_s"].tolist()
    colors = [TEAM_COLOR_MAP.get(team, "#999999")
              for team in finished["team_name"]]

    # Full table (finished + DNFs), sorted by position
    table_df = df.sort_values("position").copy()

    # Use shorter team names for prettier table output
    TEAM_DISPLAY_MAP = {
        "Red Bull Racing": "Red Bull",
        "Ferrari": "Ferrari",
        "Mercedes": "Mercedes",
        "McLaren": "McLaren",
        "Aston Martin": "Aston Martin",
        "Kick Sauber": "Sauber",
        "Haas F1 Team": "Haas",
        "RB": "VCARB",
        "Williams": "Williams",
        "Alpine": "Alpine",
    }
    table_df["team_display"] = table_df["team_name"].replace(TEAM_DISPLAY_MAP)

    def format_gap_row(row):
        gap = row["gap_to_winner_s"]
        finish_flag = row["status"]
        raw_status = row.get("classification_status", None)

        # DNFs: no gap text
        if finish_flag == "DNF":
            return ""

        # Lapped / multi-lap cars
        if isinstance(raw_status, str):
            if raw_status == "Lapped":
                return "+1 Lap"
            if raw_status.startswith("+") and "Lap" in raw_status:
                # e.g. "+2 Laps"
                return raw_status

        # Normal time gaps
        if pd.isna(gap):
            return ""
        if gap == 0:
            return "Leader"
        return f"+{gap:.3f}s"

    table_df["gap_display"] = table_df.apply(format_gap_row, axis=1)

    # Only use the display columns in the table
    table_data = table_df[["position", "driver_code",
                           "team_display", "gap_display", "status"]]

    # Figure with two columns: bar chart + table
    fig, (ax, ax_table) = plt.subplots(
        1, 2,
        figsize=(14, 6),  # a bit wider for nicer table layout
        gridspec_kw={"width_ratios": [3, 2.5]},
    )

    # Left: bar chart 
    ax.bar(driver_labels, gaps, color=colors)
    ax.set_xlabel("Driver")
    ax.set_ylabel("Gap to winner (s)")
    ax.set_title(f"{year} {event_name} – {session_code} gaps to winner")

    # Rotate driver labels for readability
    ax.set_xticklabels(driver_labels, rotation=45)

    # Add '+1 Lap' text above bars for lapped cars, staggered so they don't overlap
    lapped_index = 0
    for x, gap_val, raw_status in zip(
        driver_labels,
        gaps,
        finished.get("classification_status", [""] * len(finished)),
    ):
        if isinstance(raw_status, str) and raw_status == "Lapped":
            offset = 0.6 + 0.4 * lapped_index  # stagger vertically
            ax.text(
                x,
                gap_val + offset,   # slightly above the bar, staggered
                "+1 Lap",
                ha="center",
                va="bottom",
                fontsize=8,
            )
            lapped_index += 1

    # Right: results table 
    ax_table.axis("off")

    # Column widths (relative); tune if needed
    col_widths = [0.08, 0.12, 0.30, 0.20, 0.12]

    table = ax_table.table(
        cellText=table_data.values,
        colLabels=["Pos", "Driver", "Team", "Gap", "Status"],
        colWidths=col_widths,
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.1, 1.25)  # a bit taller and wider for readability
    ax_table.set_title("Race Results", fontsize=10)

    fig.tight_layout()
    return fig

# Streamlit UI 

st.set_page_config(page_title="F1 Gap Visualizer", layout="wide")

st.title("🏁 F1 Gap Visualizer")
st.write(
    "Select a season, event and session on the left to see the gaps to the winner "
    "and full race results."
)

with st.sidebar:
    st.header("Session selection")

    year = st.selectbox("Year", YEARS, index=len(YEARS) - 1)

    # Load event names for the selected year
    try:
        event_names = get_events_for_year(year)
    except Exception as e:
        st.error(f"Could not load event schedule for {year}: {e}")
        st.stop()

    event_name = st.selectbox("Event", event_names)

    session_label = st.selectbox("Session type", list(SESSION_OPTIONS.keys()))
    session_code = SESSION_OPTIONS[session_label]

    go = st.button("Generate plot")

if go:
    try:
        with st.spinner("Loading session and computing gaps..."):
            df = get_race_gap_data(year, event_name, session_code)
            fig = build_gap_figure(df, year, event_name, session_code)
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Something went wrong loading this session: {e}")
        st.stop()
else:
    st.info("Choose a year, event, and session in the sidebar, then click **Generate plot**.")

