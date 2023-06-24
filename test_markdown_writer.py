"""A module containing unit tests for the write_to_markdown function in the markdown_writer module.

Classes:
    TestWriteToMarkdown: A class to test the write_to_markdown function with mock data.

"""
import os
import unittest
from datetime import timedelta
from unittest.mock import mock_open, patch

from classes import IssueWithMetrics
from markdown_writer import write_to_markdown


class TestWriteToMarkdown(unittest.TestCase):
    """Test the write_to_markdown function."""

    def test_write_to_markdown(self):
        """Test that write_to_markdown writes the correct markdown file.

        This test creates a list of mock GitHub issues with time to first response
        attributes, calls write_to_markdown with the list and the average time to
        first response, time to close and checks that the function writes the correct
        markdown file.

        """
        # Create mock data
        issues_with_metrics = [
            IssueWithMetrics(
                "Issue 1",
                "https://github.com/user/repo/issues/1",
                timedelta(days=1),
                timedelta(days=2),
                timedelta(days=3),
            ),
            IssueWithMetrics(
                "Issue 2",
                "https://github.com/user/repo/issues/2",
                timedelta(days=3),
                timedelta(days=4),
                timedelta(days=5),
            ),
        ]
        average_time_to_first_response = timedelta(days=2)
        average_time_to_close = timedelta(days=3)
        average_time_to_answer = timedelta(days=4)
        num_issues_opened = 2
        num_issues_closed = 1

        # Call the function
        write_to_markdown(
            issues_with_metrics,
            average_time_to_first_response,
            average_time_to_close,
            average_time_to_answer,
            num_issues_opened,
            num_issues_closed,
        )

        # Check that the function writes the correct markdown file
        with open("issue_metrics.md", "r", encoding="utf-8") as file:
            content = file.read()
        expected_content = (
            "# Issue Metrics\n\n"
            "| Metric | Value |\n"
            "| --- | ---: |\n"
            "| Average time to first response | 2 days, 0:00:00 |\n"
            "| Average time to close | 3 days, 0:00:00 |\n"
            "| Average time to answer | 4 days, 0:00:00 |\n"
            "| Number of issues that remain open | 2 |\n"
            "| Number of issues closed | 1 |\n"
            "| Total number of issues created | 2 |\n\n"
            "| Title | URL | Time to first response | Time to close | Time to answer |\n"
            "| --- | --- | ---: | ---: | ---: |\n"
            "| Issue 1 | https://github.com/user/repo/issues/1 | 1 day, 0:00:00 | "
            "2 days, 0:00:00 | 3 days, 0:00:00 |\n"
            "| Issue 2 | https://github.com/user/repo/issues/2 | 3 days, 0:00:00 | "
            "4 days, 0:00:00 | 5 days, 0:00:00 |\n"
        )
        self.assertEqual(content, expected_content)
        os.remove("issue_metrics.md")

    def test_write_to_markdown_no_issues(self):
        """Test that write_to_markdown writes the correct markdown file when no issues are found."""
        # Call the function with no issues
        with patch("builtins.open", mock_open()) as mock_open_file:
            write_to_markdown(None, None, None, None, None, None)

        # Check that the file was written correctly
        expected_output = "no issues found for the given search criteria\n\n"
        mock_open_file.assert_called_once_with(
            "issue_metrics.md", "w", encoding="utf-8"
        )
        mock_open_file().write.assert_called_once_with(expected_output)
