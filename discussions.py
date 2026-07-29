"""
This module provides functions for working with discussions in a GitHub repository.

Functions:
    get_discussions(github_connection: Github, search_query: str) -> list:
        Get a list of discussions in a GitHub repository that match the search query.

"""

from github import Github


def get_discussions(github_connection: Github, search_query: str):
    """Get a list of discussions in a GitHub repository that match the search query.

    Args:
        github_connection (Github): An authenticated PyGithub connection.
            GitHub Enterprise routing is handled by the connection's base URL.
        search_query (str): The search query to filter discussions by.

    Returns:
        list: A list of discussions in the repository that match the search query.
    """
    # Construct the GraphQL query with pagination
    query = """
    query($query: String!, $cursor: String) {
        search(query: $query, type: DISCUSSION, first: 100, after: $cursor) {
            edges {
                node {
                    ... on Discussion {
                        title
                        url
                        createdAt
                        author {
                            login
                            __typename
                        }
                        # Only the first 100 comments are fetched (no
                        # pagination). MAX_COMMENTS_EVAL defaults to 20, so
                        # this ceiling is not hit in practice; setting it above
                        # 100 would silently cap discussion mentor counts.
                        comments(first: 100) {
                            nodes {
                                createdAt
                                author {
                                    login
                                    __typename
                                }
                            }
                        }
                        answerChosenAt
                        closedAt
                    }
                }
            }
            pageInfo {
                hasNextPage
                endCursor
            }
        }
    }
    """

    # Remove the type:discussions filter from the search query
    search_query = search_query.replace("type:discussions ", "")

    # PyGithub's graphql_query reuses the connection's auth, base URL, and
    # GitHub Enterprise /api/graphql handling, and raises GithubException on
    # HTTP or GraphQL errors.
    discussions = []
    cursor = None

    while True:
        # Set the variables for the GraphQL query
        variables = {"query": search_query, "cursor": cursor}

        # Send the GraphQL request
        _, response_json = github_connection.requester.graphql_query(query, variables)

        data = response_json["data"]

        # Extract the discussions from the current page
        for edge in data["search"]["edges"]:
            discussions.append(edge["node"])

        # Check if there are more pages
        page_info = data["search"]["pageInfo"]
        if not page_info["hasNextPage"]:
            break

        cursor = page_info["endCursor"]

    return discussions
