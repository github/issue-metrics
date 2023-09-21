"""A module for writing GitHub issue metrics to a json file.

Functions:
    write_to_json(
        issues_with_metrics: List[IssueWithMetrics],
        average_time_to_first_response: timedelta,
        average_time_to_close: timedelta,
        average_time_to_answer: timedelta,
        num_issues_opened: int,
        num_issues_closed: int,
        search_query: str,
    ) -> str:
        Write the issues with metrics to a json file.

"""


import json
from datetime import timedelta
import os
from typing import List, Union

from classes import IssueWithMetrics


def write_to_json(
    issues_with_metrics: Union[List[IssueWithMetrics], None],
    average_time_to_first_response: Union[timedelta, None],
    average_time_to_close: Union[timedelta, None],
    average_time_to_answer: Union[timedelta, None],
    average_time_in_labels: Union[dict, None],
    num_issues_opened: Union[int, None],
    num_issues_closed: Union[int, None],
    search_query: str,
) -> str:
    """
    Write the issues with metrics to a JSON file called issue_metrics.json.

    json structure is like following
    {
        "average_time_to_first_response": "2 days, 12:00:00",
        "average_time_to_close": "5 days, 0:00:00",
        "average_time_to_answer": "1 day, 0:00:00",
        "num_items_opened": 2,
        "num_items_closed": 1,
        "total_item_count": 2,
        "issues": [
            {
                "title": "Issue 1",
                "html_url": "https://github.com/owner/repo/issues/1",
                "author": "author",
                "time_to_first_response": "3 days, 0:00:00",
                "time_to_close": "6 days, 0:00:00",
                "time_to_answer": "None",
                "label_metrics": {
                    "bug": "1 day, 16:24:12"
                }
            },
            {
                "title": "Issue 2",
                "html_url": "https://github.com/owner/repo/issues/2",
                "author": "author",
                "time_to_first_response": "2 days, 0:00:00",
                "time_to_close": "4 days, 0:00:00",
                "time_to_answer": "1 day, 0:00:00",
                "label_metrics": {
                }
            },
        ],
        "search_query": "is:issue is:open repo:owner/repo"
    }

    """

    # Ensure issues_with_metrics is not None
    if not issues_with_metrics:
        return ""

    # Create a dictionary with the metrics
    labels_metrics = {}
    if average_time_in_labels:
        for label, time in average_time_in_labels.items():
            labels_metrics[label] = str(time)
    metrics = {
        "average_time_to_first_response": str(average_time_to_first_response),
        "average_time_to_close": str(average_time_to_close),
        "average_time_to_answer": str(average_time_to_answer),
        "average_time_in_labels": labels_metrics,
        "num_items_opened": num_issues_opened,
        "num_items_closed": num_issues_closed,
        "total_item_count": len(issues_with_metrics),
    }

    # Create a list of dictionaries with the issues and metrics
    issues = []
    for issue in issues_with_metrics:
        formatted_label_metrics = {}
        if issue.label_metrics:
            for label, time in issue.label_metrics.items():
                formatted_label_metrics[label] = str(time)
        issues.append(
            {
                "title": issue.title,
                "html_url": issue.html_url,
                "author": issue.author,
                "time_to_first_response": str(issue.time_to_first_response),
                "time_to_close": str(issue.time_to_close),
                "time_to_answer": str(issue.time_to_answer),
                "label_metrics": formatted_label_metrics,
            }
        )

    # Add the issues to the metrics dictionary
    metrics["issues"] = issues

    # Add the search query to the metrics dictionary
    metrics["search_query"] = search_query

    # add output to github action output
    # pylint: disable=unspecified-encoding
    metrics_json = json.dumps(metrics)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as file_handle:
            print(f"metrics={metrics_json}", file=file_handle)

    # Write the metrics to a JSON file
    with open("issue_metrics.json", "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=4)

    return metrics_json
