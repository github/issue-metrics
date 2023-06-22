"""
This module provides functions for working with discussions in a GitHub repository.

Functions:
    get_all_discussions(repo_url: str, token: str) -> List[Dict]:
        Get a list of all discussions in a GitHub repository.

"""
import requests

from common import parse_repository_url


def get_all_discussions(repo_url: str, token: str):
    """Get a list of all discussions in a GitHub repository.

    Args:
        repo_url (str): The URL of the repository to search in.
            ie https://github.com/user/repo
        token (str): A personal access token for GitHub.

    Returns:
        list: A list of all discussions in the repository.

    """
    # Parse the repository owner and name from the URL
    owner, repo = parse_repository_url(repo_url)

    # Construct the GraphQL query
    query = """
    query($owner: String!, $repo: String!) {
        repository(owner: $owner, name: $repo) {
            discussions(first: 100) {
                nodes {
                    id
                    title
                    url
                    createdAt
                    updatedAt
                    author {
                        login
                    }
                }
            }
        }
    }
    """

    # Set the variables for the GraphQL query
    variables = {"owner": owner, "repo": repo}

    # Send the GraphQL request
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": variables},
        headers=headers,
        timeout=60,
    )

    # Check for errors in the GraphQL response
    if response.status_code != 200:
        raise ValueError("GraphQL query failed")

    data = response.json()["data"]

    # Extract the discussions from the GraphQL response
    discussions = []
    for discussion in data["repository"]["discussions"]["nodes"]:
        discussions.append(discussion)

    return discussions
