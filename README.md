# F1 Gap Visualizer

A Streamlit web application that uses the FastF1 Python library to visualize **gaps to the race winner** across any Formula 1 session.  
Select a **year**, **Grand Prix**, and **session type** to instantly generate:

- A clean bar chart showing each finisher’s **gap to the winner**
- A full classification table (including **DNFs** and **lapped cars**)
- Automatic display of **Lapped** → `+1 Lap`, `+2 Laps`, etc.
- Team-colored bars using custom livery color mapping

This project showcases data engineering, visualization, clean UI design, and Python ecosystem tool integration.

---

## Features

### Session Selection
- Choose **season year** (2018–2024)
- Choose any **Grand Prix** from that season (auto-loaded from FastF1)
- Select **session type**:
  - Race (`R`)
  - Qualifying (`Q`)
  - Sprint (`S`)
  - FP1 / FP2 / FP3

### Gap Visualization
- Bar chart sorted by **official finishing position**
- Bars colored by team’s **primary livery color**
- `+1 Lap` labels automatically added for lapped drivers
- Clean marker for the race winner (`Leader`)

### Results Table
Displayed next to the chart:
- Position
- Driver code
- Team name
- Gap (`Leader`, `+X.XXXs`, `+1 Lap`, blank for DNFs)
- Status (`FINISHED` / `DNF`)

### Speed & Caching
- FastF1 disk caching for downloaded sessions
- Streamlit caching for repeated app usage
- Efficient processing pipeline

