"""A module containing unit tests for the issue_metrics module.

This module contains unit tests for the functions in the issue_metrics module
that measure and analyze metrics of GitHub issues. The tests use mock GitHub
issues and comments to test the functions' behavior.

Classes:
    TestSearchIssues: A class to test the search_issues function.
    TestAuthToGithub: A class to test the auth_to_github function.
    TestGetPerIssueMetrics: A class to test the get_per_issue_metrics function.
    TestGetEnvVars: A class to test the get_env_vars function.
    TestMain: A class to test the main function.

"""
import os
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import issue_metrics
from issue_metrics import (
    IssueWithMetrics,
    auth_to_github,
    get_env_vars,
    get_per_issue_metrics,
    measure_time_to_close,
    measure_time_to_first_response,
    search_issues,
)


class TestSearchIssues(unittest.TestCase):
    """Unit tests for the search_issues function.

    This class contains unit tests for the search_issues function in the
    issue_metrics module. The tests use the unittest module and the unittest.mock
    module to mock the GitHub API and test the function in isolation.

    Methods:
        test_search_issues: Test that search_issues returns the correct issues.

    """

    def test_search_issues(self):
        """Test that search_issues returns the correct issues."""
        # Set up the mock GitHub connection object
        mock_connection = MagicMock()
        mock_issues = [
            MagicMock(title="Issue 1"),
            MagicMock(title="Issue 2"),
        ]
        mock_connection.search_issues.return_value = mock_issues

        # Call search_issues and check that it returns the correct issues
        issues = search_issues("is:open", mock_connection)
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


class TestGetEnvVars(unittest.TestCase):
    """Test suite for the get_env_vars function."""

    def test_get_env_vars(self):
        """Test that the function correctly retrieves the environment variables."""
        # Set the environment variables
        os.environ["SEARCH_QUERY"] = "is:issue is:open repo:org/repo"

        # Call the function and check the result
        result = get_env_vars()
        expected_result = "is:issue is:open repo:org/repo"
        self.assertEqual(result[0], expected_result)

    def test_get_env_vars_missing_query(self):
        """Test that the function raises a ValueError
        if the SEARCH_QUERY environment variable is not set."""
        # Unset the SEARCH_QUERY environment variable
        os.environ.pop("SEARCH_QUERY", None)

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
            "SEARCH_QUERY": "is:open repo:user/repo",
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
                "alice",
                timedelta(days=1, hours=2, minutes=30),
            ),
            (
                "Issue 2",
                "https://github.com/user/repo/issues/2",
                "bob",
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
            "SEARCH_QUERY": "is:open repo:org/repo",
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
        mock_write_to_markdown.assert_called_once_with(
            None, None, None, None, None, None, None
        )


class TestGetPerIssueMetrics(unittest.TestCase):
    """Test suite for the get_per_issue_metrics function."""

    def test_get_per_issue_metrics(self):
        """Test that the function correctly calculates the metrics for a list of GitHub issues."""
        # Create mock data
        mock_issue1 = MagicMock(
            title="Issue 1",
            html_url="https://github.com/user/repo/issues/1",
            author="alice",
            state="open",
            comments=1,
            created_at="2023-01-01T00:00:00Z",
        )

        mock_comment1 = MagicMock()
        mock_comment1.created_at = datetime.fromisoformat("2023-01-02T00:00:00Z")
        mock_issue1.issue.comments.return_value = [mock_comment1]
        mock_issue1.issue.pull_request_urls = None

        mock_issue2 = MagicMock(
            title="Issue 2",
            html_url="https://github.com/user/repo/issues/2",
            author="bob",
            state="closed",
            comments=1,
            created_at="2023-01-01T00:00:00Z",
            closed_at="2023-01-04T00:00:00Z",
        )

        mock_comment2 = MagicMock()
        mock_comment2.created_at = datetime.fromisoformat("2023-01-03T00:00:00Z")
        mock_issue2.issue.comments.return_value = [mock_comment2]
        mock_issue2.issue.pull_request_urls = None

        issues = [
            mock_issue1,
            mock_issue2,
        ]

        # Call the function and check the result
        with unittest.mock.patch(  # type:ignore
            "issue_metrics.measure_time_to_first_response",
            measure_time_to_first_response,
        ), unittest.mock.patch(  # type:ignore
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
                "alice",
                timedelta(days=1),
                None,
                None,
                None,
            ),
            IssueWithMetrics(
                "Issue 2",
                "https://github.com/user/repo/issues/2",
                "bob",
                timedelta(days=2),
                timedelta(days=3),
                None,
                None,
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


class TestDiscussionMetrics(unittest.TestCase):
    """Test suite for the discussion_metrics function."""

    def setUp(self):
        # Mock a discussion dictionary
        self.issue1 = {
            "title": "Issue 1",
            "url": "github.com/user/repo/issues/1",
            "user": {
                "login": "alice",
            },
            "createdAt": "2023-01-01T00:00:00Z",
            "comments": {
                "nodes": [
                    {
                        "createdAt": "2023-01-02T00:00:00Z",
                    }
                ]
            },
            "answerChosenAt": "2023-01-04T00:00:00Z",
            "closedAt": "2023-01-05T00:00:00Z",
        }

        self.issue2 = {
            "title": "Issue 2",
            "url": "github.com/user/repo/issues/2",
            "user": {
                "login": "bob",
            },
            "createdAt": "2023-01-01T00:00:00Z",
            "comments": {"nodes": [{"createdAt": "2023-01-03T00:00:00Z"}]},
            "answerChosenAt": "2023-01-05T00:00:00Z",
            "closedAt": "2023-01-07T00:00:00Z",
        }

    def test_get_per_issue_metrics_with_discussion(self):
        """
        Test that the function correctly calculates
        the metrics for a list of GitHub issues with discussions.
        """

        issues = [self.issue1, self.issue2]
        metrics = get_per_issue_metrics(issues, discussions=True)

        # get_per_issue_metrics returns a tuple of
        # (issues_with_metrics, num_issues_open, num_issues_closed)
        self.assertEqual(len(metrics), 3)

        # Check that the metrics are correct, 0 issues open, 2 issues closed
        self.assertEqual(metrics[1], 0)
        self.assertEqual(metrics[2], 2)

        # Check that the issues_with_metrics has 2 issues in it
        self.assertEqual(len(metrics[0]), 2)

        # Check that the issues_with_metrics has the correct metrics,
        self.assertEqual(metrics[0][0].time_to_answer, timedelta(days=3))
        self.assertEqual(metrics[0][0].time_to_close, timedelta(days=4))
        self.assertEqual(metrics[0][0].time_to_first_response, timedelta(days=1))
        self.assertEqual(metrics[0][1].time_to_answer, timedelta(days=4))
        self.assertEqual(metrics[0][1].time_to_close, timedelta(days=6))
        self.assertEqual(metrics[0][1].time_to_first_response, timedelta(days=2))


if __name__ == "__main__":
    unittest.main()
