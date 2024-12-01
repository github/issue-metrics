"""A module containing unit tests for the get_discussions function in the discussions module.

Classes:
    TestGetDiscussions: A class to test the get_discussions function with mock GraphQL responses.

"""

import unittest
from unittest.mock import patch

from discussions import get_discussions


class TestGetDiscussions(unittest.TestCase):
    """A class to test the get_discussions function in the discussions module."""

    def _create_mock_response(
        self, discussions, has_next_page=False, end_cursor="cursor123"
    ):
        """Helper method to create a mock GraphQL response."""
        return {
            "data": {
                "search": {
                    "edges": [{"node": discussion} for discussion in discussions],
                    "pageInfo": {"hasNextPage": has_next_page, "endCursor": end_cursor},
                }
            }
        }

    @patch("requests.post")
    def test_get_discussions_single_page(self, mock_post):
        """Test the get_discussions function with a single page of results."""
        # Mock data for two discussions
        mock_discussions = [
            {
                "title": "Discussion 1",
                "url": "https://github.com/user/repo/discussions/1",
                "createdAt": "2021-01-01T00:00:00Z",
                "comments": {"nodes": [{"createdAt": "2021-01-01T00:01:00Z"}]},
                "answerChosenAt": None,
                "closedAt": None,
            },
            {
                "title": "Discussion 2",
                "url": "https://github.com/user/repo/discussions/2",
                "createdAt": "2021-01-02T00:00:00Z",
                "comments": {"nodes": [{"createdAt": "2021-01-02T00:01:00Z"}]},
                "answerChosenAt": "2021-01-03T00:00:00Z",
                "closedAt": "2021-01-04T00:00:00Z",
            },
        ]

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = self._create_mock_response(
            mock_discussions, has_next_page=False
        )

        discussions = get_discussions(
            "token", "repo:user/repo type:discussions query", ""
        )

        # Check that the function returns the expected discussions
        self.assertEqual(len(discussions), 2)
        self.assertEqual(discussions[0]["title"], "Discussion 1")
        self.assertEqual(discussions[1]["title"], "Discussion 2")

        # Verify only one API call was made
        self.assertEqual(mock_post.call_count, 1)

    @patch("requests.post")
    def test_get_discussions_multiple_pages(self, mock_post):
        """Test the get_discussions function with multiple pages of results."""
        # Mock data for pagination
        page1_discussions = [
            {
                "title": "Discussion 1",
                "url": "https://github.com/user/repo/discussions/1",
                "createdAt": "2021-01-01T00:00:00Z",
                "comments": {"nodes": [{"createdAt": "2021-01-01T00:01:00Z"}]},
                "answerChosenAt": None,
                "closedAt": None,
            }
        ]

        page2_discussions = [
            {
                "title": "Discussion 2",
                "url": "https://github.com/user/repo/discussions/2",
                "createdAt": "2021-01-02T00:00:00Z",
                "comments": {"nodes": [{"createdAt": "2021-01-02T00:01:00Z"}]},
                "answerChosenAt": None,
                "closedAt": None,
            }
        ]

        # Configure mock to return different responses for each call
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.side_effect = [
            self._create_mock_response(
                page1_discussions, has_next_page=True, end_cursor="cursor123"
            ),
            self._create_mock_response(page2_discussions, has_next_page=False),
        ]

        discussions = get_discussions(
            "token", "repo:user/repo type:discussions query", ""
        )

        # Check that all discussions were returned
        self.assertEqual(len(discussions), 2)
        self.assertEqual(discussions[0]["title"], "Discussion 1")
        self.assertEqual(discussions[1]["title"], "Discussion 2")

        # Verify that two API calls were made
        self.assertEqual(mock_post.call_count, 2)

    @patch("requests.post")
    def test_get_discussions_error_status_code(self, mock_post):
        """Test the get_discussions function with a failed HTTP response."""
        mock_post.return_value.status_code = 500

        with self.assertRaises(ValueError) as context:
            get_discussions("token", "repo:user/repo type:discussions query", "")

        self.assertIn(
            "GraphQL query failed with status code 500", str(context.exception)
        )

    @patch("requests.post")
    def test_get_discussions_graphql_error(self, mock_post):
        """Test the get_discussions function with GraphQL errors in response."""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "errors": [{"message": "GraphQL Error"}]
        }

        with self.assertRaises(ValueError) as context:
            get_discussions("token", "repo:user/repo type:discussions query", "")

        self.assertIn("GraphQL query failed:", str(context.exception))
