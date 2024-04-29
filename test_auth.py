"""A module containing unit tests for the auth module.

This module contains unit tests for the functions in the auth module
that authenticate to github.

Classes:
    TestAuthToGithub: A class to test the auth_to_github function.

"""

import unittest
from unittest.mock import MagicMock, patch

import github3
from auth import auth_to_github, get_github_app_installation_token


class TestAuthToGithub(unittest.TestCase):
    """Test the auth_to_github function."""

    @patch("github3.github.GitHub.login_as_app_installation")
    def test_auth_to_github_with_github_app(self, mock_login):
        """
        Test the auth_to_github function when GitHub app
        parameters provided.
        """
        mock_login.return_value = MagicMock()
        result = auth_to_github(12345, 678910, b"hello", "", "")

        self.assertIsInstance(result, github3.github.GitHub)

    def test_auth_to_github_with_token(self):
        """
        Test the auth_to_github function when the token is provided.
        """
        result = auth_to_github(None, None, b"", "token", "")

        self.assertIsInstance(result, github3.github.GitHub)

    def test_auth_to_github_without_authentication_information(self):
        """
        Test the auth_to_github function when authentication information is not provided.
        Expect a ValueError to be raised.
        """
        with self.assertRaises(ValueError):
            auth_to_github(None, None, b"", "", "")

    def test_auth_to_github_with_ghe(self):
        """
        Test the auth_to_github function when the GitHub Enterprise URL is provided.
        """
        result = auth_to_github(None, None, b"", "token", "https://github.example.com")

        self.assertIsInstance(result, github3.github.GitHubEnterprise)

    @patch("github3.apps.create_jwt_headers", MagicMock(return_value="gh_token"))
    @patch("requests.post")
    def test_get_github_app_installation_token(self, mock_post):
        """
        Test the get_github_app_installation_token function.
        """
        dummy_token = "dummytoken"
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"token": dummy_token}
        mock_post.return_value = mock_response

        result = get_github_app_installation_token(
            b"gh_private_token", "gh_app_id", "gh_installation_id"
        )

        self.assertEqual(result, dummy_token)
