"""A module containing classes for representing GitHub issues and their metrics.

Classes:
    IssueWithMetrics: A class to represent a GitHub issue with metrics.

"""


class IssueWithMetrics:
    """A class to represent a GitHub issue with metrics.

    Attributes:
        title (str): The title of the issue.
        html_url (str): The URL of the issue on GitHub.
        author (str): The author of the issue.
        time_to_first_response (timedelta, optional): The time it took to
            get the first response to the issue.
        time_to_close (timedelta, optional): The time it took to close the issue.
        time_to_answer (timedelta, optional): The time it took to answer the
            discussions in the issue.
        label_metrics (dict, optional): A dictionary containing the label metrics

    """

    def __init__(
        self,
        title,
        html_url,
        author,
        time_to_first_response=None,
        time_to_close=None,
        time_to_answer=None,
        labels_metrics=None,
    ):
        self.title = title
        self.html_url = html_url
        self.author = author
        self.time_to_first_response = time_to_first_response
        self.time_to_close = time_to_close
        self.time_to_answer = time_to_answer
        self.label_metrics = labels_metrics
