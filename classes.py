"""A module containing classes for representing GitHub issues and their metrics.

Classes:
    IssueWithMetrics: A class to represent a GitHub issue with metrics.

"""


class IssueWithMetrics:
    """A class to represent a GitHub issue with metrics.

    Attributes:
        title (str): The title of the issue.
        html_url (str): The URL of the issue on GitHub.
        time_to_first_response (timedelta, optional): The time it took to
            get the first response to the issue.
        time_to_close (timedelta, optional): The time it took to close the issue.
        time_to_answer (timedelta, optional): The time it took to answer the
            discussions in the issue.

    """

    def __init__(
        self,
        title,
        html_url,
        time_to_first_response=None,
        time_to_close=None,
        time_to_answer=None,
    ):
        self.title = title
        self.html_url = html_url
        self.time_to_first_response = time_to_first_response
        self.time_to_close = time_to_close
        self.time_to_answer = time_to_answer
