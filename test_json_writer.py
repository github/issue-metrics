"""Tests for the write_to_json function in json_writer.py."""

import json
import unittest
from datetime import timedelta
from classes import IssueWithMetrics
from json_writer import write_to_json


class TestWriteToJson(unittest.TestCase):
    """Tests for the write_to_json function."""

    def test_write_to_json(self):
        """Test that write_to_json writes the correct JSON file."""
        issues_with_metrics = [
            IssueWithMetrics(
                title="Issue 1",
                html_url="https://github.com/owner/repo/issues/1",
                author="alice",
                time_to_first_response=timedelta(days=3),
                time_to_close=timedelta(days=6),
                time_to_answer=None,
                labels_metrics={
                    "bug": timedelta(days=1, hours=16, minutes=24, seconds=12)
                },
            ),
            IssueWithMetrics(
                title="Issue 2",
                html_url="https://github.com/owner/repo/issues/2",
                author="bob",
                time_to_first_response=timedelta(days=2),
                time_to_close=timedelta(days=4),
                time_to_answer=timedelta(days=1),
                labels_metrics={},
            ),
        ]
        average_time_to_first_response = timedelta(days=2.5)
        average_time_to_close = timedelta(days=5)
        average_time_to_answer = timedelta(days=1)
        num_issues_opened = 2
        num_issues_closed = 1

        expected_output = {
            "average_time_to_first_response": "2 days, 12:00:00",
            "average_time_to_close": "5 days, 0:00:00",
            "average_time_to_answer": "1 day, 0:00:00",
            "average_time_in_labels": {"bug": "1 day, 16:24:12"},
            "num_items_opened": 2,
            "num_items_closed": 1,
            "total_item_count": 2,
            "issues": [
                {
                    "title": "Issue 1",
                    "html_url": "https://github.com/owner/repo/issues/1",
                    "author": "alice",
                    "time_to_first_response": "3 days, 0:00:00",
                    "time_to_close": "6 days, 0:00:00",
                    "time_to_answer": "None",
                    "label_metrics": {"bug": "1 day, 16:24:12"},
                },
                {
                    "title": "Issue 2",
                    "html_url": "https://github.com/owner/repo/issues/2",
                    "author": "bob",
                    "time_to_first_response": "2 days, 0:00:00",
                    "time_to_close": "4 days, 0:00:00",
                    "time_to_answer": "1 day, 0:00:00",
                    "label_metrics": {},
                },
            ],
            "search_query": "is:issue repo:owner/repo",
        }

        # Call the function and check the output
        self.assertEqual(
            write_to_json(
                issues_with_metrics=issues_with_metrics,
                average_time_to_first_response=average_time_to_first_response,
                average_time_to_close=average_time_to_close,
                average_time_to_answer=average_time_to_answer,
                average_time_in_labels={
                    "bug": timedelta(days=1, hours=16, minutes=24, seconds=12)
                },
                num_issues_opened=num_issues_opened,
                num_issues_closed=num_issues_closed,
                search_query="is:issue repo:owner/repo",
            ),
            json.dumps(expected_output),
        )


if __name__ == "__main__":
    unittest.main()
