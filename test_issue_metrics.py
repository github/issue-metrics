"""Unit tests for the issue_metrics module.

This module contains unit tests for the functions in the issue_metrics module.
The tests use the unittest module and the unittest.mock module to mock the
GitHub API and test the functions in isolation.

Classes:
    TestSearchIssues: A class containing unit tests for the search_issues function.
    TestMeasureTimeToFirstResponse: A class containing unit tests for the
        measure_time_to_first_response function.
    TestGetAverageTimeToFirstResponse: A class containing unit tests for the
        get_average_time_to_first_response function.
    TestWriteToMarkdown: A class containing unit tests for the write_to_markdown function.
"""
import os
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import issue_metrics
from issue_metrics import (
    auth_to_github,
    get_average_time_to_first_response,
    measure_time_to_first_response,
    search_issues,
    write_to_markdown,
)


class TestSearchIssues(unittest.TestCase):
    """Unit tests for the search_issues function.

    This class contains unit tests for the search_issues function in the
    issue_metrics module. The tests use the unittest module and the unittest.mock
    module to mock the GitHub API and test the function in isolation.

    Methods:
        test_search_issues: Test that search_issues returns the correct issues.

    """

    @patch("issue_metrics.urlparse")
    def test_search_issues(self, mock_urlparse):
        """Test that search_issues returns the correct issues."""
        # Set up the mock GitHub connection object
        mock_connection = MagicMock()
        mock_issues = [
            MagicMock(title="Issue 1"),
            MagicMock(title="Issue 2"),
        ]
        mock_connection.search_issues.return_value = mock_issues

        # Set up the mock urlparse function
        mock_urlparse.return_value.path = "/user/repo"

        # Call search_issues and check that it returns the correct issues
        issues = search_issues(
            "https://github.com/user/repo", "is:open", mock_connection
        )
        self.assertEqual(issues, mock_issues)


class TestAuthToGithub(unittest.TestCase):
    """Test the auth_to_github function."""

    @patch("github3.login")
    def test_auth_to_github_with_token(self, mock_login):
        """Test that auth_to_github works with a token.

        This test sets the GH_TOKEN environment variable and checks that
        auth_to_github returns the expected GitHub connection.

        """

        # Set up the mock GitHub connection
        mock_gh = MagicMock()
        mock_login.return_value = mock_gh

        # Set up the environment variable
        os.environ["GH_TOKEN"] = "test_token"

        # Call the function
        github_connection = auth_to_github()

        # Check the results
        self.assertEqual(github_connection, mock_gh)
        mock_login.assert_called_once_with(token="test_token")

    def test_auth_to_github_no_token(self):
        """Test that auth_to_github raises a ValueError if GH_TOKEN is not set."""
        # Unset the GH_TOKEN environment variable
        if "GH_TOKEN" in os.environ:
            del os.environ["GH_TOKEN"]

        # Call auth_to_github and check that it raises a ValueError
        with self.assertRaises(ValueError):
            issue_metrics.auth_to_github()


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

        mock_issue2 = MagicMock()
        mock_issue2.comments = 1
        mock_issue2.created_at = "2023-01-03T00:00:00Z"

        mock_comment2 = MagicMock()
        mock_comment2.created_at = datetime.fromisoformat("2023-01-04T00:00:00Z")
        mock_issue2.issue.comments.return_value = [mock_comment2]

        mock_issues = [mock_issue1, mock_issue2]

        # Call the function
        issues_with_metrics = measure_time_to_first_response(mock_issues)

        # Check the results
        self.assertEqual(len(issues_with_metrics), 2)
        self.assertEqual(issues_with_metrics[0][2], timedelta(days=1))
        self.assertEqual(issues_with_metrics[1][2], timedelta(days=1))

    def test_measure_time_to_first_response_no_comments(self):
        """Test that measure_time_to_first_response returns empty for an issue with no comments."""
        # Set up mock issues with no comments
        mock_issue1 = MagicMock(
            comments=0,
            created_at="2023-01-01T00:00:00Z",
        )

        mock_issue2 = MagicMock(
            comments=0,
            created_at="2023-01-01T00:00:00Z",
        )

        mock_issues = [mock_issue1, mock_issue2]

        # Call measure_time_to_first_response and check that it returns None
        time_to_first_response = issue_metrics.measure_time_to_first_response(
            mock_issues
        )

        self.assertEqual(len(time_to_first_response), 2)
        self.assertEqual(time_to_first_response[0][2], None)
        self.assertEqual(time_to_first_response[1][2], None)


