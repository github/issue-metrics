"""A module containing unit tests for the get_discussions function in the discussions module.

Classes:
    TestGetDiscussions: A class to test the get_discussions function with mock GraphQL responses.

"""
import unittest
from unittest.mock import patch
from discussions import get_discussions


class TestGetDiscussions(unittest.TestCase):
    """A class to test the get_discussions function in the discussions module."""

    @patch("requests.post")
    def test_get_discussions(self, mock_post):
        """Test the get_discussions function with a successful GraphQL response.

        This test mocks a successful GraphQL response and checks that the
        function returns the expected discussions.

        """
        # Mock the GraphQL response
        mock_response = {
            "data": {
                "search": {
                    "edges": [
                        {
                            "node": {
                                "title": "Discussion 1",
                                "url": "https://github.com/user/repo/discussions/1",
                                "createdAt": "2021-01-01T00:00:00Z",
                                "comments": {
                                    "nodes": [{"createdAt": "2021-01-01T00:01:00Z"}]
                                },
                                "answerChosenAt": None,
                                "closedAt": None,
                            }
                        },
                        {
                            "node": {
                                "title": "Discussion 2",
                                "url": "https://github.com/user/repo/discussions/2",
                                "createdAt": "2021-01-02T00:00:00Z",
                                "comments": {
                                    "nodes": [{"createdAt": "2021-01-02T00:01:00Z"}]
                                },
                                "answerChosenAt": "2021-01-03T00:00:00Z",
                                "closedAt": "2021-01-04T00:00:00Z",
                            }
                        },
                    ]
                }
            }
        }
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response

        # Call the function with mock arguments
        discussions = get_discussions("token", "repo:user/repo type:discussions query")

        # Check that the function returns the expected discussions
        self.assertEqual(len(discussions), 2)
        self.assertEqual(discussions[0]["title"], "Discussion 1")
        self.assertEqual(discussions[1]["title"], "Discussion 2")

    @patch("requests.post")
    def test_get_discussions_error(self, mock_post):
        """Test the get_discussions function with a failed GraphQL response.

        This test mocks a failed GraphQL response and checks that the function raises a ValueError.

        """
        # Mock a failed GraphQL response
        mock_post.return_value.status_code = 500

        # Call the function with mock arguments and check that it raises an error
        with self.assertRaises(ValueError):
            get_discussions("token", "repo:user/repo type:discussions query")
