# Simple entry point for running the visualizer without Streamlit.
# Useful for debugging.


from fastf1_gap_app.data import get_race_gap_data
from fastf1_gap_app.plotting import plot_race_gaps_for_session


def main():
    # Example session — you can change this
    year = 2023
    event = "Monza"
    session = "R"

    df = get_race_gap_data(year, event, session)
    plot_race_gaps_for_session(year, event, session)


if __name__ == "__main__":
    main()
