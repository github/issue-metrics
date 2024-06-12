"""A script for measuring time to first response and time to close for GitHub issues.

This script uses the GitHub API to search for issues/prs/discussions in a repository
and measure the time to first response and time to close for each issue. It then calculates
the average time to first response and time to close and writes the issues with
their metrics to a markdown file.

Functions:
    get_env_vars() -> EnvVars: Get the environment variables for use
        in the script.
    search_issues(search_query: str, github_connection: github3.GitHub, owners_and_repositories: List[dict])
        -> github3.structs.SearchIterator:
        Searches for issues in a GitHub repository that match the given search query.
    get_per_issue_metrics(issues: Union[List[dict], List[github3.issues.Issue]],
        discussions: bool = False), labels: Union[List[str], None] = None,
        ignore_users: List[str] = [] -> tuple[List, int, int]:
        Calculate the metrics for each issue in a list of GitHub issues.
    get_owner(search_query: str) -> Union[str, None]]:
        Get the owner from the search query.
    main(): Run the issue-metrics script.
"""

import shutil
import sys
from time import sleep
from typing import List, Union

import github3
import github3.structs
from auth import auth_to_github, get_github_app_installation_token
from classes import IssueWithMetrics
from config import EnvVars, get_env_vars
from discussions import get_discussions
from json_writer import write_to_json
from labels import get_label_metrics, get_stats_time_in_labels
from markdown_helpers import markdown_too_large_for_issue_body, split_markdown_file
from markdown_writer import write_to_markdown
from most_active_mentors import count_comments_per_user, get_mentor_count
from time_to_answer import get_stats_time_to_answer, measure_time_to_answer
from time_to_close import get_stats_time_to_close, measure_time_to_close
from time_to_first_response import (
    get_stats_time_to_first_response,
    measure_time_to_first_response,
)
from time_to_merge import measure_time_to_merge
from time_to_ready_for_review import get_time_to_ready_for_review


def search_issues(
    search_query: str,
    github_connection: github3.GitHub,
    owners_and_repositories: List[dict],
) -> List[github3.search.IssueSearchResult]:  # type: ignore
    """
    Searches for issues/prs/discussions in a GitHub repository that match
    the given search query and handles errors related to GitHub API responses.

    Args:
        search_query (str): The search query to use for finding issues/prs/discussions.
        github_connection (github3.GitHub): A connection to the GitHub API.
        owners_and_repositories (List[dict]): A list of dictionaries containing
            the owner and repository names.

    Returns:
        List[github3.search.IssueSearchResult]: A list of issues that match the search query.
    """

    # Rate Limit Handling: API only allows 30 requests per minute
    def wait_for_api_refresh(iterator: github3.structs.SearchIterator):
        max_retries = 5
        retry_count = 0
        sleep_time = 70

        while iterator.ratelimit_remaining < 5:
            if retry_count >= max_retries:
                raise RuntimeError("Exceeded maximum retries for API rate limit")

            print(
                f"GitHub API Rate Limit Low, waiting {sleep_time} seconds to refresh."
            )
            sleep(sleep_time)

            # Exponentially increase the sleep time for the next retry
            sleep_time *= 2
            retry_count += 1

    issues_per_page = 100

    print("Searching for issues...")
    issues_iterator = github_connection.search_issues(
        search_query, per_page=issues_per_page
    )
    wait_for_api_refresh(issues_iterator)

    issues = []
    repos_and_owners_string = ""
    for item in owners_and_repositories:
        repos_and_owners_string += (
            f"{item.get('owner', '')}/{item.get('repository', '')} "
        )

    # Print the issue titles
    try:
        for idx, issue in enumerate(issues_iterator, 1):
            print(issue.title)  # type: ignore
            issues.append(issue)

            # requests are sent once per page of issues
            if idx % issues_per_page == 0:
                wait_for_api_refresh(issues_iterator)

    except github3.exceptions.ForbiddenError:
        print(
            f"You do not have permission to view a repository from: '{repos_and_owners_string}'; Check your API Token."
        )
        sys.exit(1)
    except github3.exceptions.NotFoundError:
        print(
            f"The repository could not be found; Check the repository owner and names: '{repos_and_owners_string}"
        )
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


