"""A module to search for issues in a GitHub repository."""

import sys
from time import sleep
from typing import List

import github3
import github3.structs


def search_issues(
    search_query: str,
    github_connection: github3.GitHub,
    owners_and_repositories: List[dict],
    rate_limit_bypass: bool = False,
) -> List[github3.search.IssueSearchResult]:  # type: ignore
    """
    Searches for issues/prs/discussions in a GitHub repository that match
    the given search query and handles errors related to GitHub API responses.

    Args:
        search_query (str): The search query to use for finding issues/prs/discussions.
        github_connection (github3.GitHub): A connection to the GitHub API.
        owners_and_repositories (List[dict]): A list of dictionaries containing
            the owner and repository names.
        rate_limit_bypass (bool, optional): A flag to bypass the rate limit to be used
            when working with GitHub server that has rate limiting turned off. Defaults to False.

    Returns:
        List[github3.search.IssueSearchResult]: A list of issues that match the search query.
    """

    # Rate Limit Handling: API only allows 30 requests per minute
    def wait_for_api_refresh(
        iterator: github3.structs.SearchIterator, rate_limit_bypass: bool = False
    ):
        # If the rate limit bypass is enabled, don't wait for the API to refresh
        if rate_limit_bypass:
            return

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
    wait_for_api_refresh(issues_iterator, rate_limit_bypass)

    issues = []
    repos_and_owners_string = ""
    for item in owners_and_repositories:
        repos_and_owners_string += (
            f"{item.get('owner', '')}/{item.get('repository', '')} "
        )

    # Print the issue titles and add them to the list of issues
    try:
        for idx, issue in enumerate(issues_iterator, 1):
            print(issue.title)  # type: ignore
            issues.append(issue)

            # requests are sent once per page of issues
            if idx % issues_per_page == 0:
                wait_for_api_refresh(issues_iterator, rate_limit_bypass)

    except github3.exceptions.ForbiddenError:
        print(
            f"You do not have permission to view a repository \
from: '{repos_and_owners_string}'; Check your API Token."
        )
        sys.exit(1)
    except github3.exceptions.NotFoundError:
        print(
            f"The repository could not be found; \
Check the repository owner and names: '{repos_and_owners_string}"
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
