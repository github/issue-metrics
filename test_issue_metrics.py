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
from unittest.mock import MagicMock, mock_open, patch

import issue_metrics
from issue_metrics import (
    IssueWithMetrics,
    auth_to_github,
    get_average_time_to_close,
    get_average_time_to_first_response,
    get_env_vars,
    get_per_issue_metrics,
    measure_time_to_close,
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

        # Call the function
        result = measure_time_to_first_response(mock_issue1)
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
        result = measure_time_to_first_response(mock_issue1)
        expected_result = None

        # Check the results
        self.assertEqual(result, expected_result)


class TestGetAverageTimeToClose(unittest.TestCase):
    """Test suite for the get_average_time_to_close function."""

    def test_get_average_time_to_close(self):
        """Test that the function correctly calculates the average time to close."""
        # Create mock data
        issues_with_metrics = [
            IssueWithMetrics(
                "Issue 1",
                "https://github.com/user/repo/issues/1",
                None,
                timedelta(days=2),
            ),
            IssueWithMetrics(
                "Issue 2",
                "https://github.com/user/repo/issues/2",
                None,
                timedelta(days=4),
            ),
            IssueWithMetrics(
                "Issue 3", "https://github.com/user/repo/issues/3", None, None
            ),
        ]

        # Call the function and check the result
        result = get_average_time_to_close(issues_with_metrics)
        expected_result = timedelta(days=3)
        self.assertEqual(result, expected_result)

    def test_get_average_time_to_close_no_issues(self):
        """Test that the function returns None if there are no issues with time to close."""
        # Create mock data
        issues_with_metrics = [
            IssueWithMetrics(
                "Issue 1", "https://github.com/user/repo/issues/1", None, None
            ),
            IssueWithMetrics(
                "Issue 2", "https://github.com/user/repo/issues/2", None, None
            ),
            IssueWithMetrics(
                "Issue 3", "https://github.com/user/repo/issues/3", None, None
            ),
        ]

        # Call the function and check the result
        result = get_average_time_to_close(issues_with_metrics)
        expected_result = None
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


class TestMeasureTimeToClose(unittest.TestCase):
    """Test suite for the measure_time_to_close function."""

    def test_measure_time_to_close(self):
        """Test that the function correctly measures the time to close an issue."""
        # Create a mock issue object
        issue = MagicMock()
        issue.state = "closed"
        issue.created_at = "2021-01-01T00:00:00Z"
        issue.closed_at = "2021-01-03T00:00:00Z"

        # Call the function and check the result
        result = measure_time_to_close(issue)
        expected_result = timedelta(days=2)
        self.assertEqual(result, expected_result)

    def test_measure_time_to_close_raises_error(self):
        """Test that the function raises a ValueError if the issue is not closed."""
        # Create a mock issue object
        issue = MagicMock()
        issue.state = "open"

        # Call the function and check that it raises a ValueError
        with self.assertRaises(ValueError):
            measure_time_to_close(issue)


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
            ),
            IssueWithMetrics(
                "Issue 2",
                "https://github.com/user/repo/issues/2",
                timedelta(days=3),
                timedelta(days=4),
            ),
        ]
        average_time_to_first_response = timedelta(days=2)
        average_time_to_close = timedelta(days=3)
        num_issues_opened = 2
        num_issues_closed = 1

        # Call the function
        write_to_markdown(
            issues_with_metrics,
            average_time_to_first_response,
            average_time_to_close,
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
            "| Number of issues that remain open | 2 |\n"
            "| Number of issues closed | 1 |\n"
            "| Total number of issues created | 2 |\n\n"
            "| Title | URL | Time to first response | Time to close \n"
            "| --- | --- | ---: | ---: |\n"
            "| Issue 1 | https://github.com/user/repo/issues/1 | 1 day, 0:00:00 | "
            "2 days, 0:00:00 |\n"
            "| Issue 2 | https://github.com/user/repo/issues/2 | 3 days, 0:00:00 | "
            "4 days, 0:00:00 |\n"
        )
        self.assertEqual(content, expected_content)
        os.remove("issue_metrics.md")

    def test_write_to_markdown_no_issues(self):
        """Test that write_to_markdown writes the correct markdown file when no issues are found."""
        # Call the function with no issues
        with patch("builtins.open", mock_open()) as mock_open_file:
            write_to_markdown([], None, None, 0, 0)

        # Check that the file was written correctly
        expected_output = "no issues found for the given search criteria\n\n"
        mock_open_file.assert_called_once_with(
            "issue_metrics.md", "w", encoding="utf-8"
        )
        mock_open_file().write.assert_called_once_with(expected_output)


