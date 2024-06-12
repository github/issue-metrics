"""A module containing unit tests for the config module functions.

Classes:
    TestGetIntFromEnv: A class to test the get_int_env_var function.
    TestEnvVars: A class to test the get_env_vars function.

"""

import os
import unittest
from unittest.mock import patch

from config import EnvVars, get_env_vars, get_int_env_var

SEARCH_QUERY = "is:issue is:open repo:user/repo"
TOKEN = "test_token"


class TestGetIntFromEnv(unittest.TestCase):
    """
    Test suite for the get_int_from_env function.

    ...

    Test methods:
        - test_get_int_env_var: Test returns the expected integer value.
        - test_get_int_env_var_with_empty_env_var: Test returns None when environment variable
          is empty.
        - test_get_int_env_var_with_non_integer: Test returns None when environment variable
          is a non-integer.
    """

    @patch.dict(os.environ, {"INT_ENV_VAR": "12345"})
    def test_get_int_env_var(self):
        """
        Test that get_int_env_var returns the expected integer value.
        """
        result = get_int_env_var("INT_ENV_VAR")
        self.assertEqual(result, 12345)

    @patch.dict(os.environ, {"INT_ENV_VAR": ""})
    def test_get_int_env_var_with_empty_env_var(self):
        """
        This test verifies that the get_int_env_var function returns None
        when the environment variable is empty.

        """
        result = get_int_env_var("INT_ENV_VAR")
        self.assertIsNone(result)

    @patch.dict(os.environ, {"INT_ENV_VAR": "not_an_int"})
    def test_get_int_env_var_with_non_integer(self):
        """
        Test that get_int_env_var returns None when the environment variable is
        a non-integer.

        """
        result = get_int_env_var("INT_ENV_VAR")
        self.assertIsNone(result)


