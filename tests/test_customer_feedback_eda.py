import unittest

import pandas as pd

from customer_feedback_eda import analyze_feedback


class AnalyzeFeedbackTests(unittest.TestCase):
    def test_summarizes_ratings_cities_and_written_feedback(self):
        data = pd.DataFrame(
            {
                "City": ["Auckland", "Wellington", "Auckland", None],
                "Rating": ["5", "3", "invalid", "4"],
                "Feedback": [" Great ", "   ", None, "Helpful"],
            }
        )

        result = analyze_feedback(data, "City", "Rating", "Feedback")

        self.assertEqual(result["total_records"], 4)
        self.assertEqual(result["overall_average_rating"], 4.0)
        self.assertEqual(result["records_with_valid_rating"], 3)
        self.assertEqual(
            result["records_per_city"],
            [
                {"city": "(Missing)", "records": 1},
                {"city": "Auckland", "records": 2},
                {"city": "Wellington", "records": 1},
            ],
        )
        self.assertEqual(result["written_feedback_records"], 2)
        self.assertEqual(result["written_feedback_percentage"], 50.0)
        self.assertEqual(
            result["rating_distribution"],
            [
                {"rating": 3.0, "records": 1},
                {"rating": 4.0, "records": 1},
                {"rating": 5.0, "records": 1},
            ],
        )

    def test_rejects_missing_required_columns(self):
        with self.assertRaisesRegex(ValueError, "Required column"):
            analyze_feedback(pd.DataFrame({"City": []}), "City", "Rating", "Feedback")

    def test_rejects_empty_dataset(self):
        data = pd.DataFrame(columns=["City", "Rating", "Feedback"])

        with self.assertRaisesRegex(ValueError, "contains no records"):
            analyze_feedback(data, "City", "Rating", "Feedback")


if __name__ == "__main__":
    unittest.main()
