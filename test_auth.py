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
        result = auth_to_github("", 12345, 678910, b"hello", "", False)

        self.assertIsInstance(result, github3.github.GitHub, False)

    def test_auth_to_github_with_token(self):
        """
        Test the auth_to_github function when the token is provided.
        """
        result = auth_to_github("token", None, None, b"", "", False)

        self.assertIsInstance(result, github3.github.GitHub, False)

    def test_auth_to_github_without_authentication_information(self):
        """
        Test the auth_to_github function when authentication information is not provided.
        Expect a ValueError to be raised.
        """
        with self.assertRaises(ValueError):
            auth_to_github("", None, None, b"", "", False)

    def test_auth_to_github_with_ghe(self):
        """
        Test the auth_to_github function when the GitHub Enterprise URL is provided.
        """
        result = auth_to_github(
            "token", None, None, b"", "https://github.example.com", False
        )

        self.assertIsInstance(result, github3.github.GitHubEnterprise, False)

    @patch("github3.github.GitHubEnterprise")
    def test_auth_to_github_with_ghe_and_ghe_app(self, mock_ghe):
        """
        Test the auth_to_github function when the GitHub Enterprise URL \
            is provided and the app was created in GitHub Enterprise URL.
        """
        mock = mock_ghe.return_value
        mock.login_as_app_installation = MagicMock(return_value=True)
        result = auth_to_github(
            "", "123", "123", b"123", "https://github.example.com", True
        )
        mock.login_as_app_installation.assert_called_once()
        self.assertEqual(result, mock)

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
        mock_ghe = ""

        result = get_github_app_installation_token(
            mock_ghe, b"gh_private_token", "gh_app_id", "gh_installation_id"
        )

        self.assertEqual(result, dummy_token)