class TestGetEnvVars(unittest.TestCase):
    """Test suite for the get_env_vars function."""

    def test_get_env_vars(self):
        """Test that the function correctly retrieves the environment variables."""
        # Set the environment variables
        os.environ["SEARCH_QUERY"] = "is:issue is:open"
        os.environ["REPOSITORY_URL"] = "https://github.com/user/repo"

        # Call the function and check the result
        result = get_env_vars()
        expected_result = ("is:issue is:open", "https://github.com/user/repo")
        self.assertEqual(result, expected_result)

    def test_get_env_vars_missing_query(self):
        """Test that the function raises a ValueError
        if the SEARCH_QUERY environment variable is not set."""
        # Unset the SEARCH_QUERY environment variable
        os.environ.pop("SEARCH_QUERY", None)

        # Call the function and check that it raises a ValueError
        with self.assertRaises(ValueError):
            get_env_vars()

    def test_get_env_vars_missing_url(self):
        """Test that the function raises a ValueError if the
        REPOSITORY_URL environment variable is not set."""
        # Unset the REPOSITORY_URL environment variable
        os.environ.pop("REPOSITORY_URL", None)

        # Call the function and check that it raises a ValueError
        with self.assertRaises(ValueError):
            get_env_vars()


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
            "SEARCH_QUERY": "is:open",
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
            "SEARCH_QUERY": "is:open",
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
        mock_write_to_markdown.assert_called_once_with(None, None, None, None, None)


class TestGetPerIssueMetrics(unittest.TestCase):
    """Test suite for the get_per_issue_metrics function."""

    def test_get_per_issue_metrics(self):
        """Test that the function correctly calculates the metrics for a list of GitHub issues."""
        # Create mock data
        mock_issue1 = MagicMock(
            title="Issue 1",
            html_url="https://github.com/user/repo/issues/1",
            state="open",
            comments=1,
            created_at="2023-01-01T00:00:00Z",
        )

        mock_comment1 = MagicMock()
        mock_comment1.created_at = datetime.fromisoformat("2023-01-02T00:00:00Z")
        mock_issue1.issue.comments.return_value = [mock_comment1]

        mock_issue2 = MagicMock(
            title="Issue 2",
            html_url="https://github.com/user/repo/issues/2",
            state="closed",
            comments=1,
            created_at="2023-01-01T00:00:00Z",
            closed_at="2023-01-04T00:00:00Z",
        )

        mock_comment2 = MagicMock()
        mock_comment2.created_at = datetime.fromisoformat("2023-01-03T00:00:00Z")
        mock_issue2.issue.comments.return_value = [mock_comment2]
        issues = [
            mock_issue1,
            mock_issue2,
        ]

        # Call the function and check the result
        with unittest.mock.patch(
            "issue_metrics.measure_time_to_first_response",
            measure_time_to_first_response,
        ), unittest.mock.patch(
            "issue_metrics.measure_time_to_close", measure_time_to_close
        ):
            (
                result_issues_with_metrics,
                result_num_issues_open,
                result_num_issues_closed,
            ) = get_per_issue_metrics(issues)
        expected_issues_with_metrics = [
            IssueWithMetrics(
                "Issue 1",
                "https://github.com/user/repo/issues/1",
                timedelta(days=1),
                None,
            ),
            IssueWithMetrics(
                "Issue 2",
                "https://github.com/user/repo/issues/2",
                timedelta(days=2),
                timedelta(days=3),
            ),
        ]
        expected_num_issues_open = 1
        expected_num_issues_closed = 1
        self.assertEqual(result_num_issues_open, expected_num_issues_open)
        self.assertEqual(result_num_issues_closed, expected_num_issues_closed)
        self.assertEqual(
            result_issues_with_metrics[0].time_to_first_response,
            expected_issues_with_metrics[0].time_to_first_response,
        )
        self.assertEqual(
            result_issues_with_metrics[0].time_to_close,
            expected_issues_with_metrics[0].time_to_close,
        )
        self.assertEqual(
            result_issues_with_metrics[1].time_to_first_response,
            expected_issues_with_metrics[1].time_to_first_response,
        )
        self.assertEqual(
            result_issues_with_metrics[1].time_to_close,
            expected_issues_with_metrics[1].time_to_close,
        )


if __name__ == "__main__":
    unittest.main()
