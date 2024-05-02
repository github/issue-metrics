# Dealing with large issue metrics Markdown files

When working with lots of issues/pull requests/discussion results, the resulting issue_metrics.md file can become very large. This can cause the GitHub API to return an error when trying to create an issue with the contents of the file.

```shell
Pull request creation failed. Validation failed: Body is too long (maximum is 65536 characters)
```

To work around this limitation, the issue-metrics action detects the large file size and splits the issue_metrics.md file into smaller files. So instead of issue_metrics.md, you will get issue_metrics_0.md, issue_metrics_1.md, etc.
Since we don't want the action to fail, it has been designed to have the same name as usual for the first split file (issue_metrics.md) and then append a number to the name for the subsequent split files.

You can choose one of the following strategies to deal with the split files:
- Create multiple issues, each with using the next split file in the sequence.
- Upload the full file as an artifact and link to it in the issue body.
- Create an issue and put the content of the split files as issue comments.

JSON output files are not split since its not anticipated that you use them as issue body content.
