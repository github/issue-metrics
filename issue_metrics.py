"""A script for measuring time to first response and time to close for GitHub issues.

This script uses the GitHub API to search for issues/prs/discussions in a repository
and measure the time to first response and time to close for each issue. It then calculates
the average time to first response and time to close and writes the issues with
their metrics to a markdown file.

Functions:
    get_env_vars() -> EnvVars: Get the environment variables for use
        in the script.
    search_issues(search_query: str, github_connection: github3.GitHub)
        -> github3.structs.SearchIterator:
        Searches for issues in a GitHub repository that match the given search query.
    auth_to_github() -> github3.GitHub: Connect to GitHub API with token authentication.
    get_per_issue_metrics(issues: Union[List[dict], List[github3.issues.Issue]],
        discussions: bool = False), labels: Union[List[str], None] = None,
        ignore_users: List[str] = [] -> tuple[List, int, int]:
        Calculate the metrics for each issue in a list of GitHub issues.
    get_owner(search_query: str) -> Union[str, None]]:
        Get the owner from the search query.
    main(): Run the issue-metrics script.
"""

import sys
from typing import List, Union

import github3
from classes import IssueWithMetrics
from config import get_env_vars
from discussions import get_discussions
from json_writer import write_to_json
from labels import get_label_metrics, get_stats_time_in_labels
from markdown_writer import write_to_markdown
from time_to_answer import get_stats_time_to_answer, measure_time_to_answer
from time_to_close import get_stats_time_to_close, measure_time_to_close
from time_to_first_response import (
    get_stats_time_to_first_response,
    measure_time_to_first_response,
)
from time_to_merge import measure_time_to_merge
from time_to_ready_for_review import get_time_to_ready_for_review

from most_active_mentors import (
    count_comments_per_user,
    get_mentor_count
)
from config import get_env_vars


def search_issues(
    search_query: str, github_connection: github3.GitHub
) -> List[github3.search.IssueSearchResult]:  # type: ignore
    """
    Searches for issues/prs/discussions in a GitHub repository that match
    the given search query and handles errors related to GitHub API responses.

    Args:
        search_query (str): The search query to use for finding issues/prs/discussions.
        github_connection (github3.GitHub): A connection to the GitHub API.

    Returns:
        List[github3.search.IssueSearchResult]: A list of issues that match the search query.
    """
    print("Searching for issues...")
    issues_iterator = github_connection.search_issues(search_query, per_page=100)

    # Print the issue titles
    issues = []
    try:
        for issue in issues_iterator:
            print(issue.title)  # type: ignore
            issues.append(issue)
    except github3.exceptions.ForbiddenError:
        print(
            "You do not have permission to view this repository; Check you API Token."
        )
        sys.exit(1)
    except github3.exceptions.NotFoundError:
        print("The repository could not be found; Check the repository owner and name.")
        sys.exit(1)
    except github3.exceptions.ConnectionError:
        print(
            "There was a connection error; Check your internet connection or API Token."
        )
        sys.exit(1)
    except github3.exceptions.AuthenticationFailed:
        print("Authentication failed; Check your API Token.")
        sys.exit(1)
    except github3.exceptions.UnprocessableEntity:
        print("The search query is invalid; Check the search query.")
        sys.exit(1)

    return issues


def auth_to_github(
    gh_app_id: str,
    gh_app_installation_id: int,
    gh_app_private_key_bytes: bytes,
    token: str,
    ghe: str,
) -> github3.GitHub:
    """
    Connect to GitHub.com or GitHub Enterprise, depending on env variables.

    Returns:
        github3.GitHub: A github api connection.
    """

    if gh_app_id and gh_app_private_key_bytes and gh_app_installation_id:
        gh = github3.github.GitHub()
        gh.login_as_app_installation(
            gh_app_private_key_bytes, gh_app_id, gh_app_installation_id
        )
        github_connection = gh
    elif ghe and token:
        github_connection = github3.github.GitHubEnterprise(ghe, token=token)
    elif token:
        github_connection = github3.login(token=token)
    else:
        raise ValueError(
            "GH_TOKEN or the set of [GH_APP_ID, GH_APP_INSTALLATION_ID, GH_APP_PRIVATE_KEY] environment variables are not set"
        )

    return github_connection  # type: ignore


