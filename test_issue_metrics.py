import os
import unittest
from datetime import timedelta
from unittest.mock import MagicMock, patch

from issue_metrics import (
    auth_to_github,
    get_average_time_to_first_response,
    measure_time_to_first_response,
    search_issues,
    write_to_markdown,
)


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
            MagicMock(time_to_first_response=timedelta(days=1)),
            MagicMock(time_to_first_response=timedelta(hours=13, minutes=30)),
            MagicMock(time_to_first_response=timedelta(hours=4, minutes=30)),
        ]

        # Call get_average_time_to_first_response with the list of issues
        average_time_to_first_response = get_average_time_to_first_response(issues)

        # Check that the function returns the correct average time to first response
        expected_average_time_to_first_response = timedelta(hours=14)
        self.assertEqual(
            average_time_to_first_response,
            expected_average_time_to_first_response.seconds,
        )


class TestWriteToMarkdown(unittest.TestCase):
    """Test the write_to_markdown function."""

    def test_write_to_markdown(self):
        """Test that write_to_markdown writes the correct output to a file.

        This test creates a temporary file, calls write_to_markdown with a list of
        issues and their time to first response, and checks that the file contains
        the expected output.

        """
        # Create a temporary file
        with open("temp.md", "w") as f:
            f.write("")

        # Call write_to_markdown with a list of issues and their time to first response
        issues_with_metrics = [
            ("Issue 1", "1 day, 2:30:00"),
            ("Issue 2", "3 days, 4:30:00"),
            ("Issue 3", "0:30:00"),
        ]
        average_time_to_first_response = "1 day, 3:10:00"
        write_to_markdown(
            issues_with_metrics,
            average_time_to_first_response,
            file=open("temp.md", "w"),
        )

        # Check that the file contains the expected output
        with open("temp.md", "r") as f:
            output = f.read()
        expected_output = (
            "# Issue Metrics\n\n"
            "Average time to first response: 1 day, 3:10:00\n"
            "Number of issues: 3\n\n"
            "| Issue | TTFR |\n"
            "| --- | ---: |\n"
            "| Issue 2 | 3 days, 4:30:00 |\n"
            "| Issue 1 | 1 day, 2:30:00 |\n"
            "| Issue 3 | 0:30:00 |\n"
        )
        self.assertEqual(output, expected_output)

        # Remove the temporary file
        os.remove("temp.md")


class TestSearchIssues(unittest.TestCase):
    """Test the search_issues function."""

    @patch("github3.login")
    def test_search_issues(self, mock_login):
        """Test that search_issues returns the correct issues.

        This test mocks the GitHub connection and repository, and checks that
        search_issues returns the correct issues.

        """
        # Mock the GitHub connection
        mock_gh = MagicMock()
        mock_login.return_value = mock_gh

        # Mock the repository and issues
        mock_repo = MagicMock()
        mock_issue1 = MagicMock(title="Test issue 1")
        mock_issue2 = MagicMock(title="Test issue 2")
        mock_repo.search_issues.return_value = [mock_issue1, mock_issue2]
        mock_gh.repository.return_value = mock_repo

        # Call the function
        issues = search_issues(
            "https://github.com/octocat/hello-world", "is:open is:issue", mock_gh
        )

        # Check the results
        self.assertEqual(len(issues), 2)
        self.assertEqual(issues[0].title, "Test issue 1")
        self.assertEqual(issues[1].title, "Test issue 2")
        mock_gh.repository.assert_called_once_with("octocat", "hello-world")
        mock_repo.search_issues.assert_called_once_with("is:open is:issue")


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

    def test_auth_to_github_without_token(self):
        """Test that auth_to_github raises an exception without a token.

        This test sets the GH_TOKEN environment variable to an empty string and
        checks that auth_to_github raises a ValueError exception.

        """
        # Set up the environment variable
        os.environ.pop("GH_TOKEN", None)

        # Call the function and check for an exception
        with self.assertRaises(ValueError):
            auth_to_github()


class TestMeasureTimeToFirstResponse(unittest.TestCase):
    """Test the measure_time_to_first_response function."""

    def test_measure_time_to_first_response(self):
        """Test that measure_time_to_first_response calculates the correct time.

        This test mocks the GitHub connection and issue comments, and checks that
        measure_time_to_first_response calculates the correct time to first response.

        """
        # Set up the mock GitHub issues
        mock_issue1 = MagicMock()
        mock_issue1.created_at = "2023-01-01T00:00:00Z"
        mock_comment1 = MagicMock()
        mock_comment1.created_at = "2023-01-02T00:00:00Z"
        mock_issue1.comments.return_value = [mock_comment1]

        mock_issue2 = MagicMock()
        mock_issue2.created_at = "2023-01-03T00:00:00Z"
        mock_comment2 = MagicMock()
        mock_comment2.created_at = "2023-01-04T00:00:00Z"
        mock_issue2.comments.return_value = [mock_comment2]

        mock_issues = [mock_issue1, mock_issue2]

        # Call the function
        issues_with_metrics = measure_time_to_first_response(mock_issues)

        # Check the results
        self.assertEqual(len(issues_with_metrics), 2)
        self.assertEqual(issues_with_metrics[0].time_to_first_response.days, 1)
        self.assertEqual(issues_with_metrics[1].time_to_first_response.days, 1)