class TestGetAverageTimeToFirstResponse(unittest.TestCase):
    """Test the get_average_time_to_first_response function."""

    def test_get_average_time_to_first_response(self):
        """Test that get_average_time_to_first_response calculates the correct average.

        This test creates a list of mock GitHub issues with time to first response
        attributes, calls get_average_time_to_first_response with the list, and
        checks that the function returns the correct average time to first response.

        """
        # Create a list of mock GitHub issues with time to first response attributes
        issues = [
            [
                "Title 1",
                "https://github.com/owner/repo1",
                timedelta(days=1, hours=2, minutes=30),
            ],
            [
                "Title 2",
                "https://github.com/owner/repo2",
                timedelta(days=3, hours=4, minutes=30),
            ],
            ["Title 3", "https://github.com/owner/repo3", timedelta(minutes=30)],
        ]

        # Call get_average_time_to_first_response with the list of issues
        average_time_to_first_response = get_average_time_to_first_response(issues)

        # Check that the function returns the correct average time to first response
        expected_average_time_to_first_response = timedelta(
            days=1, hours=10, minutes=30
        )
        self.assertEqual(
            average_time_to_first_response, expected_average_time_to_first_response
        )


class TestGetNumberOfIssuesOpened(unittest.TestCase):
    """Test case class for the get_number_of_issues_opened function in the issue_metrics module.

    This class contains test cases for the get_number_of_issues_opened function,
        which calculates the number of open issues in a list of GitHub issues.

    """

    def test_get_number_of_issues_opened(self):
        """Test that get_number_of_issues_opened returns the correct number of open issues."""
        # Set up the mock issues
        mock_issues = [
            MagicMock(state="open"),
            MagicMock(state="closed"),
            MagicMock(state="open"),
        ]

        # Call get_number_of_issues_opened and check that it returns the
        # correct number of open issues
        num_issues_opened = issue_metrics.get_number_of_issues_open(mock_issues)
        self.assertEqual(num_issues_opened, 2)


class TestGetNumberOfIssuesClosed(unittest.TestCase):
    """Test case class for the get_number_of_issues_closeded function in the issue_metrics module.

    This class contains test cases for the get_number_of_issues_closed function,
        which calculates the number of open issues in a list of GitHub issues.

    """

    def test_get_number_of_issues_closed(self):
        """Test that get_number_of_issues_closed returns the correct number of closed issues."""
        # Set up the mock issues
        mock_issues = [
            MagicMock(state="open"),
            MagicMock(state="closed"),
            MagicMock(state="open"),
        ]

        # Call get_number_of_issues_opened and check that it returns the
        # correct number of open issues
        num_issues_closed = issue_metrics.get_number_of_issues_closed(mock_issues)
        self.assertEqual(num_issues_closed, 1)


class TestWriteToMarkdown(unittest.TestCase):
    """Test the write_to_markdown function."""

    def test_write_to_markdown(self):
        """Test that write_to_markdown writes the correct markdown file.

        This test creates a list of mock GitHub issues with time to first response
        attributes, calls write_to_markdown with the list and the average time to
        first response, and checks that the function writes the correct markdown
        file.

        """
        # Create a list of mock GitHub issues with time to first response attributes
        issues_with_metrics = [
            (
                "Issue 1",
                "https://github.com/user/repo/issues/1",
                timedelta(days=1, hours=2, minutes=30),
            ),
            (
                "Issue 2",
                "https://github.com/user/repo/issues/2",
                timedelta(days=3, hours=4, minutes=30),
            ),
            ("Issue 3", "https://github.com/user/repo/issues/3", timedelta(minutes=30)),
        ]

        # Call write_to_markdown with the list of issues and the average time to first response
        average_time_to_first_response = timedelta(days=1, hours=3, minutes=10)
        num_issues_open = 1
        num_issues_closed = 2

        write_to_markdown(
            issues_with_metrics,
            average_time_to_first_response,
            num_issues_open,
            num_issues_closed,
            file=None,
        )

        # Check that the function writes the correct markdown file
        with open("issue_metrics.md", "r", encoding="utf-8") as file:
            content = file.read()
        expected_content = (
            "# Issue Metrics\n\n"
            "Average time to first response: 1 day, 3:10:00\n"
            "Number of issues that remain open: 1\n"
            "Number of issues closed: 2\n"
            "Total number of issues created: 3\n\n"
            "| Title | URL | TTFR |\n"
            "| --- | --- | ---: |\n"
            "| Issue 3 | https://github.com/user/repo/issues/3 | 0:30:00 |\n"
            "| Issue 2 | https://github.com/user/repo/issues/2 | 3 days, 4:30:00 |\n"
            "| Issue 1 | https://github.com/user/repo/issues/1 | 1 day, 2:30:00 |\n"
        )
        self.assertEqual(content, expected_content)


