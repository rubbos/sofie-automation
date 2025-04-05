import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from datetime import timedelta
from matplotlib.patches import Rectangle
from typing import Union, List, Dict
from dataclasses import dataclass
from pathlib import Path
from dateutil.relativedelta import relativedelta

import matplotlib
matplotlib.use("Agg")  # Use the non-GUI Agg backend


@dataclass
class TimelineConfig:
    """Configuration settings for timeline visualization."""

    figsize: tuple = (15, 6)
    bar_height: float = 0.3
    base_level: float = 0
    date_format: str = "%d-%m-%Y"
    required_columns: tuple = ("Startdatum", "Einddatum", "Stad", "Land")


class TimelineVisualizer:
    """Class to handle timeline visualization of location stays."""

    def __init__(self, config: TimelineConfig = None):
        self.config = config or TimelineConfig()

    def _validate_data(self, df: pd.DataFrame) -> None:
        """Validate that DataFrame contains required columns."""
        missing_columns = [
            col for col in self.config.required_columns if col not in df.columns
        ]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

    def _prepare_dataframe(
        self,
        data: Union[List[Dict], pd.DataFrame],
        timeline_start: pd.Timestamp,
        timeline_end: pd.Timestamp,
        arrival_date: pd.Timestamp,
    ) -> pd.DataFrame:
        """Convert input data to DataFrame and prepare dates."""
        if isinstance(data, list):
            df = (
                pd.DataFrame(data)
                if all(isinstance(item, dict) for item in data)
                else pd.DataFrame(data, columns=self.config.required_columns)
            )
        else:
            df = data.copy()

        self._validate_data(df)

        # Convert dates to datetime
        for col in ["Startdatum", "Einddatum"]:
            df[col] = pd.to_datetime(df[col], format=self.config.date_format)

        # Clip dates to timeline window
        df["Startdatum"] = df["Startdatum"].clip(
            lower=timeline_start, upper=timeline_end
        )
        df["Einddatum"] = df["Einddatum"].clip(
            lower=timeline_start, upper=timeline_end)

        # Filter out periods that are completely outside the window
        df = df[
            ~((df["Startdatum"] > timeline_end) |
              (df["Einddatum"] < timeline_start))
        ]
        return df.sort_values("Startdatum")
    

    def calculate_time_of_stay(self, start, end):
        delta = relativedelta(end, start)
        months = delta.years * 12 + delta.months
        days = delta.days

        month_text = "maand" if months == 1 else "maanden"
        day_text = "dag" if days == 1 else "dagen"

        parts = []
        if months:
            parts.append(f"{months} {month_text}")
        if days:
            parts.append(f"{days} {day_text}")

        return " + ".join(parts) if parts else "0 dagen"

    # makes a readable list for users instead of visuals
    def location_table_24_months(self, *arg, **kwargs) -> str:
        df = self._prepare_dataframe(*arg, **kwargs)
        gaps = self._calculate_gaps(df, *arg[1:3])
        date_format = self.config.date_format

        locations = []
        for index, row in df.iterrows():
            time_of_stay = self.calculate_time_of_stay(row[0], row[1])
            location = (
                f"{row[0].strftime(date_format)} t/m {row[1].strftime(date_format)} in {row[2]}, {row[3]} ({time_of_stay}).")
            locations.append(location)

        arrival_gap = self.arrival_date_in_gap(gaps, *arg[2:4])
        if arrival_gap is not None:
            locations.append(arrival_gap)

        if gaps:
            locations.append("Ontbrekende periode(s):")
            for i, (gap_start, gap_end) in enumerate(gaps):
                time_of_stay = self.calculate_time_of_stay(gap_start, gap_end)
                gap = f"{gap_start.strftime(date_format)} t/m {gap_end.strftime(date_format)} in ???, ??? ({time_of_stay})."
                locations.append(gap)
        return "<br>".join(locations)

    def arrival_date_in_gap(
        self, gaps: list, timeline_end: pd.Timestamp, arrival_date: pd.Timestamp
    ) -> str:
        """Check if arrival date falls within any gap."""
        arrival_date = pd.to_datetime(arrival_date)  
        for i, (gap_start, gap_end) in enumerate(gaps):
            if gap_start <= arrival_date <= gap_end:
                time_of_stay = self.calculate_time_of_stay(gap_start, gap_end)
                return f"{arrival_date.strftime('%d-%m-%Y')} t/m {gap_end.strftime('%d-%m-%Y')} in Nederland ({time_of_stay})."
        return None

    def _calculate_gaps(
        self, df: pd.DataFrame, timeline_start: pd.Timestamp, timeline_end: pd.Timestamp
    ) -> List[tuple]:
        """Calculate gaps in the timeline."""
        gaps = []

        # Check start gap
        if df.empty:
            return [(timeline_start, timeline_end)]

        if df["Startdatum"].iloc[0] > timeline_start:
            gaps.append(
                (timeline_start, df["Startdatum"].iloc[0] - timedelta(days=1)))

        # Check intermediate gaps
        for i in range(len(df) - 1):
            current_end = df["Einddatum"].iloc[i]
            next_start = df["Startdatum"].iloc[i + 1]
            if (next_start - current_end).days > 1:
                gaps.append(
                    (current_end + timedelta(days=1),
                     next_start - timedelta(days=1))
                )

        # Check end gap
        if df["Einddatum"].iloc[-1] < timeline_end:
            gap_days = (timeline_end - df["Einddatum"].iloc[-1]).days
            if gap_days > 1:  # Changed from > 0 to > 1
                gaps.append(
                    (
                        df["Einddatum"].iloc[-1] + timedelta(days=1),
                        timeline_end - timedelta(days=1),
                    )
                )

        return gaps

    def _plot_stays(self, ax: plt.Axes, df: pd.DataFrame) -> None:
        """Plot the stays on the timeline."""
        colors = plt.cm.Pastel1(np.linspace(0, 1, len(df)))

        for idx, row in df.iterrows():
            start_num = mdates.date2num(row["Startdatum"])
            end_num = mdates.date2num(row["Einddatum"])
            width = end_num - start_num

            # Only plot if width is positive (end date after start date)
            if width > 0:
                # Plot stay rectangle
                rect = Rectangle(
                    (start_num, self.config.base_level - self.config.bar_height / 2),
                    width,
                    self.config.bar_height,
                    facecolor=colors[idx % len(colors)],
                    edgecolor="none",
                    alpha=0.7,
                )
                ax.add_patch(rect)

                # Add location label
                location = f"{row['Stad']}, {row['Land']}"
                self._add_text(
                    ax,
                    start_num + width / 2,
                    self.config.base_level + self.config.bar_height / 2 - 0.25,
                    location,
                    rotation=45,
                    fontsize=9,
                    fontweight="bold",
                )

                # Add date labels with small offset to prevent overlap
                self._add_text(
                    ax,
                    start_num,
                    self.config.base_level - self.config.bar_height / 2 - 0.15,
                    row["Startdatum"].strftime("%d-%b-%Y"),
                    rotation=45,
                    fontsize=8,
                    ha="left",
                )

                self._add_text(
                    ax,
                    end_num,
                    self.config.base_level - self.config.bar_height / 2 - 0.15,
                    row["Einddatum"].strftime("%d-%b-%Y"),
                    rotation=45,
                    fontsize=8,
                    ha="right",
                )

    def _plot_gaps(self, ax: plt.Axes, gaps: List[tuple]) -> float:
        """Plot timeline gaps and return maximum y position used."""
        max_y = self.config.base_level + self.config.bar_height

        for i, (gap_start, gap_end) in enumerate(gaps):
            # Plot gap line
            ax.hlines(
                self.config.base_level,
                gap_start,
                gap_end,
                colors="red",
                linestyles="--",
                linewidth=2,
                alpha=0.5,
            )

            # Add gap label
            gap_duration = (gap_end - gap_start).days
            gap_label = (
                f"{gap_start.strftime('%d-%b-%Y')} t/m "
                f"{gap_end.strftime('%d-%b-%Y')} ({gap_duration} days)"
            )

            y_pos = max_y + 0.1 + (i * 0.15)
            mid_point = mdates.date2num(gap_start + (gap_end - gap_start) / 2)
            self._add_text(ax, mid_point, y_pos, gap_label,
                           fontsize=8, color="red")

            max_y = max(max_y, y_pos + 0.15)

        return max_y

    @staticmethod
    def _add_text(ax: plt.Axes, x: float, y: float, text: str, **kwargs) -> None:
        """Helper method to add text to the plot with default alignment."""
        defaults = {"ha": "center", "va": "bottom"}
        ax.text(x, y, text, **{**defaults, **kwargs})

    def create_timeline(
        self,
        data: Union[List[Dict], pd.DataFrame],
        ao_start_date_str: str,
        arrival_date_str: str,
        output_file: Union[str, Path] = "timeline_image.png",
    ) -> None:
        """Create and save a timeline visualization."""
        # Calculate timeline boundaries
        ao_start_date = pd.to_datetime(
            ao_start_date_str, format=self.config.date_format
        )
        arrival_date = pd.to_datetime(
            ao_start_date_str, format=self.config.date_format
        )
        timeline_start = ao_start_date - pd.DateOffset(years=2)

        # Prepare data with timeline boundaries
        df = self._prepare_dataframe(data, timeline_start, ao_start_date, arrival_date)

        # Filter data to exact 2-year window
        df = df[df["Einddatum"] >= timeline_start].copy()

        # Create figure
        fig, ax = plt.subplots(figsize=self.config.figsize)
        fig.patch.set_facecolor("white")

        # Calculate gaps and plot elements
        gaps = self._calculate_gaps(df, timeline_start, ao_start_date)
        self._plot_stays(ax, df)
        max_y = self._plot_gaps(ax, gaps)

        # Add timeline boundaries
        for date, label in [
            (timeline_start, "Timeline Start"),
            (ao_start_date, "Timeline Einde"),
        ]:
            ax.axvline(x=mdates.date2num(date), color="black",
                       linestyle="-", alpha=0.3)
            self._add_text(
                ax,
                mdates.date2num(date),
                -0.4,
                f"{label}\n{date.strftime('%d-%b-%Y')}",
                fontsize=8,
                va="top",
            )

        # Configure axes
        ax.set_xlim(
            mdates.date2num(timeline_start - timedelta(days=30)),
            mdates.date2num(ao_start_date + timedelta(days=30)),
        )
        ax.set_ylim(-0.5, max_y + 0.1)

        # Format x-axis
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        plt.xticks(rotation=45)

        # Clean up plot
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="x", linestyle="--", alpha=0.3)

        # Add title
        plt.title(
            "Timeline 24 maanden voor aanvang tewerkstelling",
            pad=20,
            fontsize=12,
            fontweight="bold",
        )

        # Save plot
        plt.tight_layout()
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, bbox_inches="tight", dpi=100)
        plt.close()
