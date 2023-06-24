"""A module for measuring the time it takes to answer a GitHub discussion.

This module provides functions for measuring the time it takes to answer a GitHub
discussion, as well as calculating the average time to answer for a list of discussions.

Functions:
    get_average_time_to_answer(
        issues_with_metrics: List[IssueWithMetrics]
    ) -> Union[timedelta, None]:
        Calculate the average time to answer for a list of issues with metrics.
    measure_time_to_answer(
        discussion: dict
    ) -> Union[timedelta, None]:
        Measure the time it takes to answer a GitHub discussion.

"""
from datetime import datetime, timedelta
from typing import List, Union

from classes import IssueWithMetrics


def get_average_time_to_answer(
    issues_with_metrics: List[IssueWithMetrics],
) -> Union[timedelta, None]:
    """
    Calculate the average time to answer for a list of issues.
    """
    # Filter out issues with no time to answer
    issues_with_time_to_answer = [
        issue for issue in issues_with_metrics if issue.time_to_answer is not None
    ]

    # Calculate the total time to answer for all issues
    total_time_to_answer = None
    if issues_with_time_to_answer:
        total_time_to_answer = 0
        for issue in issues_with_time_to_answer:
            if issue.time_to_answer:
                total_time_to_answer += issue.time_to_answer.total_seconds()

    # Calculate the average time to answer
    num_issues_with_time_to_answer = len(issues_with_time_to_answer)
    if num_issues_with_time_to_answer > 0 and total_time_to_answer is not None:
        average_time_to_answer = total_time_to_answer / num_issues_with_time_to_answer
    else:
        return None

    # Print the average time to answer converting seconds to a readable time format
    print(f"Average time to answer: {timedelta(seconds=average_time_to_answer)}")
    return timedelta(seconds=average_time_to_answer)


def measure_time_to_answer(discussion: dict) -> Union[timedelta, None]:
    """Measure the time to answer for a discussion.

    Args:
        discussion (dict): A discussion object from the GitHub API.

    Returns:
        Union[timedelta, None]: The time to answer for the discussion.

    """
    if not discussion["answerChosenAt"]:
        return None

    if not discussion["createdAt"]:
        return None

    # Get the time to answer
    answer_time = datetime.fromisoformat(discussion["answerChosenAt"])
    created_time = datetime.fromisoformat(discussion["createdAt"])

    return answer_time - created_time