class TestMain(unittest.TestCase):
    """Unit tests for the main function.

    This class contains unit tests for the main function in the issue_metrics
    module. The tests use the unittest module and the unittest.mock module to
    mock the GitHub API and test the function in isolation.

    Methods:
        test_main: Test that main runs without errors.
        test_main_no_issues_found: Test that main handles when no issues are found

    """

    @patch("issue_metrics.auth_to_github")
    @patch("issue_metrics.search_issues")
    @patch("issue_metrics.measure_time_to_first_response")
    @patch("issue_metrics.get_average_time_to_first_response")
    @patch.dict(
        os.environ,
        {
            "ISSUE_SEARCH_QUERY": "is:open",
            "REPOSITORY_URL": "https://github.com/user/repo",
        },
    )
    def test_main(
        self,
        mock_get_average_time_to_first_response,
        mock_measure_time_to_first_response,
        mock_search_issues,
        mock_auth_to_github,
    ):
        """Test that main runs without errors."""
        # Set up the mock GitHub connection object
        mock_connection = MagicMock()
        mock_auth_to_github.return_value = mock_connection

        # Set up the mock search_issues function
        mock_issues = MagicMock(
            items=[
                MagicMock(title="Issue 1"),
                MagicMock(title="Issue 2"),
            ]
        )

        mock_search_issues.return_value = mock_issues

        # Set up the mock measure_time_to_first_response function
        mock_issues_with_ttfr = [
            (
                "Issue 1",
                "https://github.com/user/repo/issues/1",
                timedelta(days=1, hours=2, minutes=30),
            ),
            (
                "Issue 2",
                "https://github.com/user/repo/issues/2",
                timedelta(days=3, hours=4, minutes=30),
            ),
        ]
        mock_measure_time_to_first_response.return_value = mock_issues_with_ttfr

        # Set up the mock get_average_time_to_first_response function
        mock_average_time_to_first_response = 15
        mock_get_average_time_to_first_response.return_value = (
            mock_average_time_to_first_response
        )

        # Call main and check that it runs without errors
        issue_metrics.main()

        # Remove the markdown file created by main
        os.remove("issue_metrics.md")

    @patch("issue_metrics.auth_to_github")
    @patch("issue_metrics.search_issues")
    @patch("issue_metrics.write_to_markdown")
    @patch.dict(
        os.environ,
        {
            "ISSUE_SEARCH_QUERY": "is:open",
            "REPOSITORY_URL": "https://github.com/user/repo",
        },
    )
    def test_main_no_issues_found(
        self,
        mock_write_to_markdown,
        mock_search_issues,
        mock_auth_to_github,
    ):
        """Test that main writes 'No issues found' to the
        console and calls write_to_markdown with None."""

        # Set up the mock GitHub connection object
        mock_connection = MagicMock()
        mock_auth_to_github.return_value = mock_connection

        # Set up the mock search_issues function to return an empty list of issues
        mock_issues = MagicMock(items=[])
        mock_search_issues.return_value = mock_issues

        # Call main and check that it writes 'No issues found'
        issue_metrics.main()
        mock_write_to_markdown.assert_called_once_with(None, None, None, None)


if __name__ == "__main__":
    unittest.main()
