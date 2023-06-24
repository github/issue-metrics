"""A script for measuring time to first response and time to close for GitHub issues.

This script uses the GitHub API to search for issues/prs/discussions in a repository
and measure the time to first response and time to close for each issue. It then calculates
the average time to first response and time to close and writes the issues with
their metrics to a markdown file.

Functions:
    get_env_vars() -> tuple[str, str]: Get the environment variables for use
        in the script.
    search_issues(search_query: str, github_connection: github3.GitHub)
        -> github3.structs.SearchIterator:
        Searches for issues in a GitHub repository that match the given search query.
    auth_to_github() -> github3.GitHub: Connect to GitHub API with token authentication.
    get_per_issue_metrics(issues: Union[List[dict], List[github3.issues.Issue]],
        discussions: bool = False) -> tuple[List, int, int]:
        Calculate the metrics for each issue in a list of GitHub issues.
    get_repo_owner_and_name(search_query: str) -> tuple[Union[str, None], Union[str, None]]:
        Get the repository owner and name from the search query.
    get_organization(search_query: str) -> Union[str, None]: Get the organization
        from the search query.
    main(): Run the issue-metrics script.
"""

import os
from os.path import dirname, join
from typing import List, Union

import github3
from dotenv import load_dotenv

from discussions import get_discussions
from time_to_close import measure_time_to_close, get_average_time_to_close
from time_to_first_response import (
    measure_time_to_first_response,
    get_average_time_to_first_response,
)
from time_to_answer import measure_time_to_answer, get_average_time_to_answer
from markdown_writer import write_to_markdown
from classes import IssueWithMetrics


def get_env_vars() -> tuple[str, str]:
    """
    Get the environment variables for use in the script.

    Returns:
        str: the search query used to filter issues, prs, and discussions
        str: the github token used to authenticate to github.com
    """
    search_query = os.getenv("SEARCH_QUERY")
    if not search_query:
        raise ValueError("SEARCH_QUERY environment variable not set")

    token = os.getenv("GH_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set")

    return search_query, token


def search_issues(
    search_query: str, github_connection: github3.GitHub
) -> github3.structs.SearchIterator:  # type: ignore
    """
    Searches for issues/prs/discussions in a GitHub repository that match
    the given search query.

    Args:
        search_query (str): The search query to use for finding issues/prs/discussions.
        github_connection (github3.GitHub): A connection to the GitHub API.

    Returns:
        github3.structs.SearchIterator: A list of issues that match the search query.
    """
    print("Searching for issues...")
    issues = github_connection.search_issues(search_query)

    # Print the issue titles
    for issue in issues:
        print(issue.title)  # type: ignore

    return issues


def auth_to_github() -> github3.GitHub:
    """
    Connect to GitHub.com or GitHub Enterprise, depending on env variables.

    Returns:
        github3.GitHub: A github api connection.
    """
    if token := os.getenv("GH_TOKEN"):
        github_connection = github3.login(token=token)
    else:
        raise ValueError("GH_TOKEN environment variable not set")

    return github_connection  # type: ignore


def get_per_issue_metrics(
    issues: Union[List[dict], List[github3.issues.Issue]],  # type: ignore
    discussions: bool = False,
) -> tuple[List, int, int]:
    """
    Calculate the metrics for each issue/pr/discussion in a list provided.

    Args:
        issues (Union[List[dict], List[github3.issues.Issue]]): A list of
            GitHub issues or discussions.
        discussions (bool, optional): Whether the issues are discussions or not.
            Defaults to False.

    Returns:
        tuple[List[IssueWithMetrics], int, int]: A tuple containing a
            list of IssueWithMetrics objects, the number of open issues,
            and the number of closed issues or discussions.

    """
    issues_with_metrics = []
    num_issues_open = 0
    num_issues_closed = 0

    for issue in issues:
        if discussions:
            issue_with_metrics = IssueWithMetrics(
                issue["title"],
                issue["url"],
                None,
                None,
                None,
            )
            issue_with_metrics.time_to_first_response = measure_time_to_first_response(
                None, issue
            )
            issue_with_metrics.time_to_answer = measure_time_to_answer(issue)
            if issue["closedAt"]:
                issue_with_metrics.time_to_close = measure_time_to_close(None, issue)
                num_issues_closed += 1
            else:
                num_issues_open += 1
        else:
            issue_with_metrics = IssueWithMetrics(
                issue.title,  # type: ignore
                issue.html_url,  # type: ignore
                None,
                None,
                None,
            )
            issue_with_metrics.time_to_first_response = measure_time_to_first_response(
                issue, None
            )
            if issue.state == "closed":  # type: ignore
                issue_with_metrics.time_to_close = measure_time_to_close(issue, None)
                num_issues_closed += 1
            elif issue.state == "open":  # type: ignore
                num_issues_open += 1
        issues_with_metrics.append(issue_with_metrics)

    return issues_with_metrics, num_issues_open, num_issues_closed


