import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

matplotlib.use("Agg")  # Use the non-GUI backend for rendering


def create_timeline(
    data, arrival_date_str, output_file="static/images/timeline_image.png"
):
    # Convert data to DataFrame
    df = pd.DataFrame(data, columns=["Startdatum", "Einddatum", "Stad", "Land"])
    df["Startdatum"] = pd.to_datetime(df["Startdatum"], format="%d-%m-%Y")
    df["Einddatum"] = pd.to_datetime(df["Einddatum"], format="%d-%m-%Y")
    df.sort_values("Startdatum", inplace=True)

    # Define arrival date and two years back
    arrival_date = pd.to_datetime(arrival_date_str, format="%d-%m-%Y")
    two_years_back = arrival_date - timedelta(days=2 * 365)

    # Filter data for the last 2 years from the arrival date
    df = df[df["Einddatum"] >= two_years_back]

    # Check for gaps
    gaps = []
    for i in range(len(df) - 1):
        current_end = df.iloc[i]["Einddatum"]
        next_start = df.iloc[i + 1]["Startdatum"]
        if next_start > current_end + timedelta(days=1):
            gaps.append(
                (current_end + timedelta(days=1), next_start - timedelta(days=1))
            )

    # Create the timeline plot
    fig, ax = plt.subplots(figsize=(12, 6))
    positions = [i for i in range(len(df))]
    labels = df["Stad"] + ", " + df["Land"]
    start_dates = df["Startdatum"].dt.strftime("%d-%b-%Y")
    end_dates = df["Einddatum"].dt.strftime("%d-%b-%Y")

    # Plot periods of stay
    ax.hlines(
        positions,
        df["Startdatum"],
        df["Einddatum"],
        color="blue",
        linewidth=2,
        label="Stay",
    )
    ax.scatter(df["Startdatum"], positions, color="green", label="Start Date", zorder=2)
    ax.scatter(df["Einddatum"], positions, color="red", label="End Date", zorder=2)

    # Annotate stays
    for i, (start, end, label) in enumerate(zip(start_dates, end_dates, labels)):
        ax.text(
            df["Startdatum"].iloc[i],
            positions[i] + 0.1,
            start,
            fontsize=8,
            ha="right",
            color="green",
        )
        ax.text(
            df["Einddatum"].iloc[i],
            positions[i] + 0.1,
            end,
            fontsize=8,
            ha="left",
            color="red",
        )
        ax.text(
            df["Startdatum"].iloc[i]
            + (df["Einddatum"].iloc[i] - df["Startdatum"].iloc[i]) / 2,
            positions[i] - 0.3,
            label,
            fontsize=10,
            ha="center",
            color="black",
        )

    # Plot gaps
    gap_positions = len(df) + 1
    for gap_start, gap_end in gaps:
        ax.hlines(
            gap_positions,
            gap_start,
            gap_end,
            color="orange",
            linewidth=2,
            linestyle="--",
            label="Gap",
        )
        gap_label = (
            f"Gap: {gap_start.strftime('%d-%b-%Y')} to {gap_end.strftime('%d-%b-%Y')}"
        )
        ax.text(
            gap_start + (gap_end - gap_start) / 2,
            gap_positions + 0.1,
            gap_label,
            fontsize=8,
            ha="center",
            color="orange",
        )
        gap_positions += 1

    # Finalize plot
    ax.set_yticks(list(range(len(df))) + list(range(len(df), gap_positions)))
    ax.set_yticklabels([""] * gap_positions)
    ax.set_title(
        f"Chronological Timeline of Stays (Arrival Date: {arrival_date_str})",
        fontsize=14,
    )
    ax.set_xlabel("Date", fontsize=12)
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    plt.legend(loc="upper left")

    plt.savefig(output_file, bbox_inches="tight")

    plt.close()
    print(f"Timeline image saved as {output_file}")


# Example data
data = [
    ["01-07-2024", "30-09-2024", "Hohr-Grenzhausen", "Germany"],
    ["01-02-2024", "30-06-2024", "Oslo", "Norway"],
    ["01-08-2023", "31-01-2024", "Oslo", "Norway"],
    ["16-07-2023", "31-07-2023", "Hohr-Grenzhausen", "Germany"],
    ["01-01-2023", "15-07-2023", "Rotterdam", "Netherlands"],
    ["01-09-2022", "31-12-2022", "Bologna", "Italy"],
]

# Arrival date
arrival_date = "01-10-2024"

# Create timeline
create_timeline(data, arrival_date)
