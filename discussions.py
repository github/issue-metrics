"""
This module provides functions for working with discussions in a GitHub repository.

Functions:
    get_discussions(repo_url: str, token: str, search_query: str) -> List[Dict]:
        Get a list of discussions in a GitHub repository that match the search query.

"""
import requests


def get_discussions(token: str, search_query: str):
    """Get a list of discussions in a GitHub repository that match the search query.

    Args:
        token (str): A personal access token for GitHub.
        search_query (str): The search query to filter discussions by.

    Returns:
        list: A list of discussions in the repository that match the search query.

    """
    # Construct the GraphQL query
    query = """
    query($query: String!) {
        search(query: $query, type: DISCUSSION, first: 100) {
            edges {
                node {
                    ... on Discussion {
                        title
                        url
                        createdAt
                        comments(first: 1) {
                            nodes {
                                createdAt
                            }
                        }
                        answerChosenAt
                        closedAt
                    }
                }
            }
        }
    }
    """

    # Remove the type:discussions filter from the search query
    search_query = search_query.replace("type:discussions ", "")
    # Set the variables for the GraphQL query
    variables = {"query": search_query}

    # Send the GraphQL request
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": variables},
        headers=headers,
        timeout=60,
    )

    # Check for errors in the GraphQL response
    if response.status_code != 200 or "errors" in response.json():
        raise ValueError("GraphQL query failed")

    data = response.json()["data"]

    # Extract the discussions from the GraphQL response
    discussions = []
    for edge in data["search"]["edges"]:
        discussions.append(edge["node"])

    return discussions
