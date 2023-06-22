"""
Common functions that any file in this repository might use.
"""


from urllib.parse import urlparse


def parse_repository_url(repository_url: str) -> tuple[str, str]:
    """Parse the repository owner and name from a GitHub repository URL.

    Args:
        repository_url (str): The URL of the GitHub repository.

    Returns:
        tuple: A tuple containing the owner and name of the repository.

    """
    # Parse the repository owner and name from the URL
    parsed_url = urlparse(repository_url)
    path = parsed_url.path.strip("/")
    # Split the path into owner and repo
    owner, repo = path.split("/")
    return owner, repo
