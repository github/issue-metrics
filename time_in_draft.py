"""
This module contains a function that measures the time a pull request has been in draft state.
"""

from datetime import datetime, timedelta
from typing import List, Union

import github3
import numpy
import pytz
from classes import IssueWithMetrics


def measure_time_in_draft(
    issue: github3.issues.Issue,
    ready_for_review_at: Union[datetime, None],
) -> Union[datetime, None]:
    """If a pull request has had time in the draft state, return the amount of time it was in draft.

    args:
        issue (github3.issues.Issue): A GitHub issue which has been pre-qualified as a pull request.
        ready_for_review_at (datetime | None): The time the pull request was marked as
            ready for review.

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


def get_stats_time_in_draft(
    issues_with_metrics: List[IssueWithMetrics],
) -> Union[dict[str, timedelta], None]:
    """
    Calculate stats describing the time in draft for a list of issues.
    """
    # Filter out issues with no time to answer
    issues_with_time_to_draft = [
        issue for issue in issues_with_metrics if issue.time_in_draft is not None
    ]

    # Calculate the total time in draft for all issues
    draft_times = []
    if issues_with_time_to_draft:
        for issue in issues_with_time_to_draft:
            if issue.time_in_draft:
                draft_times.append(issue.time_in_draft.total_seconds())

    # Calculate stats describing time to answer
    num_issues_with_time_in_draft = len(issues_with_time_to_draft)
    if num_issues_with_time_in_draft > 0:
        average_time_in_draft = numpy.round(numpy.average(draft_times))
        med_time_in_draft = numpy.round(numpy.median(draft_times))
        ninety_percentile_time_in_draft = numpy.round(
            numpy.percentile(draft_times, 90, axis=0)
        )
    else:
        return None

    stats = {
        "avg": timedelta(seconds=average_time_in_draft),
        "med": timedelta(seconds=med_time_in_draft),
        "90p": timedelta(seconds=ninety_percentile_time_in_draft),
    }

    # Print the average time to answer converting seconds to a readable time format
    print(f"Average time to answer: {timedelta(seconds=average_time_in_draft)}")
    return stats
