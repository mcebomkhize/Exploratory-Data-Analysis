"""Summarize and visualize a cleaned customer-feedback CSV file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def analyze_feedback(
    data: pd.DataFrame,
    city_column: str,
    rating_column: str,
    feedback_column: str,
) -> dict[str, Any]:
    """Calculate the requested summary metrics from a feedback dataframe."""
    columns = [city_column, rating_column, feedback_column]
    missing_columns = [column for column in columns if column not in data.columns]
    if missing_columns:
        raise ValueError(f"Required column(s) not found: {', '.join(missing_columns)}")
    if data.empty:
        raise ValueError("The input dataset contains no records.")

    ratings = pd.to_numeric(data[rating_column], errors="coerce")
    city_labels = data[city_column].astype("string").fillna("(Missing)")
    city_summary = (
        pd.DataFrame({"city": city_labels, "rating": ratings})
        .groupby("city", sort=True)
        .agg(records=("city", "size"), average_rating=("rating", "mean"))
        .reset_index()
    )

    rating_counts = ratings.dropna().value_counts(sort=False).sort_index()
    feedback_present = data[feedback_column].fillna("").astype(str).str.strip().ne("")
    feedback_count = int(feedback_present.sum())

    return {
        "total_records": int(len(data)),
        "overall_average_rating": (
            float(ratings.mean()) if ratings.notna().any() else None
        ),
        "records_with_valid_rating": int(ratings.notna().sum()),
        "records_per_city": [
            {"city": str(row.city), "records": int(row.records)}
            for row in city_summary.itertuples(index=False)
        ],
        "average_rating_per_city": [
            {
                "city": str(row.city),
                "average_rating": (
                    float(row.average_rating)
                    if pd.notna(row.average_rating)
                    else None
                ),
            }
            for row in city_summary.itertuples(index=False)
        ],
        "rating_distribution": [
            {"rating": float(rating), "records": int(count)}
            for rating, count in rating_counts.items()
        ],
        "written_feedback_records": feedback_count,
        "written_feedback_percentage": float(
            np.divide(feedback_count * 100, len(data))
        ),
    }


def create_visualizations(
    summary: dict[str, Any],
    output_directory: Path,
) -> list[Path]:
    """Save charts for city averages, city counts, ratings, and feedback presence."""
    output_directory.mkdir(parents=True, exist_ok=True)
    chart_paths: list[Path] = []
    city_averages = [
        row for row in summary["average_rating_per_city"]
        if row["average_rating"] is not None
    ]

    fig, ax = plt.subplots(figsize=(9, 5))
    if city_averages:
        labels = [row["city"] for row in city_averages]
        values = [row["average_rating"] for row in city_averages]
        ax.bar(labels, values, color="steelblue")
        ax.set_ylabel("Average rating")
        ax.tick_params(axis="x", labelrotation=35)
    else:
        ax.text(0.5, 0.5, "No valid numeric ratings", ha="center", va="center")
        ax.set_xticks([])
        ax.set_yticks([])
    ax.set_title("Average rating by city")
    fig.tight_layout()
    chart_paths.append(output_directory / "average_rating_by_city.png")
    fig.savefig(chart_paths[-1], dpi=150)
    plt.close(fig)

    city_counts = summary["records_per_city"]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(
        [row["city"] for row in city_counts],
        [row["records"] for row in city_counts],
        color="darkseagreen",
    )
    ax.set_title("Feedback records by city")
    ax.set_ylabel("Number of records")
    ax.tick_params(axis="x", labelrotation=35)
    fig.tight_layout()
    chart_paths.append(output_directory / "records_by_city.png")
    fig.savefig(chart_paths[-1], dpi=150)
    plt.close(fig)

    rating_distribution = summary["rating_distribution"]
    fig, ax = plt.subplots(figsize=(8, 5))
    if rating_distribution:
        ax.bar(
            [row["rating"] for row in rating_distribution],
            [row["records"] for row in rating_distribution],
            color="cornflowerblue",
        )
        ax.set_xlabel("Rating")
        ax.set_ylabel("Number of records")
    else:
        ax.text(0.5, 0.5, "No valid numeric ratings", ha="center", va="center")
        ax.set_xticks([])
        ax.set_yticks([])
    ax.set_title("Rating distribution")
    fig.tight_layout()
    chart_paths.append(output_directory / "rating_distribution.png")
    fig.savefig(chart_paths[-1], dpi=150)
    plt.close(fig)

    feedback_count = summary["written_feedback_records"]
    total_records = summary["total_records"]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(
        ["Written feedback", "No written feedback"],
        [feedback_count, total_records - feedback_count],
        color=["mediumseagreen", "lightgray"],
    )
    ax.set_ylabel("Number of records")
    ax.set_title("Records with written feedback")
    fig.tight_layout()
    chart_paths.append(output_directory / "written_feedback.png")
    fig.savefig(chart_paths[-1], dpi=150)
    plt.close(fig)

    return chart_paths


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize and visualize a customer-feedback CSV dataset."
    )
    parser.add_argument("csv_file", type=Path, help="Path to the cleaned CSV file")
    parser.add_argument(
        "--city-column", default="City", help="City column name (default: City)"
    )
    parser.add_argument(
        "--rating-column", default="Rating", help="Rating column name (default: Rating)"
    )
    parser.add_argument(
        "--feedback-column",
        default="Feedback",
        help="Written-feedback column name (default: Feedback)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("eda_output"),
        help="Directory for the JSON summary and charts (default: eda_output)",
    )
    args = parser.parse_args()

    try:
        data = pd.read_csv(args.csv_file)
        summary = analyze_feedback(
            data,
            city_column=args.city_column,
            rating_column=args.rating_column,
            feedback_column=args.feedback_column,
        )
        args.output_dir.mkdir(parents=True, exist_ok=True)
        summary_path = args.output_dir / "summary.json"
        summary_path.write_text(
            json.dumps(summary, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        chart_paths = create_visualizations(summary, args.output_dir)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    print(f"Total records: {summary['total_records']}")
    print(f"Overall average rating: {summary['overall_average_rating']}")
    print(
        "Records with written feedback: "
        f"{summary['written_feedback_records']} "
        f"({summary['written_feedback_percentage']:.2f}%)"
    )
    print(f"Summary: {summary_path}")
    for chart_path in chart_paths:
        print(f"Chart: {chart_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
