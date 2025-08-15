"""Unit tests for labels.py"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import github3
import pytz
from classes import IssueWithMetrics
from labels import get_label_events, get_label_metrics, get_stats_time_in_labels


class TestLabels(unittest.TestCase):
    """Unit tests for labels.py"""

    def setUp(self):
        self.issue = MagicMock()  # type: ignore
        self.issue.issue = MagicMock(spec=github3.issues.Issue)  # type: ignore
        self.issue.created_at = "2021-01-01T00:00:00Z"
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
            MagicMock(
                event="labeled",
                label={"name": "bug"},
                created_at=datetime(2021, 1, 4, tzinfo=pytz.UTC),
            ),
            # Label labeled after issue close date
            MagicMock(
                event="labeled",
                label={"name": "foo"},
                created_at=datetime(2021, 1, 20, tzinfo=pytz.UTC),
            ),
        ]

    def test_get_label_events(self):
        """Test get_label_events"""
        labels = ["bug"]
        events = get_label_events(self.issue, labels)
        self.assertEqual(len(events), 3)
        self.assertEqual(events[0].label["name"], "bug")
        self.assertEqual(events[1].label["name"], "bug")
        self.assertEqual(events[2].label["name"], "bug")

    def test_get_label_metrics_closed_issue(self):
        """Test get_label_metrics using a closed issue"""
        labels = ["bug", "feature"]
        metrics = get_label_metrics(self.issue, labels)
        self.assertEqual(metrics["bug"], timedelta(days=3))
        self.assertEqual(metrics["feature"], timedelta(days=3))

    def test_get_label_metrics_open_issue(self):
        """Test get_label_metrics using an open issue"""
        self.issue.state = "open"
        labels = ["bug", "feature"]
        metrics = get_label_metrics(self.issue, labels)
        self.assertLessEqual(
            metrics["bug"],
            datetime.now(pytz.utc) - datetime(2021, 1, 2, tzinfo=pytz.UTC),
        )
        self.assertGreater(
            metrics["bug"],
            datetime.now(pytz.utc) - datetime(2021, 1, 3, tzinfo=pytz.UTC),
        )
        self.assertLessEqual(
            metrics["feature"],
            datetime.now(pytz.utc) - datetime(2021, 1, 2, tzinfo=pytz.UTC),
        )
        self.assertGreater(
            metrics["feature"],
            datetime.now(pytz.utc) - datetime(2021, 1, 4, tzinfo=pytz.UTC),
        )

    def test_get_label_metrics_closed_issue_labeled_past_closed_at(self):
        """Test get_label_metrics using a closed issue that was labeled past issue closed_at"""
        self.issue.state = "closed"
        labels = ["foo"]
        metrics = get_label_metrics(self.issue, labels)
        self.assertEqual(metrics["foo"], None)

    def test_get_label_metrics_closed_issue_label_removed_before_closure(self):
        """Test get_label_metrics for a closed issue where label was removed before closure"""
        # Create a mock issue that reproduces the problem scenario:
        # Issue created: day 0 (2021-01-01)
        # Label added: day 5 (2021-01-06)
        # Label removed: day 10 (2021-01-11)
        # Issue closed: day 15 (2021-01-16)
        # Expected duration: 5 days (from day 5 to day 10)

        issue = MagicMock()
        issue.issue = MagicMock(spec=github3.issues.Issue)
        issue.created_at = "2021-01-01T00:00:00Z"
        issue.closed_at = "2021-01-16T00:00:00Z"  # 15 days after creation
        issue.state = "closed"
        issue.issue.events.return_value = [
            MagicMock(
                event="labeled",
                label={"name": "test-label"},
                created_at=datetime(2021, 1, 6, tzinfo=pytz.UTC),  # day 5
            ),
            MagicMock(
                event="unlabeled",
                label={"name": "test-label"},
                created_at=datetime(2021, 1, 11, tzinfo=pytz.UTC),  # day 10
            ),
        ]

        labels = ["test-label"]
        metrics = get_label_metrics(issue, labels)

        # Should be 5 days (from day 5 to day 10), not 15 days (full issue duration)
        expected_duration = timedelta(days=5)
        self.assertEqual(metrics["test-label"], expected_duration)

    def test_get_label_metrics_closed_issue_label_remains_through_closure(self):
        """Test get_label_metrics for a closed issue where label remains applied through closure"""
        # Test scenario where label is applied and never removed:
        # Issue created: day 0 (2021-01-01)
        # Label added: day 2 (2021-01-03)
        # Issue closed: day 10 (2021-01-11)
        # Expected duration: 10 days (from issue creation to closure)

        issue = MagicMock()
        issue.issue = MagicMock(spec=github3.issues.Issue)
        issue.created_at = "2021-01-01T00:00:00Z"
        issue.closed_at = "2021-01-11T00:00:00Z"  # 10 days after creation
        issue.state = "closed"
        issue.issue.events.return_value = [
            MagicMock(
                event="labeled",
                label={"name": "stays-applied"},
                created_at=datetime(2021, 1, 3, tzinfo=pytz.UTC),  # day 2
            ),
            # No unlabel event - label remains applied
        ]

        labels = ["stays-applied"]
        metrics = get_label_metrics(issue, labels)

        # Should be 8 days (from day 2 when label was applied to day 10 when issue closed)
        expected_duration = timedelta(days=8)
        self.assertEqual(metrics["stays-applied"], expected_duration)


class TestGetAverageTimeInLabels(unittest.TestCase):
    """Unit tests for get_stats_time_in_labels"""

    def setUp(self):
        self.issues_with_metrics = MagicMock()
        self.issues_with_metrics = [
            IssueWithMetrics(
                title="issue1",
                html_url="url1",
                author="alice",
                time_to_first_response=None,
                time_to_close=None,
                time_to_answer=None,
                labels_metrics={"bug": timedelta(days=2)},
            ),
        ]

    def test_get_stats_time_in_labels(self):
        """Test get_stats_time_in_labels"""
        labels = ["bug", "feature"]
        metrics = get_stats_time_in_labels(self.issues_with_metrics, labels)
        print(metrics)
        self.assertEqual(len(metrics["avg"]), 2)
        self.assertEqual(metrics["avg"]["bug"], timedelta(days=2))
        self.assertIsNone(metrics["avg"].get("feature"))


if __name__ == "__main__":
    unittest.main()
