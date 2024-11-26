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
) -> Union[timedelta, None]:
    """If a pull request has had time in the draft state, return the cumulative amount of time it was in draft.

    args:
        issue (github3.issues.Issue): A GitHub issue which has been pre-qualified as a pull request.

    returns:
        Union[timedelta, None]: Total time the pull request has spent in draft state.
    """
    events = issue.events()
    draft_start = None
    total_draft_time = timedelta(0)

    for event in events:
        if event.event == "converted_to_draft":
            draft_start = event.created_at
        elif event.event == "ready_for_review" and draft_start:
            # Calculate draft time for this interval
            total_draft_time += event.created_at - draft_start
            draft_start = None

    # If the PR is currently in draft state, calculate the time in draft up to now
    if draft_start and issue.issue.state == "open":
        total_draft_time += datetime.now(pytz.utc) - draft_start

    return total_draft_time if total_draft_time > timedelta(0) else None


def get_stats_time_in_draft(
    issues_with_metrics: List[IssueWithMetrics],
) -> Union[dict[str, timedelta], None]:
    """
    Calculate stats describing the time in draft for a list of issues.
    """
    # Filter out issues with no time in draft
    issues_with_time_to_draft = [
        issue for issue in issues_with_metrics if issue.time_in_draft is not None
    ]

    # Calculate the total time in draft for all issues
    draft_times = []
    if issues_with_time_to_draft:
        for issue in issues_with_time_to_draft:
            if issue.time_in_draft:
                draft_times.append(issue.time_in_draft.total_seconds())

    # Calculate stats describing time in draft
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

    # Print the average time in draft converting seconds to a readable time format
    print(f"Average time in draft: {timedelta(seconds=average_time_in_draft)}")
    return stats