def get_per_issue_metrics(
    issues: Union[List[dict], List[github3.search.IssueSearchResult]],  # type: ignore
    discussions: bool = False,
    labels: Union[List[str], None] = None,
    ignore_users: Union[List[str], None] = None,
) -> tuple[List, int, int]:
    """
    Calculate the metrics for each issue/pr/discussion in a list provided.

    Args:
        issues (Union[List[dict], List[github3.search.IssueSearchResult]]): A list of
            GitHub issues or discussions.
        discussions (bool, optional): Whether the issues are discussions or not.
            Defaults to False.
        labels (List[str]): A list of labels to measure time spent in. Defaults to empty list.
        ignore_users (List[str]): A list of users to ignore when calculating metrics.

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
                None,
                None,
                None,
            )
            issue_with_metrics.time_to_first_response = measure_time_to_first_response(
                None, issue, ignore_users
            )
            issue_with_metrics.mentor_activity = count_comments_per_user(
                None, issue, ignore_users
                # TODO review arguments max_comments_to_eval, heavily_involved
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
                issue.user["login"],  # type: ignore
                None,
                None,
                None,
                None,
            )

            # Check if issue is actually a pull request
            pull_request, ready_for_review_at = None, None
            if issue.issue.pull_request_urls:  # type: ignore
                pull_request = issue.issue.pull_request()  # type: ignore
                ready_for_review_at = get_time_to_ready_for_review(issue, pull_request)

            issue_with_metrics.time_to_first_response = measure_time_to_first_response(
                issue, None, pull_request, ready_for_review_at, ignore_users
            )
            issue_with_metrics.mentor_activity = count_comments_per_user(
                issue, None, pull_request, ready_for_review_at, ignore_users
            )
            # TODO review arguments max_comments_to_eval, heavily_involved
            if labels:
                issue_with_metrics.label_metrics = get_label_metrics(issue, labels)
            if issue.state == "closed":  # type: ignore
                if pull_request:
                    issue_with_metrics.time_to_close = measure_time_to_merge(
                        pull_request, ready_for_review_at
                    )
                else:
                    issue_with_metrics.time_to_close = measure_time_to_close(
                        issue, None
                    )
                num_issues_closed += 1
            elif issue.state == "open":  # type: ignore
                num_issues_open += 1
        issues_with_metrics.append(issue_with_metrics)

    return issues_with_metrics, num_issues_open, num_issues_closed


def get_owner(
    search_query: str,
) -> Union[str, None]:
    """Get the owner from the search query.

    Args:
        search_query (str): The search query used to search for issues.

    Returns:
        Union[str, None]: The owner.

    """
    search_query_split = search_query.split(" ")
    owner = None
    for item in search_query_split:
        if "repo:" in item and "/" in item:
            owner = item.split(":")[1].split("/")[0]
        if "org:" in item or "owner:" in item or "user:" in item:
            owner = item.split(":")[1]

    return owner


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

    # Get the environment variables for use in the script
    env_vars = get_env_vars()
    search_query = env_vars.search_query
    token = env_vars.gh_token
    ignore_users = env_vars.ignore_users

    # Auth to GitHub.com
    github_connection = auth_to_github(
        env_vars.gh_app_id,
        env_vars.gh_app_installation_id,
        env_vars.gh_app_private_key_bytes,
        token,
        env_vars.ghe,
    )
    min_mentor_count = 10

    # Get the repository owner and name from the search query
    owner = get_owner(search_query)

    if owner is None:
        raise ValueError(
            "The search query must include a repository owner and name \
            (ie. repo:owner/repo), an organization (ie. org:organization), \
            a user (ie. user:login) or an owner (ie. owner:user-or-organization)"
        )

    # Determine if there are label to measure
    labels = env_vars.labels_to_measure

    # Search for issues
    # If type:discussions is in the search_query, search for discussions using get_discussions()
    if "type:discussions" in search_query:
        if labels:
            raise ValueError(
                "The search query for discussions cannot include labels to measure"
            )
        issues = get_discussions(token, search_query)
        if len(issues) <= 0:
            print("No discussions found")
            write_to_markdown(None, None, None, None, None, None, None, None)
            return
    else:
        issues = search_issues(search_query, github_connection)
        if len(issues) <= 0:
            print("No issues found")
            write_to_markdown(None, None, None, None, None, None, None, None)
            return

    # Get all the metrics
    issues_with_metrics, num_issues_open, num_issues_closed = get_per_issue_metrics(
        issues,
        discussions="type:discussions" in search_query,
        labels=labels,
        ignore_users=ignore_users,
    )

    stats_time_to_first_response = get_stats_time_to_first_response(issues_with_metrics)
    stats_time_to_close = None
    if num_issues_closed > 0:
        stats_time_to_close = get_stats_time_to_close(issues_with_metrics)

    stats_time_to_answer = get_stats_time_to_answer(issues_with_metrics)

    num_mentor_count = get_mentor_count(issues_with_metrics, min_mentor_comments)

    # Get stats describing the time in label for each label and store it in a dictionary
    # where the key is the label and the value is the average time
    stats_time_in_labels = get_stats_time_in_labels(issues_with_metrics, labels)

    # Write the results to json and a markdown file
    write_to_json(
        issues_with_metrics,
        stats_time_to_first_response,
        stats_time_to_close,
        stats_time_to_answer,
        stats_time_in_labels,
        num_issues_open,
        num_issues_closed,
        num_mentor_count,
        search_query,
    )
    write_to_markdown(
        issues_with_metrics,
        stats_time_to_first_response,
        stats_time_to_close,
        stats_time_to_answer,
        stats_time_in_labels,
        num_issues_open,
        num_issues_closed,
        num_mentor_count,
        labels,
        search_query,
    )


if __name__ == "__main__":
    main()
