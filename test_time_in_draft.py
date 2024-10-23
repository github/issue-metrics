"""A test suite for the measure_time_in_draft function."""

import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytz
from time_in_draft import measure_time_in_draft


class TestMeasureTimeInDraft(unittest.TestCase):
    """
    Unit tests for the measure_time_in_draft function.
    """

    def setUp(self):
        """
        Setup common test data and mocks.
        """
        self.issue = MagicMock()
        self.issue.issue.events.return_value = [
            MagicMock(
                event="created_at", created_at=datetime(2021, 1, 1, tzinfo=pytz.utc)
            ),
            MagicMock(
                event="other_event", created_at=datetime(2021, 1, 2, tzinfo=pytz.utc)
            ),
        ]

    def test_time_in_draft_with_ready_for_review(self):
        """
        Test measure_time_in_draft when ready_for_review_at is provided.
        """
        ready_for_review_at = datetime(2021, 1, 3, tzinfo=pytz.utc)
        result = measure_time_in_draft(self.issue, ready_for_review_at)
        expected = timedelta(days=2)
        self.assertEqual(result, expected, "The time in draft should be 2 days.")

    def test_time_in_draft_without_ready_for_review(self):
        """
        Test measure_time_in_draft when ready_for_review_at is not provided.
        """
        now = datetime(2021, 1, 4, tzinfo=pytz.utc)
        with unittest.mock.patch("time_in_draft.datetime") as mock_datetime:
            mock_datetime.now.return_value = now
            result = measure_time_in_draft(self.issue, None)
            expected = timedelta(days=3)
            self.assertEqual(result, expected, "The time in draft should be 3 days.")

    def test_time_in_draft_with_no_events(self):
        """
        Test measure_time_in_draft when there are no events.
        """
        self.issue.issue.events.return_value = []
        result = measure_time_in_draft(self.issue, None)
        self.assertIsNone(result, "The result should be None when there are no events.")


if __name__ == "__main__":
    unittest.main()
