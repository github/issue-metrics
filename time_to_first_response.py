"""A module for measuring the time it takes to get the first response to a GitHub issue.

This module provides functions for measuring the time it takes to get the first response
to a GitHub issue, as well as calculating the average time to first response for a list
of issues.

Functions:
    measure_time_to_first_response(
        issue: Union[github3.issues.Issue, None],
        discussion: Union[dict, None]
        pull_request: Union[github3.pulls.PullRequest, None],
    ) -> Union[timedelta, None]:
        Measure the time to first response for a single issue or a discussion.
    get_average_time_to_first_response(
        issues: List[IssueWithMetrics]
    ) -> Union[timedelta, None]:
        Calculate the average time to first response for a list of issues with metrics.

"""
from datetime import datetime, timedelta
from typing import List, Union

import github3

from classes import IssueWithMetrics


def measure_time_to_first_response(
    issue: Union[github3.issues.Issue, None],  # type: ignore
    discussion: Union[dict, None],
    pull_request: Union[github3.pulls.PullRequest, None] = None,
    ready_for_review_at: Union[datetime, None] = None,
    ignore_users: List[str] = None,
) -> Union[timedelta, None]:
    """Measure the time to first response for a single issue, pull request, or a discussion.

    Args:
        issue (Union[github3.issues.Issue, None]): A GitHub issue.
        discussion (Union[dict, None]): A GitHub discussion.
        pull_request (Union[github3.pulls.PullRequest, None]): A GitHub pull request.
        ignore_users (List[str]): A list of GitHub usernames to ignore.

    Returns:
        Union[timedelta, None]: The time to first response for the issue/discussion.

    """
    first_review_comment_time = None
    first_comment_time = None
    earliest_response = None
    issue_time = None
    if ignore_users is None:
        ignore_users = []

    # Get the first comment time
    if issue:
        comments = issue.issue.comments(
            number=20, sort="created", direction="asc"
        )  # type: ignore
        for comment in comments:
            if ignore_comment(issue.issue.user, comment.user, ignore_users, comment.created_at, ready_for_review_at):
                continue
            first_comment_time = comment.created_at
            break

        # Check if the issue is actually a pull request
        # so we may also get the first review comment time
        if pull_request:
            review_comments = pull_request.reviews(number=50)  # type: ignore
            for review_comment in review_comments:
                if ignore_comment(issue.issue.user, review_comment.user, ignore_users,
                                  review_comment.submitted_at, ready_for_review_at):
                    continue
                first_review_comment_time = review_comment.submitted_at
                break

        # Figure out the earliest response timestamp
        if first_comment_time and first_review_comment_time:
            earliest_response = min(first_comment_time, first_review_comment_time)
        elif first_comment_time:
            earliest_response = first_comment_time
        elif first_review_comment_time:
            earliest_response = first_review_comment_time
        else:
            return None

        # Get the created_at time for the issue so we can calculate the time to first response
        if ready_for_review_at:
            issue_time = ready_for_review_at
        else:
            issue_time = datetime.fromisoformat(issue.created_at)  # type: ignore

    if discussion and len(discussion["comments"]["nodes"]) > 0:
        earliest_response = datetime.fromisoformat(
            discussion["comments"]["nodes"][0]["createdAt"]
        )
        issue_time = datetime.fromisoformat(discussion["createdAt"])

    # Calculate the time between the issue and the first comment
    if earliest_response and issue_time:
        return earliest_response - issue_time

    return None


def ignore_comment(
    issue_user: github3.users.User,
    comment_user: github3.users.User,
    ignore_users: List[str],
    comment_created_at: datetime,
    ready_for_review_at: Union[datetime, None],
) -> bool:
    """Check if a comment should be ignored."""
    return (
        # ignore comments by IGNORE_USERS
        comment_user.login in ignore_users
        # ignore comments by bots
        or comment_user.type == "Bot"
        # ignore comments by the issue creator
        or comment_user.login == issue_user.login
        # ignore comments created before the issue was ready for review
        or (ready_for_review_at and comment_created_at < ready_for_review_at))


def get_average_time_to_first_response(
    issues: List[IssueWithMetrics],
) -> Union[timedelta, None]:
    """Calculate the average time to first response for a list of issues.

    Args:
        issues (List[IssueWithMetrics]): A list of GitHub issues with metrics attached.

    Returns:
        datetime.timedelta: The average time to first response for the issues in seconds.

    """
    total_time_to_first_response = 0
    none_count = 0
    for issue in issues:
        if issue.time_to_first_response:
            total_time_to_first_response += issue.time_to_first_response.total_seconds()
        else:
            none_count += 1

    if len(issues) - none_count <= 0:
        return None

    average_seconds_to_first_response = total_time_to_first_response / (
        len(issues) - none_count
    )  # type: ignore

    # Print the average time to first response converting seconds to a readable time format
    print(
        f"Average time to first response: {timedelta(seconds=average_seconds_to_first_response)}"
    )

    return timedelta(seconds=average_seconds_to_first_response)
