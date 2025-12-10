# Uses the data loaded and cleaned in data.py to plot a bar chart

import matplotlib.pyplot as plt
import pandas as pd
from fastf1_gap_app.data import get_race_gap_data


TEAM_COLOR_MAP = {
    "Red Bull Racing": "#00255A",   
    "Ferrari": "#E8002D",          
    "Mercedes": "#00D2BE",         
    "McLaren": "#FF8000",           
    "Aston Martin": "#006F62",      
    "Kick Sauber": "#00E701",      
    "Haas F1 Team": "#B6BABD",      
    "RB": "#6692FF",               
    "Williams": "#00AEEF",          
    "Alpine": "#0090FF",            
}


def plot_race_gaps(df, year=None, event_name=None, session_type=None, show=True):
    # 1. Keep only finished drivers for the bar chart
    finished = df[df["status"] == "FINISHED"].copy()
    finished = finished.sort_values("position")

    driver_labels = finished["driver_code"].tolist()
    gaps = finished["gap_to_winner_s"].tolist()
    colors = [TEAM_COLOR_MAP.get(team, "#999999")
              for team in finished["team_name"]]

    # 2. Prepare full results table (including DNFs)
    table_df = df.sort_values("position").copy()

    def format_gap_row(row):
        gap = row["gap_to_winner_s"]
        finish_flag = row["status"]
        raw_status = row.get("classification_status", None)

        # DNFs: no gap text
        if finish_flag == "DNF":
            return ""

        # Lapped cars / multi-laps
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

    table_data = table_df[["position", "driver_code",
                           "team_name", "gap_display", "status"]]

    # 3. Create side-by-side chart + table
    fig, (ax, ax_table) = plt.subplots(
        1, 2,
        figsize=(12, 5),
        gridspec_kw={"width_ratios": [3, 2]}
    )

    # Left: bar chart 
    ax.bar(driver_labels, gaps, color=colors)
    ax.set_xlabel("Driver")
    ax.set_ylabel("Gap to winner (s)")

    if year is not None and event_name is not None and session_type is not None:
        ax.set_title(f"{year} {event_name} {session_type} – Gaps to winner")

    # Rotate driver labels for readability
    ax.set_xticklabels(driver_labels, rotation=45)

    # Add '+1 Lap' text above bars for lapped cars
    for x, gap_val, raw_status in zip(
        driver_labels,
        gaps,
        finished.get("classification_status", [""] * len(finished))
    ):
        if isinstance(raw_status, str) and raw_status == "Lapped":
            ax.text(
                x,
                gap_val + 1,   # slightly above the bar
                "+1 Lap",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    # Right: results table 
    ax_table.axis("off")

    table = ax_table.table(
        cellText=table_data.values,
        colLabels=["Pos", "Driver", "Team", "Gap", "Status"],
        loc="center"
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.2)
    ax_table.set_title("Race Results", fontsize=10)

    plt.tight_layout()
    if show:
        plt.show()
    return fig

def plot_race_gaps_for_session(year, event_name, session_type):
    # Uses the prevous function to plot the data
    df = get_race_gap_data(year, event_name, session_type)
    plot_race_gaps(df, year=year, event_name=event_name, session_type=session_type, show=True)



