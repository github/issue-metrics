"""This module provides unit tests for the time_to_answer module."""

import unittest
from datetime import timedelta
from typing import List

from classes import IssueWithMetrics
from time_to_answer import get_average_time_to_answer, measure_time_to_answer


class TestGetAverageTimeToAnswer(unittest.TestCase):
    """A test case for the get_average_time_to_answer function.

    This test case includes three test methods:
    - test_returns_none_for_empty_list
    - test_returns_none_for_list_with_no_time_to_answer
    - test_returns_average_time_to_answer
    """

    def test_returns_none_for_empty_list(self):
        """Tests that the function returns None when given an empty list of issues."""
        # Arrange
        issues_with_metrics: List[IssueWithMetrics] = []

        # Act
        result = get_average_time_to_answer(issues_with_metrics)

        # Assert
        self.assertIsNone(result)

    def test_returns_none_for_list_with_no_time_to_answer(self):
        """
        Tests that the function returns None when given a list of
        issues with no time to answer.
        """
        # Arrange
        issues_with_metrics = [
            IssueWithMetrics("issue1", None, None),
            IssueWithMetrics("issue2", None, None),
        ]

        # Act
        result = get_average_time_to_answer(issues_with_metrics)

        # Assert
        self.assertIsNone(result)

    def test_returns_average_time_to_answer(self):
        """
        Tests that the function correctly calculates the average
        time to answer for a list of issues with time to answer.
        """

        # Arrange
        issues_with_metrics = [
            IssueWithMetrics("issue1", "url1", "alice", None, None, timedelta(seconds=10)),
            IssueWithMetrics("issue2", "url2", "bob", None, None, timedelta(seconds=20)),
            IssueWithMetrics("issue3", "url3", "carol", None, None, timedelta(seconds=30)),
        ]

        # Act
        result = get_average_time_to_answer(issues_with_metrics)

        # Assert
        self.assertEqual(result, timedelta(seconds=20))


class TestMeasureTimeToAnswer(unittest.TestCase):
    """A test case for the measure_time_to_answer function.

    This test case includes three test methods:
    - test_returns_none_if_answer_chosen_at_is_missing
    - test_returns_none_if_created_at_is_missing
    - test_returns_time_to_answer
    """

    def test_returns_none_if_answer_chosen_at_is_missing(self):
        """
        Tests that the function returns None when the answerChosenAt
        field is missing from the discussion object.
        """
        # Arrange
        discussion = {"createdAt": "2022-01-01T00:00:00Z", "answerChosenAt": None}

        # Act
        result = measure_time_to_answer(discussion)

        # Assert
        self.assertIsNone(result)

    def test_returns_none_if_created_at_is_missing(self):
        """
        Tests that the function returns None when the createdAt
        field is missing from the discussion object.
        """
        # Arrange
        discussion = {"createdAt": None, "answerChosenAt": "2022-01-01T00:00:00Z"}

        # Act
        result = measure_time_to_answer(discussion)

        # Assert
        self.assertIsNone(result)

    def test_returns_time_to_answer(self):
        """
        Tests that the function correctly calculates the time to answer for
        a discussion object with both createdAt and answerChosenAt fields.
        """
        # Arrange
        discussion = {
            "createdAt": "2022-01-01T00:00:00Z",
            "answerChosenAt": "2022-01-01T00:01:00Z",
        }

        # Act
        result = measure_time_to_answer(discussion)

        # Assert
        self.assertEqual(result, timedelta(minutes=1))
