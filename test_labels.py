""" Unit tests for labels.py """
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import github3
import pytz
from classes import IssueWithMetrics

from labels import get_average_time_in_labels, get_label_events, get_label_metrics


class TestLabels(unittest.TestCase):
    """Unit tests for labels.py"""

    def setUp(self):
        self.issue = MagicMock()  # type: ignore
        self.issue.issue = MagicMock(spec=github3.issues.Issue)  # type: ignore
        self.issue.created_at = "2020-01-01T00:00:00Z"
        self.issue.closed_at = "2021-01-05T00:00:00Z"
        self.issue.state = "closed"
        self.issue.issue.events.return_value = [
            MagicMock(
                event="labeled",
                label={"name": "bug"},
                created_at=datetime(2021, 1, 1, tzinfo=pytz.UTC),
            ),
            MagicMock(
                event="labeled",
                label={"name": "feature"},
                created_at=datetime(2021, 1, 2, tzinfo=pytz.UTC),
            ),
            MagicMock(
                event="unlabeled",
                label={"name": "bug"},
                created_at=datetime(2021, 1, 3, tzinfo=pytz.UTC),
            ),
        ]

    def test_get_label_events(self):
        """Test get_label_events"""
        labels = ["bug"]
        events = get_label_events(self.issue, labels)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].label["name"], "bug")
        self.assertEqual(events[1].label["name"], "bug")

    def test_get_label_metrics_closed_issue(self):
        """Test get_label_metrics using a closed issue"""
        labels = ["bug", "feature"]
        metrics = get_label_metrics(self.issue, labels)
        self.assertEqual(metrics["bug"], timedelta(days=2))
        self.assertEqual(metrics["feature"], timedelta(days=3))

    def test_get_label_metrics_open_issue(self):
        """Test get_label_metrics using an open issue"""
        self.issue.state = "open"
        labels = ["bug", "feature"]
        metrics = get_label_metrics(self.issue, labels)
        self.assertEqual(metrics["bug"], timedelta(days=2))
        self.assertLessEqual(
            metrics["feature"],
            datetime.now(pytz.utc) - datetime(2021, 1, 2, tzinfo=pytz.UTC),
        )
        self.assertGreater(
            metrics["feature"],
            datetime.now(pytz.utc) - datetime(2021, 1, 4, tzinfo=pytz.UTC),
        )


class TestGetAverageTimeInLabels(unittest.TestCase):
    """Unit tests for get_average_time_in_labels"""

    def setUp(self):
        self.issues_with_metrics = MagicMock()
        self.issues_with_metrics = [
            IssueWithMetrics(
                "issue1", "url1", "alice", None, None, None, {"bug": timedelta(days=2)}
            ),
        ]

    def test_get_average_time_in_labels(self):
        """Test get_average_time_in_labels"""
        labels = ["bug", "feature"]
        metrics = get_average_time_in_labels(self.issues_with_metrics, labels)
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics["bug"], timedelta(days=2))
        self.assertIsNone(metrics.get("feature"))


if __name__ == "__main__":
    unittest.main()
