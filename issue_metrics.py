"""A script for measuring time to first response and time to close for GitHub issues.

This script uses the GitHub API to search for issues in a repository and measure
the time to first response and time to close for each issue. It then calculates
the average time to first response and time to close and writes the issues with
their metrics to a markdown file.

Functions:
    search_issues: Search for issues in a GitHub repository.
    auth_to_github: Authenticate to the GitHub API.
    measure_time_to_first_response: Measure the time to first response for a GitHub issue.
    get_average_time_to_first_response: Calculate the average time to first response for
        a list of issues.
    measure_time_to_close: Measure the time to close for a GitHub issue.
    get_average_time_to_close: Calculate the average time to close for a list of issues.
    write_to_markdown: Write the issues with metrics to a markdown file.

"""

import os
from datetime import datetime, timedelta
from os.path import dirname, join
from urllib.parse import urlparse
from typing import List

import github3

# IssueWithMetrics is a type alias for a GitHub issue with metrics attached.
from github3.issues.issue import Issue as IssueWithMetrics
from dotenv import load_dotenv



def search_issues(
    repository_url: str,
    search_query: str,
    github_connection: github3.GitHub
) -> List[github3.issues.Issue]:
    """
    Searches for issues in a GitHub repository that match the given search query.

    Args:
        repository_url (str): The URL of the repository to search in.
            ie https://github.com/user/repo
        search_query (str): The search query to use for finding issues.
        github_connection (github3.GitHub): A connection to the GitHub API.

    Returns:
        List[github3.issues.Issue]: A list of issues that match the search query.
    """
    print("Searching for issues...")
    # Parse the repository owner and name from the URL
    parsed_url = urlparse(repository_url)
    path = parsed_url.path.strip("/")
    print(f"parsing URL: {repository_url}")
    # Split the path into owner and repo
    owner, repo = path.split("/")
    print(f"owner: {owner}, repo: {repo}")

    # Search for issues that match the query
    full_query = f"repo:{owner}/{repo} {search_query}"
    issues = github_connection.search_issues(full_query)  # type: ignore

    # Print the issue titles
    for issue in issues:
        print(issue.title)

    return issues


def auth_to_github() -> github3.GitHub | None:
    """
    Connect to GitHub.com or GitHub Enterprise, depending on env variables.

    Returns:
        github3.GitHub: A github api connection.
    """
    token = os.getenv("GH_TOKEN")
    if token:
        github_connection = github3.login(token=token)
    else:
        raise ValueError("GH_TOKEN environment variable not set")

    return github_connection  # type: ignore


def measure_time_to_first_response(issue: github3.issues.Issue) -> timedelta:
    """Measure the time to first response for a single issue.

    Args:
        issue (github3.issues.Issue): A GitHub issue.

    Returns:
        time to first response (datetime.timedelta): The time to first response for the issue.

    """
    # Get the first comment
    if issue.comments <= 0:
        first_comment_time = None
        time_to_first_response = None
    else:
        comments = issue.issue.comments(
            number=1, sort="created", direction="asc"
        )  # type: ignore
        for comment in comments:
            # Get the created_at time for the first comment
            first_comment_time = comment.created_at  # type: ignore

        # Get the created_at time for the issue
        issue_time = datetime.fromisoformat(issue.created_at)  # type: ignore

        # Calculate the time between the issue and the first comment
        time_to_first_response = first_comment_time - issue_time  # type: ignore

    return time_to_first_response


def measure_time_to_close(issue: github3.issues.Issue) -> timedelta:
    """Measure the time it takes to close an issue.

    Args:
        issue (github3.Issue): A GitHub issue.

    Returns:
        datetime.timedelta: The time it takes to close the issue.

    """
    if issue.state != "closed":
        raise ValueError("Issue must be closed to measure time to close.")

    closed_at = datetime.fromisoformat(issue.closed_at)
    created_at = datetime.fromisoformat(issue.created_at)

    time_to_close = closed_at - created_at

    return time_to_close


def get_average_time_to_first_response(issues: List[IssueWithMetrics]) -> timedelta:
    """Calculate the average time to first response for a list of issues.

    Args:
        issues (List[IssueWithMetrics]): A list of GitHub issues with metrics attached.

    Returns:
        datetime.timedelta: The average time to first response for the issues in seconds.

    """
    total_time_to_first_response = 0
    none_count = 0
    for issue in issues:
        if issue.time_to_first_response:
            total_time_to_first_response += issue.time_to_first_response.total_seconds()
        else:
            none_count += 1

    average_seconds_to_first_response = total_time_to_first_response / (
        len(issues) - none_count
    )  # type: ignore

    # Print the average time to first response converting seconds to a readable time format
    print(
        f"Average time to first response: {timedelta(seconds=average_seconds_to_first_response)}"
    )

    return timedelta(seconds=average_seconds_to_first_response)