class TestGetEnvVars(unittest.TestCase):
    """
    Test suite for the get_env_vars function.
    """

    def setUp(self):
        env_keys = [
            "GH_APP_ID",
            "GH_APP_INSTALLATION_ID",
            "GH_APP_PRIVATE_KEY",
            "GH_TOKEN",
            "GHE",
            "HIDE_AUTHOR",
            "HIDE_ITEMS_CLOSED_COUNT",
            "HIDE_LABEL_METRICS",
            "HIDE_TIME_TO_ANSWER",
            "HIDE_TIME_TO_CLOSE",
            "HIDE_TIME_TO_FIRST_RESPONSE",
            "IGNORE_USERS",
            "LABELS_TO_MEASURE",
            "SEARCH_QUERY",
        ]
        for key in env_keys:
            if key in os.environ:
                del os.environ[key]

    @patch.dict(
        os.environ,
        {
            "GH_APP_ID": "12345",
            "GH_APP_INSTALLATION_ID": "678910",
            "GH_APP_PRIVATE_KEY": "hello",
            "GH_TOKEN": "",
            "GH_ENTERPRISE_URL": "",
            "HIDE_AUTHOR": "",
            "HIDE_ITEMS_CLOSED_COUNT": "false",
            "HIDE_LABEL_METRICS": "",
            "HIDE_TIME_TO_ANSWER": "",
            "HIDE_TIME_TO_CLOSE": "",
            "HIDE_TIME_TO_FIRST_RESPONSE": "",
            "IGNORE_USERS": "",
            "LABELS_TO_MEASURE": "",
            "SEARCH_QUERY": SEARCH_QUERY,
        },
        clear=True,
    )
    def test_get_env_vars_with_github_app(self):
        """Test that all environment variables are set correctly using GitHub App"""
        expected_result = EnvVars(
            12345,
            678910,
            b"hello",
            "",
            "",
            False,
            False,
            False,
            False,
            False,
            False,
            [],
            [],
            False,
            "10",
            "20",
            "3",
            SEARCH_QUERY,
        )
        result = get_env_vars(True)
        self.assertEqual(str(result), str(expected_result))

    @patch.dict(
        os.environ,
        {
            "GH_APP_ID": "",
            "GH_APP_INSTALLATION_ID": "",
            "GH_APP_PRIVATE_KEY": "",
            "GH_ENTERPRISE_URL": "",
            "GH_TOKEN": TOKEN,
            "HIDE_AUTHOR": "",
            "HIDE_ITEMS_CLOSED_COUNT": "false",
            "HIDE_LABEL_METRICS": "",
            "HIDE_TIME_TO_ANSWER": "",
            "HIDE_TIME_TO_CLOSE": "",
            "HIDE_TIME_TO_FIRST_RESPONSE": "",
            "IGNORE_USERS": "",
            "LABELS_TO_MEASURE": "",
            "SEARCH_QUERY": SEARCH_QUERY,
        },
        clear=True,
    )
    def test_get_env_vars_with_token(self):
        """Test that all environment variables are set correctly using a list of repositories"""
        expected_result = EnvVars(
            None,
            None,
            b"",
            TOKEN,
            "",
            False,
            False,
            False,
            False,
            False,
            False,
            [],
            [],
            False,
            "10",
            "20",
            "3",
            SEARCH_QUERY,
        )
        result = get_env_vars(True)
        self.assertEqual(str(result), str(expected_result))

    @patch.dict(
        os.environ,
        {
            "GH_APP_ID": "",
            "GH_APP_INSTALLATION_ID": "",
            "GH_APP_PRIVATE_KEY": "",
            "GH_TOKEN": "",
            "SEARCH_QUERY": SEARCH_QUERY,
            "HIDE_ITEMS_CLOSED_COUNT": "false",
        },
        clear=True,
    )
    def test_get_env_vars_missing_token(self):
        """Test that an error is raised if the TOKEN environment variables is not set"""
        with self.assertRaises(ValueError):
            get_env_vars(True)

    @patch.dict(
        os.environ,
        {
            "GH_APP_ID": "",
            "GH_APP_INSTALLATION_ID": "",
            "GH_APP_PRIVATE_KEY": "",
            "GH_TOKEN": TOKEN,
            "SEARCH_QUERY": "",
            "HIDE_ITEMS_CLOSED_COUNT": "false",
        },
        clear=True,
    )
    def test_get_env_vars_missing_query(self):
        """Test that an error is raised if the SEARCH_QUERY environment variable is not set."""

        with self.assertRaises(ValueError):
            get_env_vars(True)

    @patch.dict(
        os.environ,
        {
            "GH_APP_ID": "",
            "GH_APP_INSTALLATION_ID": "",
            "GH_APP_PRIVATE_KEY": "",
            "GH_TOKEN": TOKEN,
            "GH_ENTERPRISE_URL": "",
            "HIDE_AUTHOR": "true",
            "HIDE_ITEMS_CLOSED_COUNT": "true",
            "HIDE_LABEL_METRICS": "true",
            "HIDE_TIME_TO_ANSWER": "true",
            "HIDE_TIME_TO_CLOSE": "true",
            "HIDE_TIME_TO_FIRST_RESPONSE": "true",
            "IGNORE_USERS": "",
            "LABELS_TO_MEASURE": "waiting-for-review,waiting-for-manager",
            "SEARCH_QUERY": SEARCH_QUERY,
        },
    )
    def test_get_env_vars_optional_values(self):
        """Test that optional values are set to their default values if not provided"""
        expected_result = EnvVars(
            None,
            None,
            b"",
            TOKEN,
            "",
            True,
            True,
            True,
            True,
            True,
            True,
            [],
            ["waiting-for-review", "waiting-for-manager"],
            False,
            10,
            20,
            3,
            SEARCH_QUERY,
        )
        result = get_env_vars(True)
        self.assertEqual(str(result), str(expected_result))

    @patch.dict(
        os.environ,
        {
            "GH_APP_ID": "",
            "GH_APP_INSTALLATION_ID": "",
            "GH_APP_PRIVATE_KEY": "",
            "GH_TOKEN": "TOKEN",
            "SEARCH_QUERY": SEARCH_QUERY,
        },
        clear=True,
    )
    def test_get_env_vars_optionals_are_defaulted(self):
        """Test that optional values are set to their default values if not provided"""
        expected_result = EnvVars(
            None,
            None,
            b"",
            "TOKEN",
            "",
            False,
            False,
            False,
            False,
            False,
            False,
            [],
            [],
            False,
            "10",
            "20",
            "3",
            SEARCH_QUERY,
        )
        result = get_env_vars(True)
        self.assertEqual(str(result), str(expected_result))


if __name__ == "__main__":
    unittest.main()
