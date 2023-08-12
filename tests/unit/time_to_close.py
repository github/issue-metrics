"""A module for measuring the time it takes to close a GitHub issue or discussion.

This module provides functions for measuring the time it takes to close a GitHub issue
or discussion, as well as calculating the average time to close for a list of issues.

Functions:
    measure_time_to_close(
        issue: Union[github3.issues.Issue, None],
        discussion: Union[dict, None]
    ) -> Union[timedelta, None]:
        Measure the time it takes to close an issue or discussion.
    get_average_time_to_close(
        issues_with_metrics: List[IssueWithMetrics]
    ) -> Union[timedelta, None]:
        Calculate the average time to close for a list of issues with metrics.

"""
from datetime import datetime, timedelta
from typing import List, Union

import github3

from classes import IssueWithMetrics


def measure_time_to_close(
    issue: Union[github3.issues.Issue, None], discussion: Union[dict, None]  # type: ignore
) -> Union[timedelta, None]:
    """Measure the time it takes to close an issue or discussion.

    Args:
        issue (Union[github3.issues.Issue, None]): A GitHub issue.
        discussion (Union[dict, None]): A GitHub discussion.

    Returns:
        Union[datetime.timedelta, None]: The time it takes to close the issue.

    """
    closed_at, created_at = None, None
    if issue:
        if issue.state != "closed":
            return None
        closed_at = datetime.fromisoformat(issue.closed_at)
        created_at = datetime.fromisoformat(issue.created_at)

    if discussion:
        if discussion["closedAt"] is None:
            return None
        closed_at = datetime.fromisoformat(discussion["closedAt"])
        created_at = datetime.fromisoformat(discussion["createdAt"])

    if closed_at and created_at:
        return closed_at - created_at
    return None


def get_average_time_to_close(
    issues_with_metrics: List[IssueWithMetrics],
) -> Union[timedelta, None]:
    """Calculate the average time to close for a list of issues.

    Args:
        issues_with_metrics (List[IssueWithMetrics]): A list of issues with metrics.
            Each issue should be a issue_with_metrics tuple.

    Returns:
        Union[float, None]: The average time to close for the issues.

    """
    # Filter out issues with no time to close
    issues_with_time_to_close = [
        issue for issue in issues_with_metrics if issue.time_to_close is not None
    ]

    # Calculate the total time to close for all issues
    total_time_to_close = None
    if issues_with_time_to_close:
        total_time_to_close = 0
        for issue in issues_with_time_to_close:
            if issue.time_to_close:
                total_time_to_close += issue.time_to_close.total_seconds()

    # Calculate the average time to close
    num_issues_with_time_to_close = len(issues_with_time_to_close)
    if num_issues_with_time_to_close > 0 and total_time_to_close is not None:
        average_time_to_close = total_time_to_close / num_issues_with_time_to_close
    else:
        return None

    # Print the average time to close converting seconds to a readable time format
    print(f"Average time to close: {timedelta(seconds=average_time_to_close)}")
    return timedelta(seconds=average_time_to_close)