def write_to_markdown(
    issues_with_metrics: List[IssueWithMetrics],
    average_time_to_first_response: timedelta,
    average_time_to_close: timedelta,
    num_issues_opened: int,
    num_issues_closed: int,
    file=None
) -> None:
    """Write the issues with metrics to a markdown file.

    Args:
        issues_with_metrics (IssueWithMetrics): A list of GitHub issues with metrics
        average_time_to_first_response (datetime.timedelta): The average time to first
            response for the issues.
        average_time_to_close (datetime.timedelta): The average time to close for the issues.
        file (file object, optional): The file object to write to. If not provided,
            a file named "issue_metrics.md" will be created.
        num_issues_opened (int): The number of issues that remain opened.
        num_issues_closed (int): The number of issues that were closed.

    Returns:
        None.

    """
    if (
        not issues_with_metrics
        and not average_time_to_first_response
        and not average_time_to_close
        and not num_issues_opened
        and not num_issues_closed
    ):
        with file or open("issue_metrics.md", "w", encoding="utf-8") as file:
            file.write("no issues found for the given search criteria\n\n")
    else:
        # Sort the issues by time to first response
        issues_with_metrics.sort(
            key=lambda x: x.time_to_first_response or timedelta.max
        )
        with file or open("issue_metrics.md", "w", encoding="utf-8") as file:
            file.write("# Issue Metrics\n\n")
            file.write("| Metric | Value |\n")
            file.write("| --- | ---: |\n")
            file.write(
                f"| Average time to first response | {average_time_to_first_response} |\n"
            )
            file.write(f"| Average time to close | {average_time_to_close} |\n")
            file.write(f"| Number of issues that remain open | {num_issues_opened} |\n")
            file.write(f"| Number of issues closed | {num_issues_closed} |\n")
            file.write(
                f"| Total number of issues created | {len(issues_with_metrics)} |\n\n"
            )
            file.write("| Title | URL | Time to first response | Time to close \n")
            file.write("| --- | --- | ---: | ---: |\n")
            for issue in issues_with_metrics:
                file.write(
                    f"| "
                    f"{issue.title} | "
                    f"{issue.html_url} | "
                    f"{issue.time_to_first_response} |"
                    f" {issue.time_to_close} |"
                    f"\n"
                )
        print("Wrote issue metrics to issue_metrics.md")


def get_average_time_to_close(issues_with_metrics: List[IssueWithMetrics]) -> timedelta:
    """Calculate the average time to close for a list of issues.

    Args:
        issues_with_metrics (List[IssueWithMetrics]): A list of issues with metrics.
            Each issue should be a issue_with_metrics tuple.

    Returns:
        datetime.timedelta: The average time to close for the issues.

    """
    # Filter out issues with no time to close
    issues_with_time_to_close = [
        issue for issue in issues_with_metrics if issue.time_to_close is not None
    ]

    # Calculate the total time to close for all issues
    total_time_to_close = sum(
        [issue.time_to_close for issue in issues_with_time_to_close], timedelta()
    )

    # Calculate the average time to close
    num_issues_with_time_to_close = len(issues_with_time_to_close)
    if num_issues_with_time_to_close > 0:
        average_time_to_close = total_time_to_close / num_issues_with_time_to_close
    else:
        average_time_to_close = None

    # Print the average time to close converting seconds to a readable time format
    print(f"Average time to close: {average_time_to_close}")
    return average_time_to_close


def main():
    """Run the issue-metrics script.

    This function authenticates to GitHub, searches for issues using the
    SEARCH_QUERY environment variable, measures the time to first response
    and close for each issue, calculates the average time to first response,
    and writes the results to a markdown file.

    Raises:
        ValueError: If the SEARCH_QUERY environment variable is not set.
        ValueError: If the REPOSITORY_URL environment variable is not set.
    """

    print("Starting issue-metrics search...")

    # Load env variables from file
    dotenv_path = join(dirname(__file__), ".env")
    load_dotenv(dotenv_path)

    # Auth to GitHub.com
    github_connection = auth_to_github()

    # Get the environment variables for use in the script
    search_query, repo_url = get_env_vars()

    # Search for issues
    issues = search_issues(repo_url, search_query, github_connection)
    if len(issues.items) <= 0:
        print("No issues found")
        write_to_markdown(None, None, None, None, None)
        return

    # Find the time to first response, time to close, average, open, and closed issues
    issues_with_metrics = []
    num_issues_open = 0
    num_issues_closed = 0

    for issue in issues:
        issue_with_metrics = IssueWithMetrics(
            issue.title,  # type: ignore
            issue.html_url,  # type: ignore
            None,
            None,
        )
        issue_with_metrics.time_to_first_response = measure_time_to_first_response(
            issue
        )
        if issue.state == "closed":  # type: ignore
            issue_with_metrics.time_to_close = measure_time_to_close(issue)  # type: ignore
        if issue.state == "open":  # type: ignore
            num_issues_open += 1
        if issue.state == "closed":  # type: ignore
            num_issues_closed += 1
        issues_with_metrics.append(issue_with_metrics)

    average_time_to_first_response = get_average_time_to_first_response(
        issues_with_metrics
    )
    average_time_to_close = None
    if num_issues_closed > 0:
        average_time_to_close = get_average_time_to_close(issues_with_metrics)

    # Write the results to a markdown file
    write_to_markdown(
        issues_with_metrics,
        average_time_to_first_response,
        average_time_to_close,
        num_issues_open,
        num_issues_closed,
    )


def get_env_vars() -> tuple[str, str]:
    """
    Get the environment variables for use in the script.

    Returns:
        str: the search query used to filter issues and prs
        str: the full url of the repo to search
    """
    search_query = os.getenv("SEARCH_QUERY")
    if not search_query:
        raise ValueError("SEARCH_QUERY environment variable not set")

    repo_url = os.getenv("REPOSITORY_URL")
    if not repo_url:
        raise ValueError("REPOSITORY_URL environment variable not set")
    return search_query, repo_url


class IssueWithMetrics:
    """A class to represent a GitHub issue with metrics."""

    def __init__(
        self, title, html_url, time_to_first_response=None, time_to_close=None
    ):
        self.title = title
        self.html_url = html_url
        self.time_to_first_response = time_to_first_response
        self.time_to_close = time_to_close


if __name__ == "__main__":
    main()
