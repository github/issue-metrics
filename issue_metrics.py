import os
from datetime import datetime
from os.path import dirname, join
from urllib.parse import urlparse

import github3
from dotenv import load_dotenv


def search_issues(repository_url, issue_search_query, github_connection):
    """
    Searches for issues in a GitHub repository that match the given search query.

    Args:
        repository_url (str): The URL of the repository to search in.
        issue_search_query (str): The search query to use for finding issues.
        github_connection (github3.GitHub): A connection to the GitHub API.

    Returns:
        List[github3.issues.Issue]: A list of issues that match the search query.
    """
    # Parse the repository owner and name from the URL
    parsed_url = urlparse(repository_url)
    path = parsed_url.path.strip("/")

    # Split the path into owner and repo
    owner, repo = path.split("/")

    # Get the repository object
    repo = github_connection.repository(owner, repo)  # type: ignore

    # Search for issues that match the query
    issues = repo.search_issues(issue_search_query)  # type: ignore

    # Print the issue titles
    for issue in issues:
        print(issue.title)

    return issues


def auth_to_github():
    """Connect to GitHub.com or GitHub Enterprise, depending on env variables."""
    token = os.getenv("GH_TOKEN")
    if token:
        github_connection = github3.login(token=os.getenv("GH_TOKEN"))
    else:
        raise ValueError("GH_TOKEN environment variable not set")

    if not github_connection:
        raise ValueError("Unable to authenticate to GitHub")
    return github_connection  # type: ignore


def measure_time_to_first_response(issues):
    """Measure the time to first response for each issue.

    Args:
        issues (list of github3.Issue): A list of GitHub issues.

    Returns:
        list of github3.Issue: A list of GitHub issues with the time to first response
        added as an attribute.

    Raises:
        TypeError: If the input is not a list of GitHub issues.

    """
    issues_with_metrics = []
    for issue in issues:
        # Get the first comment
        first_comment = issue.comments()[0]  # type: ignore

        # Get the created_at time for the first comment
        first_comment_time = datetime.fromisoformat(first_comment.created_at)  # type: ignore

        # Get the created_at time for the issue
        issue_time = datetime.fromisoformat(issue.created_at)  # type: ignore

        # Calculate the time between the issue and the first comment
        time_to_first_response = first_comment_time - issue_time

        # Add the time to the issue
        issue.time_to_first_response = time_to_first_response

        # Add the issue to the list of issues with metrics
        issues_with_metrics.append(issue)

    return issues_with_metrics


def get_average_time_to_first_response(issues):
    """Calculate the average time to first response for a list of issues.

    Args:
        issues (list of github3.Issue): A list of GitHub issues with the time to
        first response added as an attribute.

    Returns:
        datetime.timedelta: The average time to first response for the issues.

    Raises:
        TypeError: If the input is not a list of GitHub issues.

    """
    total_time_to_first_response = 0
    for issue in issues:
        total_time_to_first_response += issue.time_to_first_response.total_seconds()

    average_time_to_first_response = total_time_to_first_response / len(
        issues
    )  # type: ignore

    return average_time_to_first_response


def write_to_markdown(issues_with_metrics, average_time_to_first_response, file=None):
    """Write the issues with metrics to a markdown file.

    Args:
        issues_with_metrics (list of tuple): A list of tuples containing a GitHub issue
        and its time to first response.
        average_time_to_first_response (datetime.timedelta): The average time to first
        response for the issues.
        file (file object, optional): The file object to write to. If not provided,
        a file named "issue_metrics.md" will be created.

    Returns:
        None.

    """
    issues_with_metrics.sort(key=lambda x: x[1], reverse=True)
    with file or open("issue_metrics.md", "w", encoding="utf-8") as file:
        file.write("# Issue Metrics\n\n")
        file.write(
            f"Average time to first response: {average_time_to_first_response}\n"
        )
        file.write(f"Number of issues: {len(issues_with_metrics)}\n\n")
        file.write("| Issue | TTFR |\n")
        file.write("| --- | ---: |\n")
        for issue, ttfr in issues_with_metrics:
            file.write(f"| {issue} | {ttfr} |\n")
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

    issue_search_query = os.getenv("REPOSITORY_URL")
    if not issue_search_query:
        raise ValueError("REPOSITORY_URL environment variable not set")

    # Search for issues
    issues = search_issues(issue_search_query, issue_search_query, github_connection)

    # Print the number of issues found
    print(f"Found {len(issues)} issues")

    # Find the time to first response
    issues_with_ttfr = measure_time_to_first_response(issues)
    average_time_to_first_response = get_average_time_to_first_response(
        issues_with_ttfr
    )

    # Print the average time to first response
    print(f"Average time to first response: {average_time_to_first_response}")

    # Write the results to a markdown file
    write_to_markdown(issues_with_ttfr, average_time_to_first_response)


if __name__ == "__main__":
    main()
