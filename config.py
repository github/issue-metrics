"""A module for managing environment variables used in GitHub metrics calculation.

This module defines a class for encapsulating environment variables and a function to retrieve these variables.

Classes:
    EnvVars: Represents the collection of environment variables used in the script.

Functions:
    get_env_vars: Retrieves and returns an instance of EnvVars populated with environment variables.
"""

import os
from os.path import dirname, join
from typing import List

from dotenv import load_dotenv


class EnvVars:
    # pylint: disable=too-many-instance-attributes
    """
    Environment variables

    Attributes:
        gh_app_id (int | None): The GitHub App ID to use for authentication
        gh_app_installation_id (int | None): The GitHub App Installation ID to use for authentication
        gh_app_private_key_bytes (bytes): The GitHub App Private Key as bytes to use for authentication
        gh_token (str | None): GitHub personal access token (PAT) for API authentication
        ghe (str): The GitHub Enterprise URL to use for authentication
        hide_author (bool): If true, the author's information is hidden in the output
        hide_label_metrics (bool): If true, the label metrics are hidden in the output
        hide_time_to_answer (bool): If true, the time to answer discussions is hidden in the output
        hide_time_to_close (bool): If true, the time to close metric is hidden in the output
        hide_time_to_first_response (bool): If true, the time to first response metric is hidden in the output
        ignore_users (List[str]): List of usernames to ignore when calculating metrics
        labels_to_measure (List[str]): List of labels to measure how much time the lable is applied
        enable_mentor_count (str): If set to TRUE, compute number of mentors
        min_mentor_comments (str): If set, defines the minimum number of comments for mentors
        max_comments_eval (str): If set, defines the maximum number of comments to look at for mentor evaluation
        heavily_involved_cutoff (str): If set, defines the cutoff after which heavily involved commentors in
        search_query (str): Search query used to filter issues/prs/discussions on GitHub
    """

    def __init__(
        self,
        gh_app_id: int | None,
        gh_app_installation_id: int | None,
        gh_app_private_key_bytes: bytes,
        gh_token: str | None,
        ghe: str | None,
        hide_author: bool,
        hide_label_metrics: bool,
        hide_time_to_answer: bool,
        hide_time_to_close: bool,
        hide_time_to_first_response: bool,
        ignore_user: List[str],
        labels_to_measure: List[str],
        enable_mentor_count: str,
        min_mentor_comments: str,
        max_comments_eval: str,
        heavily_involved_cutoff: str,
        search_query: str,
    ):
        self.gh_app_id = gh_app_id
        self.gh_app_installation_id = gh_app_installation_id
        self.gh_app_private_key_bytes = gh_app_private_key_bytes
        self.search_query = search_query
        self.gh_token = gh_token
        self.ghe = ghe
        self.ignore_users = ignore_user
        self.labels_to_measure = labels_to_measure
        self.hide_author = hide_author
        self.hide_label_metrics = hide_label_metrics
        self.hide_time_to_answer = hide_time_to_answer
        self.hide_time_to_close = hide_time_to_close
        self.hide_time_to_first_response = hide_time_to_first_response
        self.enable_mentor_count = enable_mentor_count
        self.min_mentor_comments = min_mentor_comments
        self.max_comments_eval = max_comments_eval
        self.heavily_involved_cutoff = heavily_involved_cutoff
        self.search_query = search_query

    def __repr__(self):
        return (
            f"EnvVars("
            f"{self.gh_app_id},"
            f"{self.gh_app_installation_id},"
            f"{self.gh_app_private_key_bytes},"
            f"{self.gh_token},"
            f"{self.ghe},"
            f"{self.hide_author},"
            f"{self.hide_label_metrics},"
            f"{self.hide_time_to_answer},"
            f"{self.hide_time_to_close},"
            f"{self.hide_time_to_first_response},"
            f"{self.ignore_users},"
            f"{self.labels_to_measure},"
            f"{self.enable_mentor_count},"
            f"{self.min_mentor_comments},"
            f"{self.max_comments_eval},"
            f"{self.heavily_involved_cutoff},"
            f"{self.search_query})"
        )


