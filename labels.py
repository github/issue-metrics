""" Functions for calculating time spent in labels. """
from datetime import datetime, timedelta
from typing import List

import github3
import pytz


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


def get_label_metrics(issue: github3.issues.Issue, labels: List[str]) -> dict:  # type: ignore
    """
    Calculate the time spent with the given labels on a given issue.

    Args:
        issue (github3.issues.Issue): A GitHub issue.
        labels (List[str]): A list of labels to measure time spent in.

    Returns:
        dict: A dictionary containing the time spent in each label.
    """
    label_metrics = {}
    label_events = get_label_events(issue, labels)

    for label in labels:
        label_metrics[label] = timedelta(0)

    # If the event is one of the labels we're looking for, add the time to the dictionary
    unlabeled = {}
    for event in label_events:
        if event.event == "labeled":
            if event.label["name"] in labels:
                label_metrics[
                    event.label["name"]
                ] -= event.created_at - datetime.fromisoformat(issue.created_at)
        elif event.event == "unlabeled":
            unlabeled[event.label["name"]] = True
            if event.label["name"] in labels:
                label_metrics[
                    event.label["name"]
                ] += event.created_at - datetime.fromisoformat(issue.created_at)

    for label in labels:
        if label not in unlabeled:
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
