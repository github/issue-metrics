"""A script for measuring time to first response for GitHub issues.

This script uses the GitHub API to search for issues in a repository and measure
the time to first response for each issue. It then calculates the average time
to first response and writes the issues with their time to first response to a
markdown file.

Functions:
    search_issues: Search for issues in a GitHub repository.
    auth_to_github: Authenticate to the GitHub API.
    measure_time_to_first_response: Measure the time to first response for a GitHub issue.
    get_average_time_to_first_response: Calculate the average time to first response for
    a list of issues.
    write_to_markdown: Write the issues with metrics to a markdown file.

"""

import os
from datetime import datetime, timedelta
from os.path import dirname, join
from urllib.parse import urlparse

import github3
from dotenv import load_dotenv


def search_issues(repository_url, issue_search_query, github_connection):
    """
    Searches for issues in a GitHub repository that match the given search query.

    Args:
        repository_url (str): The URL of the repository to search in.
            ie https://github.com/user/repo
        issue_search_query (str): The search query to use for finding issues.
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
    full_query = f"repo:{owner}/{repo} {issue_search_query}"
    issues = github_connection.search_issues(full_query)  # type: ignore

    # Print the issue titles
    for issue in issues:
        print(issue.title)

    return issues


def auth_to_github():
    """Connect to GitHub.com or GitHub Enterprise, depending on env variables."""
    token = os.getenv("GH_TOKEN")
    if token:
        github_connection = github3.login(token=token)
    else:
        raise ValueError("GH_TOKEN environment variable not set")

    return github_connection  # type: ignore


def measure_time_to_first_response(issues):
    """Measure the time to first response for each issue.

    Args:
        issues (list of github3.Issue): A list of GitHub issues.

    Returns:
        list of tuple: A list of tuples containing a GitHub issue
        title, url, and its time to first response.

    Raises:
        TypeError: If the input is not a list of GitHub issues.

    """
    issues_with_metrics = []
    for issue in issues:
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

        # Add the issue to the list of issues with metrics
        issues_with_metrics.append(
            [
                issue.title,
                issue.html_url,
                time_to_first_response,
            ]
        )

    return issues_with_metrics


def get_average_time_to_first_response(issues):
    """Calculate the average time to first response for a list of issues.

    Args:
        issues (list of github3.Issue): A list of GitHub issues with the time to
        first response added as an attribute.

    Returns:
        datetime.timedelta: The average time to first response for the issues in seconds.

    Raises:
        TypeError: If the input is not a list of GitHub issues.

    """
    total_time_to_first_response = 0
    for issue in issues:
        total_time_to_first_response += issue[2].total_seconds()

    average_seconds_to_first_response = total_time_to_first_response / len(
        issues
    )  # type: ignore

    # Print the average time to first response converting seconds to a readable time format
    print(
        f"Average time to first response: {timedelta(seconds=average_seconds_to_first_response)}"
    )

    return timedelta(seconds=average_seconds_to_first_response)


def get_number_of_issues_open(issues):
    """Get the number of issues that were opened.

    Args:
        issues (list of github3.Issue): A list of GitHub issues.

    Returns:
        int: The number of issues that were opened.

    """
    num_issues_opened = 0
    for issue in issues:
        if issue.state == "open":
            num_issues_opened += 1

    return num_issues_opened


def get_number_of_issues_closed(issues):
    """Get the number of issues that were closed.

    Args:
        issues (list of github3.Issue): A list of GitHub issues.

    Returns:
        int: The number of issues that were closed.

    """
    num_issues_closed = 0
    for issue in issues:
        if issue.state == "closed":
            num_issues_closed += 1

    return num_issues_closed


def write_to_markdown(
    issues_with_metrics,
    average_time_to_first_response,
    num_issues_opened,
    num_issues_closed,
    file=None,
):
    """Write the issues with metrics to a markdown file.

    Args:
        issues_with_metrics (list of tuple): A list of tuples containing a GitHub issue
            and its time to first response.
        average_time_to_first_response (datetime.timedelta): The average time to first
            response for the issues.
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
        and not num_issues_opened
        and not num_issues_closed
    ):
        with file or open("issue_metrics.md", "w", encoding="utf-8") as file:
            file.write("no issues found for the given search criteria\n\n")
    else:
        issues_with_metrics.sort(key=lambda x: x[1], reverse=True)
        with file or open("issue_metrics.md", "w", encoding="utf-8") as file:
            file.write("# Issue Metrics\n\n")
            file.write(
                f"Average time to first response: {average_time_to_first_response}\n"
            )
            file.write(f"Number of issues that remain open: {num_issues_opened}\n")
            file.write(f"Number of issues closed: {num_issues_closed}\n")
            file.write(
                f"Total number of issues created: {len(issues_with_metrics)}\n\n"
            )
            file.write("| Title | URL | TTFR |\n")
            file.write("| --- | --- | ---: |\n")
            for title, url, ttfr in issues_with_metrics:
                file.write(f"| {title} | {url} | {ttfr} |\n")
        print("Wrote issue metrics to issue_metrics.md")


def main():
    """Run the issue-metrics script.

    This function authenticates to GitHub, searches for issues using the
    ISSUE_SEARCH_QUERY environment variable, measures the time to first response
    for each issue, calculates the average time to first response, and writes the
    results to a markdown file.

    Raises:
        ValueError: If the ISSUE_SEARCH_QUERY environment variable is not set.
        ValueError: If the REPOSITORY_URL environment variable is not set.
    """

    print("Starting issue-metrics search...")

    # Load env variables from file
    dotenv_path = join(dirname(__file__), ".env")
    load_dotenv(dotenv_path)

    # Auth to GitHub.com
    github_connection = auth_to_github()

    # Get the environment variables for use in the script
    issue_search_query = os.getenv("ISSUE_SEARCH_QUERY")
    if not issue_search_query:
        raise ValueError("ISSUE_SEARCH_QUERY environment variable not set")

    repo_url = os.getenv("REPOSITORY_URL")
    if not repo_url:
        raise ValueError("REPOSITORY_URL environment variable not set")

    # Search for issues
    issues = search_issues(repo_url, issue_search_query, github_connection)
    if len(issues.items) <= 0:
        print("No issues found")
        write_to_markdown(None, None, None, None)

        return
    # Find the time to first response, average, open, and closed issues
    issues_with_ttfr = measure_time_to_first_response(issues)
    average_time_to_first_response = get_average_time_to_first_response(
        issues_with_ttfr
    )
    num_issues_open = get_number_of_issues_open(issues)
    num_issues_closed = get_number_of_issues_closed(issues)

    # Write the results to a markdown file
    write_to_markdown(
        issues_with_ttfr,
        average_time_to_first_response,
        num_issues_open,
        num_issues_closed,
    )


if __name__ == "__main__":
    main()
