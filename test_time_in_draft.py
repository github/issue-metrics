"""A test suite for the measure_time_in_draft function."""

import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytz
from time_in_draft import get_stats_time_in_draft, measure_time_in_draft


class TestMeasureTimeInDraft(unittest.TestCase):
    """
    Unit tests for the measure_time_in_draft function.
    """

    def setUp(self):
        """
        Setup common test data and mocks.
        """
        self.issue = MagicMock()
        self.issue.issue.state = "open"

    def test_time_in_draft_with_ready_for_review(self):
        """
        Test measure_time_in_draft with one draft and review interval.
        """
        self.issue.events.return_value = [
            MagicMock(event="converted_to_draft", created_at=datetime(2021, 1, 1, tzinfo=pytz.utc)),
            MagicMock(event="ready_for_review", created_at=datetime(2021, 1, 3, tzinfo=pytz.utc)),
        ]
        result = measure_time_in_draft(self.issue)
        expected = timedelta(days=2)
        self.assertEqual(result, expected, "The time in draft should be 2 days.")

    def test_time_in_draft_without_ready_for_review(self):
        """
        Test measure_time_in_draft when ready_for_review_at is not provided and issue is still open.
        """
        self.issue.events.return_value = [
            MagicMock(event="converted_to_draft", created_at=datetime(2021, 1, 1, tzinfo=pytz.utc)),
        ]
        now = datetime(2021, 1, 4, tzinfo=pytz.utc)
        with unittest.mock.patch("time_in_draft.datetime") as mock_datetime:
            mock_datetime.now.return_value = now
            result = measure_time_in_draft(self.issue)
            expected = timedelta(days=3)
            self.assertEqual(result, expected, "The time in draft should be 3 days.")


    def test_time_in_draft_multiple_intervals(self):
        """
        Test measure_time_in_draft with multiple draft intervals.
        """
        self.issue.events.return_value = [
            MagicMock(event="converted_to_draft", created_at=datetime(2021, 1, 1, tzinfo=pytz.utc)),
            MagicMock(event="ready_for_review", created_at=datetime(2021, 1, 3, tzinfo=pytz.utc)),
            MagicMock(event="converted_to_draft", created_at=datetime(2021, 1, 5, tzinfo=pytz.utc)),
            MagicMock(event="ready_for_review", created_at=datetime(2021, 1, 7, tzinfo=pytz.utc)),
        ]
        result = measure_time_in_draft(self.issue)
        expected = timedelta(days=4)
        self.assertEqual(result, expected, "The total time in draft should be 4 days.")

    def test_time_in_draft_ongoing_draft(self):
        """
        Test measure_time_in_draft with an ongoing draft interval.
        """
        self.issue.events.return_value = [
            MagicMock(event="converted_to_draft", created_at=datetime(2021, 1, 1, tzinfo=pytz.utc)),
        ]
        with unittest.mock.patch("time_in_draft.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2021, 1, 4, tzinfo=pytz.utc)
            result = measure_time_in_draft(self.issue)
            expected = timedelta(days=3)
            self.assertEqual(result, expected, "The ongoing draft time should be 3 days.")

    def test_time_in_draft_no_draft_events(self):
        """
        Test measure_time_in_draft with no draft-related events.
        """
        self.issue.events.return_value = []
        result = measure_time_in_draft(self.issue)
        self.assertIsNone(result, "The result should be None when there are no draft events.")

    def test_time_in_draft_without_ready_for_review_and_closed(self):
        """
        Test measure_time_in_draft for a closed issue with an ongoing draft and ready_for_review_at is not provided.
        """
        self.issue.events.return_value = [
            MagicMock(event="converted_to_draft", created_at=datetime(2021, 1, 1, tzinfo=pytz.utc)),
        ]
        self.issue.issue.state = "closed"
        result = measure_time_in_draft(self.issue)
        self.assertIsNone(result, "The result should be None for a closed issue with an ongoing draft.")


class TestGetStatsTimeInDraft(unittest.TestCase):
    """
    Unit tests for the get_stats_time_in_draft function.
    """

    def test_get_stats_time_in_draft_with_data(self):
        """
        Test get_stats_time_in_draft with valid draft times.
        """
        issues = [
            MagicMock(time_in_draft=timedelta(days=1)),
            MagicMock(time_in_draft=timedelta(days=2)),
            MagicMock(time_in_draft=timedelta(days=3)),
        ]

        result = get_stats_time_in_draft(issues)
        expected = {
            "avg": timedelta(days=2),
            "med": timedelta(days=2),
            "90p": timedelta(days=2, seconds=69120),
        }

        self.assertEqual(
            result, expected, "The statistics for time in draft are incorrect."
        )

    def test_get_stats_time_in_draft_no_data(self):
        """
        Test get_stats_time_in_draft with no draft times.
        """
        issues = [
            MagicMock(time_in_draft=None),
            MagicMock(time_in_draft=None),
        ]

        result = get_stats_time_in_draft(issues)
        self.assertIsNone(
            result, "The result should be None when there are no draft times."
        )

    def test_get_stats_time_in_draft_empty_list(self):
        """
        Test get_stats_time_in_draft with an empty list of issues.
        """
        issues = []

        result = get_stats_time_in_draft(issues)
        self.assertIsNone(
            result, "The result should be None when the list of issues is empty."
        )


if __name__ == "__main__":
    unittest.main()
