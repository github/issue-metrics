"""Unit tests for the search module."""

import unittest
from unittest.mock import MagicMock

from search import get_owners_and_repositories, search_issues


class TestSearchIssues(unittest.TestCase):
    """Unit tests for the search_issues function.

    This class contains unit tests for the search_issues function in the
    issue_metrics module. The tests use the unittest module and the unittest.mock
    module to mock the GitHub API and test the function in isolation.

    Methods:
        test_search_issues_with_owner_and_repository:
            Test that search_issues with owner/repo returns the correct issues.
        test_search_issues_with_just_owner_or_org:
            Test that search_issues with just an owner/org returns the correct issues.
        test_search_issues_with_just_owner_or_org_with_bypass:
            Test that search_issues with just an owner/org returns the correct issues
            with rate limit bypass enabled.

    """

    def test_search_issues_with_owner_and_repository(self):
        """Test that search_issues with owner/repo returns the correct issues."""

        # Set up the mock GitHub connection object
        mock_issues = [
            MagicMock(title="Issue 1"),
            MagicMock(title="Issue 2"),
        ]

        # simulating github3.structs.SearchIterator return value
        mock_search_result = MagicMock()
        mock_search_result.__iter__.return_value = iter(mock_issues)
        mock_search_result.ratelimit_remaining = 30

        mock_connection = MagicMock()
        mock_connection.search_issues.return_value = mock_search_result

        # Call search_issues and check that it returns the correct issues
        repo_with_owner = {"owner": "owner1", "repository": "repo1"}
        owners_and_repositories = [repo_with_owner]
        issues = search_issues("is:open", mock_connection, owners_and_repositories)
        self.assertEqual(issues, mock_issues)

    def test_search_issues_with_just_owner_or_org(self):
        """Test that search_issues with just an owner/org returns the correct issues."""

        # Set up the mock GitHub connection object
        mock_issues = [
            MagicMock(title="Issue 1"),
            MagicMock(title="Issue 2"),
            MagicMock(title="Issue 3"),
        ]

        # simulating github3.structs.SearchIterator return value
        mock_search_result = MagicMock()
        mock_search_result.__iter__.return_value = iter(mock_issues)
        mock_search_result.ratelimit_remaining = 30

        mock_connection = MagicMock()
        mock_connection.search_issues.return_value = mock_search_result

        # Call search_issues and check that it returns the correct issues
        org = {"owner": "org1"}
        owners = [org]
        issues = search_issues("is:open", mock_connection, owners)
        self.assertEqual(issues, mock_issues)

    def test_search_issues_with_just_owner_or_org_with_bypass(self):
        """Test that search_issues with just an owner/org returns the correct issues."""

        # Set up the mock GitHub connection object
        mock_issues = [
            MagicMock(title="Issue 1"),
            MagicMock(title="Issue 2"),
            MagicMock(title="Issue 3"),
        ]

        # simulating github3.structs.SearchIterator return value
        mock_search_result = MagicMock()
        mock_search_result.__iter__.return_value = iter(mock_issues)
        mock_search_result.ratelimit_remaining = 30

        mock_connection = MagicMock()
        mock_connection.search_issues.return_value = mock_search_result

        # Call search_issues and check that it returns the correct issues
        org = {"owner": "org1"}
        owners = [org]
        issues = search_issues(
            "is:open", mock_connection, owners, rate_limit_bypass=True
        )
        self.assertEqual(issues, mock_issues)


class TestGetOwnerAndRepository(unittest.TestCase):
    """Unit tests for the get_owners_and_repositories function.

    This class contains unit tests for the get_owners_and_repositories function in the
    issue_metrics module. The tests use the unittest module and the unittest.mock
    module to mock the GitHub API and test the function in isolation.

    Methods:
        test_get_owners_with_owner_and_repo_in_query: Test get both owner and repo.
        test_get_owner_and_repositories_without_repo_in_query: Test get just owner.
        test_get_owners_and_repositories_without_either_in_query: Test get neither.
        test_get_owners_and_repositories_with_multiple_entries: Test get multiple entries.
        test_get_owners_and_repositories_with_org: Test get org as owner.
        test_get_owners_and_repositories_with_user: Test get user as owner.
    """

    def test_get_owners_with_owner_and_repo_in_query(self):
        """Test get both owner and repo."""
        result = get_owners_and_repositories("repo:owner1/repo1")
        self.assertEqual(result[0].get("owner"), "owner1")
        self.assertEqual(result[0].get("repository"), "repo1")

    def test_get_owner_and_repositories_without_repo_in_query(self):
        """Test get just owner."""
        result = get_owners_and_repositories("org:owner1")
        self.assertEqual(result[0].get("owner"), "owner1")
        self.assertIsNone(result[0].get("repository"))

    def test_get_owners_and_repositories_without_either_in_query(self):
        """Test get neither."""
        result = get_owners_and_repositories("is:blah")
        self.assertEqual(result, [])

    def test_get_owners_and_repositories_with_multiple_entries(self):
        """Test get multiple entries."""
        result = get_owners_and_repositories("repo:owner1/repo1 org:owner2")
        self.assertEqual(result[0].get("owner"), "owner1")
        self.assertEqual(result[0].get("repository"), "repo1")
        self.assertEqual(result[1].get("owner"), "owner2")
        self.assertIsNone(result[1].get("repository"))

    def test_get_owners_and_repositories_with_org(self):
        """Test get org as owner."""
        result = get_owners_and_repositories("org:owner1")
        self.assertEqual(result[0].get("owner"), "owner1")
        self.assertIsNone(result[0].get("repository"))

    def test_get_owners_and_repositories_with_user(self):
        """Test get user as owner."""
        result = get_owners_and_repositories("user:owner1")
        self.assertEqual(result[0].get("owner"), "owner1")
        self.assertIsNone(result[0].get("repository"))
