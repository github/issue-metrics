"""A module containing unit tests for the time_to_first_response module.

This module contains unit tests for the measure_time_to_first_response and
get_average_time_to_first_response functions in the time_to_first_response module.
The tests use mock GitHub issues and comments to test the functions' behavior.

Classes:
    TestMeasureTimeToFirstResponse: A class to test the measure_time_to_first_response function.
    TestGetAverageTimeToFirstResponse: A class to test the
        get_average_time_to_first_response function.

"""
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from classes import IssueWithMetrics
from time_to_first_response import (
    get_average_time_to_first_response,
    measure_time_to_first_response,
)


class TestMeasureTimeToFirstResponse(unittest.TestCase):
    """Test the measure_time_to_first_response function."""

    def test_measure_time_to_first_response(self):
        """Test that measure_time_to_first_response calculates the correct time.

        This test mocks the GitHub connection and issue comments, and checks that
        measure_time_to_first_response calculates the correct time to first response.

        """
        # Set up the mock GitHub issues
        mock_issue1 = MagicMock()
        mock_issue1.comments = 1
        mock_issue1.created_at = "2023-01-01T00:00:00Z"

        mock_comment1 = MagicMock()
        mock_comment1.created_at = datetime.fromisoformat("2023-01-02T00:00:00Z")
        mock_issue1.issue.comments.return_value = [mock_comment1]

        # Call the function
        result = measure_time_to_first_response(mock_issue1, None)
        expected_result = timedelta(days=1)

        # Check the results
        self.assertEqual(result, expected_result)

    def test_measure_time_to_first_response_no_comments(self):
        """Test that measure_time_to_first_response returns empty for an issue with no comments."""
        # Set up mock issues with no comments
        mock_issue1 = MagicMock()
        mock_issue1.comments = 0
        mock_issue1.created_at = "2023-01-01T00:00:00Z"

        # Call the function
        result = measure_time_to_first_response(mock_issue1, None)
        expected_result = None

        # Check the results
        self.assertEqual(result, expected_result)

    def test_measure_time_to_first_response_ignore_users(self):
        """Test that measure_time_to_first_response ignores comments from ignored users."""
        # Set up the mock GitHub issues
        mock_issue1 = MagicMock()
        mock_issue1.comments = 1
        mock_issue1.created_at = "2023-01-01T00:00:00Z"

        # Set up the mock GitHub comments (one ignored, one not ignored)
        mock_comment1 = MagicMock()
        mock_comment1.user.login = "ignored_user"
        mock_comment1.created_at = datetime.fromisoformat("2023-01-02T00:00:00Z")

        mock_comment2 = MagicMock()
        mock_comment2.user.login = "not_ignored_user"
        mock_comment2.created_at = datetime.fromisoformat("2023-01-03T00:00:00Z")

        mock_issue1.issue.comments.return_value = [mock_comment1, mock_comment2]

        # Call the function
        result = measure_time_to_first_response(mock_issue1, None, ["ignored_user"])
        expected_result = timedelta(days=2)

        # Check the results
        self.assertEqual(result, expected_result)


class TestGetAverageTimeToFirstResponse(unittest.TestCase):
    """Test the get_average_time_to_first_response function."""

    def test_get_average_time_to_first_response(self):
        """Test that get_average_time_to_first_response calculates the correct average.

        This test creates a list of mock GitHub issues with time to first response
        attributes, calls get_average_time_to_first_response with the list, and
        checks that the function returns the correct average time to first response.

        """
        # Create mock data
        issues_with_metrics = [
            IssueWithMetrics(
                "Issue 1", "https://github.com/user/repo/issues/1", timedelta(days=1)
            ),
            IssueWithMetrics(
                "Issue 2", "https://github.com/user/repo/issues/2", timedelta(days=2)
            ),
            IssueWithMetrics("Issue 3", "https://github.com/user/repo/issues/3", None),
        ]

        # Call the function and check the result
        result = get_average_time_to_first_response(issues_with_metrics)
        expected_result = timedelta(days=1.5)
        self.assertEqual(result, expected_result)