def get_repo_owner_and_name(
    search_query: str,
) -> tuple[Union[str, None], Union[str, None]]:
    """Get the repository owner and name from the search query.

    Args:
        search_query (str): The search query used to search for issues.

    Returns:
        tuple[Union[str, None], Union[str, None]]: A tuple containing the repository owner and name.

    """
    search_query_split = search_query.split(" ")
    repo_owner, repo_name = None, None
    for item in search_query_split:
        if "repo:" in item and "/" in item:
            repo_owner = item.split(":")[1].split("/")[0]
            repo_name = item.split(":")[1].split("/")[1]

    return repo_owner, repo_name


def get_organization(search_query: str) -> Union[str, None]:
    """Get the organization from the search query.

    Args:
        search_query (str): The search query used to search for issues.

    Returns:
        Union[str, None]: The organization from the search query.

    """
    # Get the organization from the search query
    search_query_split = search_query.split(" ")
    organization = None
    for item in search_query_split:
        if "org:" in item:
            organization = item.split(":")[1]

    return organization


def main():
    """Run the issue-metrics script.

    This function authenticates to GitHub, searches for issues/prs/discussions
    using the SEARCH_QUERY environment variable, measures the time to first response
    and close for each issue, calculates the average time to first response,
    and writes the results to a markdown file.

    Raises:
        ValueError: If the SEARCH_QUERY environment variable is not set.
        ValueError: If the search query does not include a repository owner and name.
    """

    print("Starting issue-metrics search...")

    # Load env variables from file
    dotenv_path = join(dirname(__file__), ".env")
    load_dotenv(dotenv_path)

    # Auth to GitHub.com
    github_connection = auth_to_github()

    # Get the environment variables for use in the script
    env_vars = get_env_vars()
    search_query = env_vars[0]
    token = env_vars[1]

    # Get the repository owner and name from the search query
    owner, repo_name = get_repo_owner_and_name(search_query)
    organization = get_organization(search_query)

    if (owner is None or repo_name is None) and organization is None:
        raise ValueError(
            "The search query must include a repository owner and name \
            (ie. repo:owner/repo) or an organization (ie. org:organization)"
        )

    # Search for issues
    # If type:discussions is in the search_query, search for discussions using get_discussions()
    if "type:discussions" in search_query:
        issues = get_discussions(token, search_query)
        if len(issues) <= 0:
            print("No discussions found")
            write_to_markdown(None, None, None, None, None, None)
            return
    else:
        if owner is None or repo_name is None:
            raise ValueError(
                "The search query for issues/prs must include a repository owner and name \
                (ie. repo:owner/repo)"
            )
        issues = search_issues(search_query, github_connection)
        if len(issues.items) <= 0:
            print("No issues found")
            write_to_markdown(None, None, None, None, None, None)
            return

    # Get all the metrics
    issues_with_metrics, num_issues_open, num_issues_closed = get_per_issue_metrics(
        issues,
        discussions="type:discussions" in search_query,
    )

    average_time_to_first_response = get_average_time_to_first_response(
        issues_with_metrics
    )
    average_time_to_close = None
    if num_issues_closed > 0:
        average_time_to_close = get_average_time_to_close(issues_with_metrics)

    average_time_to_answer = get_average_time_to_answer(issues_with_metrics)

    # Write the results to a markdown file
    write_to_markdown(
        issues_with_metrics,
        average_time_to_first_response,
        average_time_to_close,
        average_time_to_answer,
        num_issues_open,
        num_issues_closed,
    )


if __name__ == "__main__":
    main()