def get_per_issue_metrics(
    issues: Union[List[dict], List[github3.search.IssueSearchResult]],  # type: ignore
    env_vars: EnvVars,
    discussions: bool = False,
    labels: Union[List[str], None] = None,
    ignore_users: Union[List[str], None] = None,
    max_comments_to_eval: int = 20,
    heavily_involved: int = 3,
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
        env_vars (EnvVars): The environment variables for the script.

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
            if env_vars.hide_time_to_first_response is False:
                issue_with_metrics.time_to_first_response = (
                    measure_time_to_first_response(None, issue, ignore_users)
                )
            if env_vars.enable_mentor_count:
                issue_with_metrics.mentor_activity = count_comments_per_user(
                    None,
                    issue,
                    None,
                    None,
                    ignore_users,
                    max_comments_to_eval,
                    heavily_involved,
                )
            if env_vars.hide_time_to_answer is False:
                issue_with_metrics.time_to_answer = measure_time_to_answer(issue)
            if issue["closedAt"]:
                num_issues_closed += 1
                if not env_vars.hide_time_to_close:
                    issue_with_metrics.time_to_close = measure_time_to_close(
                        None, issue
                    )
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

            if env_vars.hide_time_to_first_response is False:
                issue_with_metrics.time_to_first_response = (
                    measure_time_to_first_response(
                        issue, None, pull_request, ready_for_review_at, ignore_users
                    )
                )
            if env_vars.enable_mentor_count:
                issue_with_metrics.mentor_activity = count_comments_per_user(
                    issue,
                    None,
                    pull_request,
                    ready_for_review_at,
                    ignore_users,
                    max_comments_to_eval,
                    heavily_involved,
                )
            if labels and env_vars.hide_label_metrics is False:
                issue_with_metrics.label_metrics = get_label_metrics(issue, labels)
            if issue.state == "closed":  # type: ignore
                num_issues_closed += 1
                if not env_vars.hide_time_to_close:
                    if pull_request:
                        issue_with_metrics.time_to_close = measure_time_to_merge(
                            pull_request, ready_for_review_at
                        )
                    else:
                        issue_with_metrics.time_to_close = measure_time_to_close(
                            issue, None
                        )
            elif issue.state == "open":  # type: ignore
                num_issues_open += 1
        issues_with_metrics.append(issue_with_metrics)

    return issues_with_metrics, num_issues_open, num_issues_closed


def get_owners_and_repositories(
    search_query: str,
) -> List[dict]:
    """Get the owners and repositories from the search query.

    Args:
        search_query (str): The search query used to search for issues.

    Returns:
        List[dict]: A list of dictionaries of owners and repositories.

    """
    search_query_split = search_query.split(" ")
    results_list = []
    for item in search_query_split:
        result = {}
        if "repo:" in item and "/" in item:
            result["owner"] = item.split(":")[1].split("/")[0]
            result["repository"] = item.split(":")[1].split("/")[1]
        if "org:" in item or "owner:" in item or "user:" in item:
            result["owner"] = item.split(":")[1]
        if "user:" in item:
            result["owner"] = item.split(":")[1]
        if "owner:" in item:
            result["owner"] = item.split(":")[1]
        if result:
            results_list.append(result)

    return results_list


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
    hide_items_closed_count = env_vars.hide_items_closed_count

    gh_app_id = env_vars.gh_app_id
    gh_app_installation_id = env_vars.gh_app_installation_id
    gh_app_private_key_bytes = env_vars.gh_app_private_key_bytes

    if not token and gh_app_id and gh_app_installation_id and gh_app_private_key_bytes:
        token = get_github_app_installation_token(
            gh_app_id, gh_app_private_key_bytes, gh_app_installation_id
        )

    # Auth to GitHub.com
    github_connection = auth_to_github(
        gh_app_id,
        gh_app_installation_id,
        gh_app_private_key_bytes,
        token,
        env_vars.ghe,
    )
    enable_mentor_count = env_vars.enable_mentor_count
    min_mentor_count = int(env_vars.min_mentor_comments)
    max_comments_eval = int(env_vars.max_comments_eval)
    heavily_involved_cutoff = int(env_vars.heavily_involved_cutoff)

    # Get the owners and repositories from the search query
    owners_and_repositories = get_owners_and_repositories(search_query)

    # Every search query must include a repository owner for each repository, organization, or user
    for item in owners_and_repositories:
        if item["owner"] is None:
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
        issues = search_issues(search_query, github_connection, owners_and_repositories)
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
        max_comments_to_eval=max_comments_eval,
        heavily_involved=heavily_involved_cutoff,
        env_vars=env_vars,
    )

    stats_time_to_first_response = get_stats_time_to_first_response(issues_with_metrics)
    stats_time_to_close = None
    if num_issues_closed > 0:
        stats_time_to_close = get_stats_time_to_close(issues_with_metrics)

    stats_time_to_answer = get_stats_time_to_answer(issues_with_metrics)

    num_mentor_count = 0
    if enable_mentor_count:
        num_mentor_count = get_mentor_count(issues_with_metrics, min_mentor_count)

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
        hide_items_closed_count,
    )

    max_char_count = 65535
    if markdown_too_large_for_issue_body("issue_metrics.md", max_char_count):
        split_markdown_file("issue_metrics.md", max_char_count)
        shutil.move("issue_metrics.md", "issue_metrics_full.md")
        shutil.move("issue_metrics_0.md", "issue_metrics.md")
        print(
            "Issue metrics markdown file is too large for GitHub issue body and has been \
            split into multiple files. ie. issue_metrics.md, issue_metrics_1.md, etc. \
            The full file is saved as issue_metrics_full.md\n\
            See https://github.com/github/issue-metrics/blob/main/docs/dealing-with-large-issue-metrics.md"
        )


if __name__ == "__main__":
    main()
