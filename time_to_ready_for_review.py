"""A module for getting the time a pull request was marked as ready for review
after being in draft mode.

This module provides functions for getting the time a GitHub pull request was
marked as ready for review, if it was formerly in draft mode.

Functions:
    get_time_to_ready_for_review(
        issue: github3.issues.Issue,
        pull_request: github3.pulls.PullRequest
    ) -> Union[datetime, None]:
        If a pull request was formerly a draft, get the time it was marked as
        ready for review.

"""

from datetime import datetime
from typing import Union

import github3


def get_time_to_ready_for_review(
    issue: github3.issues.Issue, pull_request: github3.pulls.PullRequest
) -> Union[datetime, None]:
    """If a pull request was formerly a draft, get the time it was marked as ready
    for review

    Args:
        issue (github3.issues.Issue): A GitHub issue.
        pull_request (github3.pulls.PullRequest): A GitHub pull request.

    Returns:
        Union[datetime, None]: The time the pull request was marked as ready for review
    """
    if pull_request.draft:
        return None

    events = issue.issue.events(number=50)
    for event in events:
        if event.event == "ready_for_review":
            return event.created_at

    return None
