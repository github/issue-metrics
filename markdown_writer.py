"""A module for writing GitHub issue metrics to a markdown file.

This module provides a function for writing a list of GitHub issues with metrics
to a markdown file. The metrics include the average time to first response, the
average time to close, and the average time to answer the discussions. The module
also provides functions for sorting the issues by time to first response.

Functions:
    write_to_markdown(
        issues_with_metrics: List[IssueWithMetrics],
        average_time_to_first_response: timedelta,
        average_time_to_close: timedelta,
        average_time_to_answer: timedelta,
        num_issues_opened: int,
        num_issues_closed: int,
        file: file object = None
    ) -> None:
        Write the issues with metrics to a markdown file.

"""
from datetime import timedelta
from typing import List, Union

from classes import IssueWithMetrics


def write_to_markdown(
    issues_with_metrics: Union[List[IssueWithMetrics], None],
    average_time_to_first_response: Union[timedelta, None],
    average_time_to_close: Union[timedelta, None],
    average_time_to_answer: Union[timedelta, None],
    num_issues_opened: Union[int, None],
    num_issues_closed: Union[int, None],
    file=None,
) -> None:
    """Write the issues with metrics to a markdown file.

    Args:
        issues_with_metrics (IssueWithMetrics): A list of GitHub issues with metrics
        average_time_to_first_response (datetime.timedelta): The average time to first
            response for the issues.
        average_time_to_close (datetime.timedelta): The average time to close for the issues.
        average_time_to_answer (datetime.timedelta): The average time to answer the discussions.
        file (file object, optional): The file object to write to. If not provided,
            a file named "issue_metrics.md" will be created.
        num_issues_opened (int): The number of issues that remain opened.
        num_issues_closed (int): The number of issues that were closed.

    Returns:
        None.

    """
    if not issues_with_metrics or len(issues_with_metrics) == 0:
        with file or open("issue_metrics.md", "w", encoding="utf-8") as file:
            file.write("no issues found for the given search criteria\n\n")
    else:
        # Sort the issues by time to first response
        issues_with_metrics.sort(
            key=lambda x: x.time_to_first_response or timedelta.max
        )
        with file or open("issue_metrics.md", "w", encoding="utf-8") as file:
            file.write("# Issue Metrics\n\n")
            file.write("| Metric | Value |\n")
            file.write("| --- | ---: |\n")
            file.write(
                f"| Average time to first response | {average_time_to_first_response} |\n"
            )
            file.write(f"| Average time to close | {average_time_to_close} |\n")
            file.write(f"| Average time to answer | {average_time_to_answer} |\n")
            file.write(f"| Number of issues that remain open | {num_issues_opened} |\n")
            file.write(f"| Number of issues closed | {num_issues_closed} |\n")
            file.write(
                f"| Total number of issues created | {len(issues_with_metrics)} |\n\n"
            )
            file.write(
                "| Title | URL | Time to first response | Time to close | Time to answer |\n"
            )
            file.write("| --- | --- | ---: | ---: | ---: |\n")
            for issue in issues_with_metrics:
                file.write(
                    f"| "
                    f"{issue.title} | "
                    f"{issue.html_url} | "
                    f"{issue.time_to_first_response} |"
                    f" {issue.time_to_close} |"
                    f" {issue.time_to_answer} |"
                    f"\n"
                )
        print("Wrote issue metrics to issue_metrics.md")
