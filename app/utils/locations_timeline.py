import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import timedelta
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle


def create_timeline(
    data, arrival_date_str, output_file="static/images/timeline_image.png"
):
    # Convert data to DataFrame - handle both list of dicts and direct input
    if isinstance(data, list):
        if all(isinstance(item, dict) for item in data):
            df = pd.DataFrame(data)
        else:
            # If it's a list but not of dictionaries, try to create DataFrame differently
            df = pd.DataFrame(data, columns=["Startdatum", "Einddatum", "Stad", "Land"])
    else:
        # If data is already a DataFrame
        df = data

    # Verify required columns exist
    required_columns = ["Startdatum", "Einddatum", "Stad", "Land"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print("Current columns in DataFrame:", df.columns.tolist())
        print("Data structure received:", data)
        raise ValueError(f"Missing required columns: {missing_columns}")

    # Convert dates to datetime
    df["Startdatum"] = pd.to_datetime(df["Startdatum"], format="%d-%m-%Y")
    df["Einddatum"] = pd.to_datetime(df["Einddatum"], format="%d-%m-%Y")
    df = df.sort_values("Startdatum")

    # Define arrival date and two years back
    arrival_date = pd.to_datetime(arrival_date_str, format="%d-%m-%Y")
    two_years_back = arrival_date - timedelta(days=2 * 365)

    # Filter data for the last 2 years from the arrival date
    df = df[df["Einddatum"] >= two_years_back].copy()

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(15, 6))
    fig.patch.set_facecolor("white")

    # Calculate all gaps (including start and end of timeline)
    gaps = []

    # Check gap at the start of the timeline
    if len(df) > 0:
        first_start = df["Startdatum"].iloc[0]
        if first_start > two_years_back:
            start_gap_days = (first_start - two_years_back).days
            if start_gap_days > 0:
                gaps.append((two_years_back, first_start - timedelta(days=1)))

        # Check gaps between stays
        for i in range(len(df) - 1):
            current_end = df["Einddatum"].iloc[i]
            next_start = df["Startdatum"].iloc[i + 1]
            gap_days = (next_start - current_end).days - 1
            if gap_days > 0:
                gaps.append(
                    (current_end + timedelta(days=1), next_start - timedelta(days=1))
                )

        # Check gap at the end of the timeline
        last_end = df["Einddatum"].iloc[-1]
        if last_end < arrival_date:
            end_gap_days = (arrival_date - last_end).days - 1
            if end_gap_days > 0:
                gaps.append((last_end + timedelta(days=1), arrival_date))

    # Plot settings
    base_level = 0
    bar_height = 0.3
    colors = plt.cm.Pastel1(np.linspace(0, 1, len(df)))

    # Plot stays
    for idx, row in df.iterrows():
        start_num = mdates.date2num(row["Startdatum"])
        end_num = mdates.date2num(row["Einddatum"])
        width = end_num - start_num

        rect = Rectangle(
            (start_num, base_level - bar_height / 2),
            width,
            bar_height,
            facecolor=colors[idx % len(colors)],
            edgecolor="none",
            alpha=0.7,
        )
        ax.add_patch(rect)

        location = f"{row['Stad']}, {row['Land']}"
        mid_point = start_num + width / 2
        ax.text(
            mid_point,
            base_level + bar_height / 2 + 0.05,
            location,
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )

        start_date = row["Startdatum"].strftime("%d-%b-%Y")
        end_date = row["Einddatum"].strftime("%d-%b-%Y")
        ax.text(
            start_num,
            base_level - bar_height / 2 - 0.1,
            start_date,
            ha="right",
            va="top",
            fontsize=8,
            rotation=45,
        )
        ax.text(
            end_num,
            base_level - bar_height / 2 - 0.1,
            end_date,
            ha="left",
            va="top",
            fontsize=8,
            rotation=45,
        )

    # Plot gaps with staggered labels
    for i, (gap_start, gap_end) in enumerate(gaps):
        ax.hlines(
            base_level,
            gap_start,
            gap_end,
            colors="red",
            linestyles="--",
            linewidth=2,
            alpha=0.5,
        )

        gap_duration = (gap_end - gap_start).days
        gap_label = f"{gap_start.strftime('%d-%b-%Y')} t/m {gap_end.strftime('%d-%b-%Y')} ({gap_duration} days)"

        vertical_position = base_level + bar_height + 0.1 + (i * 0.15)
        mid_point = mdates.date2num(gap_start + (gap_end - gap_start) / 2)
        ax.text(
            mid_point,
            vertical_position,
            gap_label,
            ha="center",
            va="bottom",
            fontsize=8,
            color="red",
        )

    # Add markers for timeline boundaries
    ax.axvline(
        x=mdates.date2num(two_years_back), color="black", linestyle="-", alpha=0.3
    )
    ax.axvline(x=mdates.date2num(arrival_date), color="black", linestyle="-", alpha=0.3)

    ax.text(
        mdates.date2num(two_years_back),
        -0.4,
        "Timeline Start\n" + two_years_back.strftime("%d-%b-%Y"),
        ha="center",
        va="top",
        fontsize=8,
        color="black",
    )
    ax.text(
        mdates.date2num(arrival_date),
        -0.4,
        "Arrival Date\n" + arrival_date.strftime("%d-%b-%Y"),
        ha="center",
        va="top",
        fontsize=8,
        color="black",
    )

    # Set axis limits
    ax.set_xlim(
        mdates.date2num(two_years_back - timedelta(days=30)),
        mdates.date2num(arrival_date + timedelta(days=30)),
    )
    ax.set_ylim(-0.5, 0.8 + (len(gaps) * 0.15))

    # Format x-axis
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.xticks(rotation=45)

    # Remove y-axis
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Add grid
    ax.grid(axis="x", linestyle="--", alpha=0.3)

    # Add title
    plt.title(
        "Timeline voor aanvang tewerkstelling", pad=20, fontsize=12, fontweight="bold"
    )

    # Save plot
    plt.tight_layout()
    plt.savefig(output_file, bbox_inches="tight", dpi=300)
    plt.close()

    print(f"Timeline image saved as {output_file}")
