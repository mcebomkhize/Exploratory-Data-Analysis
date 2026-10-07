# Customer Feedback Exploratory Data Analysis

This script summarizes a cleaned customer-feedback CSV and creates charts for
the overall rating, city comparisons, rating distribution, and written-feedback
coverage. The dataset is not included; point the script at your local CSV file.

## Setup

Install the Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run

The default column names are `City`, `Rating`, and `Feedback`:

```powershell
python customer_feedback_eda.py .\customer_feedback.csv
```

If your CSV uses different headers, provide them explicitly:

```powershell
python customer_feedback_eda.py .\customer_feedback.csv `
  --city-column Location --rating-column Score --feedback-column Comment `
  --output-dir .\eda_output
```

The output directory contains `summary.json` and four PNG charts. The summary
reports record counts by city, average rating overall and by city, the rating
distribution, and the count and percentage of records with nonblank written
feedback. Rows with missing city values are grouped under `(Missing)`. Ratings
that cannot be parsed as numbers are excluded from rating averages and the
rating distribution, but remain included in record counts and the written
feedback percentage.

## Tests

Run the focused tests with:

```powershell
python -m unittest discover -s tests
```
