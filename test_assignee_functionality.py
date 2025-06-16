"""Test assignee functionality added to issue metrics."""

import os
import unittest
from unittest.mock import patch
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
            self.assertLess(assignee_index, author_index, 
                          "Assignee column should appear before Author column")


if __name__ == "__main__":
    unittest.main()