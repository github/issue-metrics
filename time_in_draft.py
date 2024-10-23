"""
This module contains a function that measures the time a pull request has been in draft state.
"""

from datetime import datetime
from typing import Union

import github3
import pytz


def measure_time_in_draft(
    issue: github3.issues.Issue,
    ready_for_review_at: Union[datetime, None],
) -> Union[datetime, None]:
    """If a pull request has had time in the draft state, return the amount of time it was in draft.

    args:
        issue (github3.issues.Issue): A GitHub issue which has been pre-qualified as a pull request.
        ready_for_review_at (datetime | None): The time the pull request was marked as ready for review.

    returns:
        Union[datetime, None]: The time the pull request was in draft state.
    """
    events = issue.issue.events(number=50)
    try:
        pr_opened_at = None
        for event in events:
            if event.event == "created_at":
                pr_opened_at = event.created_at
        if pr_opened_at and ready_for_review_at:
            return ready_for_review_at - pr_opened_at
        if pr_opened_at and not ready_for_review_at:
            return datetime.now(pytz.utc) - pr_opened_at

    except TypeError as e:
        print(
            f"An error occurred processing review events for {issue.issue.html_url}. \
Perhaps issue contains a ghost user. {e}"
        )
        return None

    return None