def get_bool_env_var(env_var_name: str) -> bool:
    """Get a boolean environment variable.

    Args:
        env_var_name: The name of the environment variable to retrieve.

    Returns:
        The value of the environment variable as a boolean.
    """
    return os.environ.get(env_var_name, "").strip().lower() == "true"


def get_int_env_var(env_var_name: str) -> int | None:
    """Get an integer environment variable.

    Args:
        env_var_name: The name of the environment variable to retrieve.

    Returns:
        The value of the environment variable as an integer or None.
    """
    env_var = os.environ.get(env_var_name)
    if env_var is None or not env_var.strip():
        return None
    try:
        return int(env_var)
    except ValueError:
        return None


def get_env_vars(test: bool = False) -> EnvVars:
    """
    Get the environment variables for use in the script.

    Returns EnvVars object with all environment variables
    """
    if not test:
        dotenv_path = join(dirname(__file__), ".env")
        load_dotenv(dotenv_path)

    search_query = os.getenv("SEARCH_QUERY")
    if not search_query:
        raise ValueError("SEARCH_QUERY environment variable not set")

    gh_app_id = get_int_env_var("GH_APP_ID")
    gh_app_private_key_bytes = os.environ.get("GH_APP_PRIVATE_KEY", "").encode("utf8")
    gh_app_installation_id = get_int_env_var("GH_APP_INSTALLATION_ID")

    if gh_app_id and (not gh_app_private_key_bytes or not gh_app_installation_id):
        raise ValueError(
            "GH_APP_ID set and GH_APP_INSTALLATION_ID or GH_APP_PRIVATE_KEY variable not set"
        )

    gh_token = os.getenv("GH_TOKEN")
    if (
        not gh_app_id
        and not gh_app_private_key_bytes
        and not gh_app_installation_id
        and not gh_token
    ):
        raise ValueError("GH_TOKEN environment variable not set")

    ghe = os.getenv("GH_ENTERPRISE_URL", default="").strip()

    labels_to_measure_list: List[str] = []
    labels_to_measure: str | None = os.getenv("LABELS_TO_MEASURE")
    if labels_to_measure:
        labels_to_measure_list = labels_to_measure.split(",")

    ignore_users_list: List[str] = []
    ignore_users: str | None = os.getenv("IGNORE_USERS")
    if ignore_users:
        ignore_users_list = ignore_users.split(",")

    # Hidden columns
    hide_author = get_bool_env_var("HIDE_AUTHOR")
    hide_label_metrics = get_bool_env_var("HIDE_LABEL_METRICS")
    hide_time_to_answer = get_bool_env_var("HIDE_TIME_TO_ANSWER")
    hide_time_to_close = get_bool_env_var("HIDE_TIME_TO_CLOSE")
    hide_time_to_first_response = get_bool_env_var("HIDE_TIME_TO_FIRST_RESPONSE")
    enable_mentor_count = get_bool_env_var("ENABLE_MENTOR_COUNT")
    min_mentor_comments = os.getenv("MIN_MENTOR_COMMENTS", "10")
    max_comments_eval = os.getenv("MAX_COMMENTS_EVAL", "20")
    heavily_involved_cutoff = os.getenv("HEAVILY_INVOLVED_CUTOFF", "3")

    return EnvVars(
        gh_app_id,
        gh_app_installation_id,
        gh_app_private_key_bytes,
        gh_token,
        ghe,
        hide_author,
        hide_label_metrics,
        hide_time_to_answer,
        hide_time_to_close,
        hide_time_to_first_response,
        ignore_users_list,
        labels_to_measure_list,
        enable_mentor_count,
        min_mentor_comments,
        max_comments_eval,
        heavily_involved_cutoff,
        search_query,
    )
