"""
This is the module that contains functions related to authenticating
to GitHub.
"""

import github3
import requests


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


def get_github_app_installation_token(
    gh_app_id: str, gh_app_private_key_bytes: bytes, gh_app_installation_id: str
) -> str | None:
    """
    Get a GitHub App Installation token.
    Args:
        gh_app_id (str): the GitHub App ID
        gh_app_private_key_bytes (bytes): the GitHub App Private Key
        gh_app_installation_id (str): the GitHub App Installation ID
    Returns:
        str: the GitHub App token
    """
    jwt_headers = github3.apps.create_jwt_headers(gh_app_private_key_bytes, gh_app_id)
    url = f"https://api.github.com/app/installations/{gh_app_installation_id}/access_tokens"

    try:
        response = requests.post(url, headers=jwt_headers, json=None, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    return response.json().get("token")
