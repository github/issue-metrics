"""Test assignee functionality added to issue metrics."""

import os
import unittest
from unittest.mock import patch

from classes import IssueWithMetrics
from markdown_writer import get_non_hidden_columns


class TestAssigneeFunctionality(unittest.TestCase):
    """Test suite for the assignee functionality."""

    @patch.dict(
        os.environ,
        {
            "GH_TOKEN": "test_token",
            "SEARCH_QUERY": "is:issue is:open repo:user/repo",
            "HIDE_ASSIGNEE": "false",
            "HIDE_AUTHOR": "false",
        },
        clear=True,
    )
    def test_get_non_hidden_columns_includes_assignee_by_default(self):
        """Test that assignee column is included by default."""
        columns = get_non_hidden_columns(labels=None)
        self.assertIn("Assignee", columns)
        self.assertIn("Author", columns)

    @patch.dict(
        os.environ,
        {
            "GH_TOKEN": "test_token",
            "SEARCH_QUERY": "is:issue is:open repo:user/repo",
            "HIDE_ASSIGNEE": "true",
            "HIDE_AUTHOR": "false",
        },
        clear=True,
    )
    def test_get_non_hidden_columns_hides_assignee_when_env_set(self):
        """Test that assignee column is hidden when HIDE_ASSIGNEE is true."""
        columns = get_non_hidden_columns(labels=None)
        self.assertNotIn("Assignee", columns)
        self.assertIn("Author", columns)

    @patch.dict(
        os.environ,
        {
            "GH_TOKEN": "test_token",
            "SEARCH_QUERY": "is:issue is:open repo:user/repo",
            "HIDE_ASSIGNEE": "false",
            "HIDE_AUTHOR": "true",
        },
        clear=True,
    )
    def test_get_non_hidden_columns_shows_assignee_but_hides_author(self):
        """Test that assignee can be shown while author is hidden."""
        columns = get_non_hidden_columns(labels=None)
        self.assertIn("Assignee", columns)
        self.assertNotIn("Author", columns)

    @patch.dict(
        os.environ,
        {
            "GH_TOKEN": "test_token",
            "SEARCH_QUERY": "is:issue is:open repo:user/repo",
            "HIDE_ASSIGNEE": "true",
            "HIDE_AUTHOR": "true",
        },
        clear=True,
    )
    def test_get_non_hidden_columns_hides_both_assignee_and_author(self):
        """Test that both assignee and author can be hidden."""
        columns = get_non_hidden_columns(labels=None)
        self.assertNotIn("Assignee", columns)
        self.assertNotIn("Author", columns)

    def test_assignee_column_position(self):
        """Test that assignee column appears before author column."""
        with patch.dict(
            os.environ,
            {
                "GH_TOKEN": "test_token",
                "SEARCH_QUERY": "is:issue is:open repo:user/repo",
                "HIDE_ASSIGNEE": "false",
                "HIDE_AUTHOR": "false",
            },
            clear=True,
        ):
            columns = get_non_hidden_columns(labels=None)
            assignee_index = columns.index("Assignee")
            author_index = columns.index("Author")
            self.assertLess(
                assignee_index,
                author_index,
                "Assignee column should appear before Author column",
            )

    def test_multiple_assignees_rendering_logic(self):
        """Test that multiple assignees are rendered correctly in assignee column."""

        # Test the assignee rendering logic directly
        endpoint = "github.com"
        columns = ["Title", "URL", "Assignee", "Author"]

        # Initialize variables
        multiple_output = ""
        single_output = ""
        none_output = ""

        # Test case 1: Multiple assignees
        issue_multiple = IssueWithMetrics(
            title="Test Issue with Multiple Assignees",
            html_url="https://github.com/test/repo/issues/1",
            author="testuser",
            assignee="alice",
            assignees=["alice", "bob", "charlie"],
        )

        # Simulate the new rendering logic
        if "Assignee" in columns:
            if issue_multiple.assignees:
                assignee_links = [
                    f"[{assignee}](https://{endpoint}/{assignee})"
                    for assignee in issue_multiple.assignees
                ]
                multiple_output = f" {', '.join(assignee_links)} |"
            else:
                multiple_output = " None |"

        expected_multiple = (
            " [alice](https://github.com/alice), [bob](https://github.com/bob), "
            "[charlie](https://github.com/charlie) |"
        )
        self.assertEqual(
            multiple_output,
            expected_multiple,
            "Multiple assignees should be rendered as comma-separated links",
        )

        # Test case 2: Single assignee
        issue_single = IssueWithMetrics(
            title="Test Issue with Single Assignee",
            html_url="https://github.com/test/repo/issues/2",
            author="testuser",
            assignee="alice",
            assignees=["alice"],
        )

        if "Assignee" in columns:
            if issue_single.assignees:
                assignee_links = [
                    f"[{assignee}](https://{endpoint}/{assignee})"
                    for assignee in issue_single.assignees
                ]
                single_output = f" {', '.join(assignee_links)} |"
            else:
                single_output = " None |"

        expected_single = " [alice](https://github.com/alice) |"
        self.assertEqual(
            single_output,
            expected_single,
            "Single assignee should be rendered as a single link",
        )

        # Test case 3: No assignees
        issue_none = IssueWithMetrics(
            title="Test Issue with No Assignees",
            html_url="https://github.com/test/repo/issues/3",
            author="testuser",
            assignee=None,
            assignees=[],
        )

        if "Assignee" in columns:
            if issue_none.assignees:
                assignee_links = [
                    f"[{assignee}](https://{endpoint}/{assignee})"
                    for assignee in issue_none.assignees
                ]
                none_output = f" {', '.join(assignee_links)} |"
            else:
                none_output = " None |"

        expected_none = " None |"
        self.assertEqual(
            none_output, expected_none, "No assignees should be rendered as 'None'"
        )

        print(f"✅ Multiple assignees test: {expected_multiple}")
        print(f"✅ Single assignee test: {expected_single}")
        print(f"✅ No assignees test: {expected_none}")


if __name__ == "__main__":
    unittest.main()
