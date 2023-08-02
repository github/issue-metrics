""" Functions for calculating time spent in labels. """
from datetime import datetime, timedelta
from typing import List

import github3
import pytz

from classes import IssueWithMetrics


def get_label_events(
    issue: github3.issues.Issue, labels: List[str]  # type: ignore
) -> List[github3.issues.event]:  # type: ignore
    """
    Get the label events for a given issue if the label is of interest.

    Args:
        issue (github3.issues.Issue): A GitHub issue.
        labels (List[str]): A list of labels of interest.

    Returns:
        List[github3.issues.event]: A list of label events for the given issue.
    """
    label_events = []
    for event in issue.issue.events():
        if event.event in ("labeled", "unlabeled") and event.label["name"] in labels:
            label_events.append(event)

    return label_events


def get_label_metrics(issue: github3.issues.Issue, labels: List[str]) -> dict:
    """
    Calculate the time spent with the given labels on a given issue.

    Args:
        issue (github3.issues.Issue): A GitHub issue.
        labels (List[str]): A list of labels to measure time spent in.

    Returns:
        dict: A dictionary containing the time spent in each label or None.
    """
    label_metrics = {}
    label_events = get_label_events(issue, labels)

    for label in labels:
        label_metrics[label] = None

    # If the event is one of the labels we're looking for, add the time to the dictionary
    unlabeled = {}
    labeled = {}
    if not label_events:
        return label_metrics

    # Calculate the time to add or subtract to the time spent in label based on the label events
    for event in label_events:
        if event.event == "labeled":
            labeled[event.label["name"]] = True
            if event.label["name"] in labels:
                if label_metrics[event.label["name"]] is None:
                    label_metrics[event.label["name"]] = timedelta(0)
                label_metrics[
                    event.label["name"]
                ] -= event.created_at - datetime.fromisoformat(issue.created_at)
        elif event.event == "unlabeled":
            unlabeled[event.label["name"]] = True
            if event.label["name"] in labels:
                if label_metrics[event.label["name"]] is None:
                    label_metrics[event.label["name"]] = timedelta(0)
                label_metrics[
                    event.label["name"]
                ] += event.created_at - datetime.fromisoformat(issue.created_at)

    for label in labels:
        # if the label is still on there, add the time from the last event to now
        if label in labeled and label not in unlabeled:
            # if the issue is closed, add the time from the issue creation to the closed_at time
            if issue.state == "closed":
                label_metrics[label] += datetime.fromisoformat(
                    issue.closed_at
                ) - datetime.fromisoformat(issue.created_at)
            else:
                # if the issue is open, add the time from the issue creation to now
                label_metrics[label] += datetime.now(pytz.utc) - datetime.fromisoformat(
                    issue.created_at
                )

    return label_metrics


def get_average_time_in_labels(
    issues_with_metrics: List[IssueWithMetrics],
    labels: List[str],
) -> dict[str, timedelta]:
    """Calculate the average time spent in each label."""
    average_time_in_labels = {}
    number_of_issues_in_labels = {}
    for issue in issues_with_metrics:
        if issue.label_metrics:
            for label in issue.label_metrics:
                if issue.label_metrics[label] is None:
                    continue
                if label not in average_time_in_labels:
                    average_time_in_labels[label] = issue.label_metrics[label]
                    number_of_issues_in_labels[label] = 1
                else:
                    average_time_in_labels[label] += issue.label_metrics[label]
                    number_of_issues_in_labels[label] += 1

    for label in average_time_in_labels:
        average_time_in_labels[label] = (
            average_time_in_labels[label] / number_of_issues_in_labels[label]
        )

    for label in labels:
        if label not in average_time_in_labels:
            average_time_in_labels[label] = None

    return average_time_in_labels
