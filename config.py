"""A module for managing environment variables used in GitHub metrics calculation.

This module defines a class for encapsulating environment variables and a function to retrieve these variables.

Classes:
    EnvVars: Represents the collection of environment variables used in the script.

Functions:
    get_env_vars: Retrieves and returns an instance of EnvVars populated with environment variables.
"""
import os
from typing import List


class EnvVars:
    # pylint: disable=too-many-instance-attributes
    """
    Environment variables

    Attributes:
        search_query (str): Search query used to filter issues/prs/discussions on GitHub
        gh_token (str): GitHub personal access token (PAT) for API authentication
        labels_to_measure (List[str]): List of labels to measure how much time the lable is applied
        ignore_users (List[str]): List of usernames to ignore when calculating metrics
        github_server_url (str): URL of GitHub server (Github.com or Github Enterprise)
        hide_author (str): If set, the author's information is hidden in the output
        hide_time_to_first_response (str): If set, the time to first response metric is hidden in the output
        hide_time_to_close (str): If set, the time to close metric is hidden in the output
        hide_time_to_answer (str): If set, the time to answer discussions is hidden in the output
        hide_label_metrics (str): If set, the label metrics are hidden in the output
    """
    def __init__(self, search_query: str, gh_token: str, labels_to_measure: List[str], ignore_user: List[str],
                 github_server_url: str, hide_author: str, hide_time_to_first_response: str,
                 hide_time_to_close: str, hide_time_to_answer: str, hide_label_metrics: str):
        self.search_query = search_query
        self.gh_token = gh_token
        self.labels_to_measure = labels_to_measure
        self.ignore_users = ignore_user
        self.github_server_url = github_server_url
        self.hide_author = hide_author
        self.hide_time_to_first_response = hide_time_to_first_response
        self.hide_time_to_close = hide_time_to_close
        self.hide_time_to_answer = hide_time_to_answer
        self.hide_label_metrics = hide_label_metrics


def get_env_vars() -> EnvVars:
    """
    Get the environment variables for use in the script.

    Returns EnvVars object with all environment variables
    """
    search_query = os.getenv("SEARCH_QUERY")
    if not search_query:
        raise ValueError("SEARCH_QUERY environment variable not set")

    gh_token = os.getenv("GH_TOKEN")
    if not gh_token:
        raise ValueError("GITHUB_TOKEN environment variable not set")

    labels_to_measure = os.getenv("LABELS_TO_MEASURE")
    if labels_to_measure:
        labels_to_measure = labels_to_measure.split(",")
    else:
        labels_to_measure = []

    ignore_users = os.getenv("IGNORE_USERS")
    if ignore_users:
        ignore_users = ignore_users.split(",")
    else:
        ignore_users = []

    github_server_url = os.getenv("GITHUB_SERVER_URL")

    # Hidden columns
    hide_author = os.getenv("HIDE_AUTHOR")
    hide_time_to_first_response = os.getenv("HIDE_TIME_TO_FIRST_RESPONSE")
    hide_time_to_close = os.getenv("HIDE_TIME_TO_CLOSE")
    hide_time_to_answer = os.getenv("HIDE_TIME_TO_ANSWER")
    hide_label_metrics = os.getenv("HIDE_LABEL_METRICS")

    return EnvVars(
        search_query,
        gh_token,
        labels_to_measure,
        ignore_users,
        github_server_url,
        hide_author,
        hide_time_to_first_response,
        hide_time_to_close,
        hide_time_to_answer,
        hide_label_metrics
    )
