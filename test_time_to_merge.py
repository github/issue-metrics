"""A module containing unit tests for the time_to_merge module.

This module contains unit tests for the measure_time_to_merge
function in the time_to_merge module.
The tests use mock GitHub pull request to test the function's behavior.

Classes:
    TestMeasureTimeToMerge: A class to test the measure_time_to_merge function.

"""
from datetime import timedelta, datetime
import unittest
from unittest.mock import MagicMock

from time_to_merge import measure_time_to_merge


class TestMeasureTimeToMerge(unittest.TestCase):
    """Test suite for the measure_time_to_merge function."""

    def test_measure_time_to_merge_ready_for_review(self):
        """Test that the function correctly measures the time to merge a pull request that was formerly a draft."""
        # Create a mock pull request object
        pull_request = MagicMock()
        pull_request.merged_at = datetime.fromisoformat("2021-01-03T00:00:00Z")
        ready_for_review_at = datetime.fromisoformat("2021-01-01T00:00:00Z")

        # Call the function and check the result
        result = measure_time_to_merge(pull_request, ready_for_review_at)
        expected_result = timedelta(days=2)
        self.assertEqual(result, expected_result)

    def test_measure_time_to_merge_created_at(self):
        """Test that the function correctly measures the time to merge a pull request that was never a draft."""
        # Create a mock pull request object
        pull_request = MagicMock()
        pull_request.merged_at = datetime.fromisoformat("2021-01-03T00:00:00Z")
        pull_request.created_at = datetime.fromisoformat("2021-01-01T00:00:00Z")

        # Call the function and check the result
        result = measure_time_to_merge(pull_request, None)
        expected_result = timedelta(days=2)
        self.assertEqual(result, expected_result)

    def test_measure_time_to_merge_returns_none(self):
        """Test that the function returns None if the pull request is not merged."""
        # Create a mock issue object
        pull_request = MagicMock()
        pull_request.merged_at = None

        # Call the function and check that it returns None
        self.assertEqual(None, measure_time_to_merge(pull_request, None))
