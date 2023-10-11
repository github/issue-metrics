# Table of Contents
- [Issue Metrics Action](#issue-metrics-action)
  - [Example use cases](#example-use-cases)
  - [Support](#support)
  - [Use as a GitHub Action](#use-as-a-github-action)
    - [Configuration](#configuration)
    - [Example workflows](#example-workflows)
      - [Calculated Time Example](#calculated-time-example)
      - [Fixed Time Example](#fixed-time-example)
      - [Multiple Repositories Example](#multiple-repositories-example)
    - [SEARCH_QUERY](#search_query)
    - [Measuring time spent in labels](#measuring-time-spent-in-labels)
    - [Example issue_metrics.md output](#example-issue_metricsmd-output)
    - [Example using the JSON output instead of the markdown output](#example-using-the-json-output-instead-of-the-markdown-output)
    - [Assigning teams instead of individuals](#assigning-teams-instead-of-individuals)
  - [Local usage without Docker](#local-usage-without-docker)
  - [License](#license)


# Issue Metrics Action

[![CodeQL](https://github.com/github/issue-metrics/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/github/issue-metrics/actions/workflows/codeql-analysis.yml) [![Docker Image CI](https://github.com/github/issue-metrics/actions/workflows/docker-image.yml/badge.svg)](https://github.com/github/issue-metrics/actions/workflows/docker-image.yml) [![Python package](https://github.com/github/issue-metrics/actions/workflows/python-package.yml/badge.svg)](https://github.com/github/issue-metrics/actions/workflows/python-package.yml)

This is a GitHub Action that searches for pull requests/issues/discussions in a repository
and measures and reports on several metrics. The issues/pull requests/discussions to
search for can be filtered by using a search query.

| Metric | Description |
|--------|-------------|
|Time to First Response | The duration from creation to the initial comment or review.|
|Time to Close | The period from creation to closure.|
|Time to Answer (Discussions Only) | The time from creation to an answer.|
|Time in Label | The duration from label application to removal, requires LABELS_TO_MEASURE env variable.|


*For pull requests, these metrics exclude the time the PR was in draft mode.

*For Issue and pull requests, issue/pull request author's own comments and comments by bots are excluded.

This action, developed by GitHub OSPO for our internal use, is open-sourced for your potential benefit.
Feel free to inquire about its usage by creating an issue in this repository.

To find syntax for search queries, check out the [documentation on searching issues and pull requests](https://docs.github.com/en/issues/tracking-your-work-with-issues/filtering-and-searching-issues-and-pull-requests)
or the [documentation on searching discussions](https://docs.github.com/en/search-github/searching-on-github/searching-discussions).

## Example use cases

| Metric | Description |
|--------|-------------|
|Maintainer Metrics| Monitor issue and pull request metrics for effective attention.|
|Timely Response| Ensure prompt user contact as a first responder.|
|OSPO Insights| Track open source request status and processing times.|
|Review Efficiency| Analyze PR review durations for retrospectives.|


## Support

If you need support using this project or have questions about it, please [open up an issue in this repository](https://github.com/github/issue-metrics/issues). Requests made directly to GitHub staff or support team will be redirected here to open an issue. GitHub SLA's and support/services contracts do not apply to this repository.

## Use as a GitHub Action

1. Create a repository to host this GitHub Action or select an existing repository. This is easiest if it is the same repository as the one you want to measure metrics on.
1. Select a best fit workflow file from the [examples below](#example-workflows).
1. Copy that example into your repository (from step 1) and into the proper directory for GitHub Actions: `.github/workflows/` directory with the file extension `.yml` (ie. `.github/workflows/issue-metrics.yml`)
1. Edit the values (`SEARCH_QUERY`, `assignees`) from the sample workflow with your information. See the [SEARCH_QUERY](#search_query) section for more details on options.
1. If you are running metrics on a repository other than the one where the workflow file is going to be, then update the value of `GH_TOKEN`. Do this by creating a [GitHub API token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic) with permissions to read the repo and write issues. Then take the value of the API token you just created, and [create a repository secret](https://docs.github.com/en/actions/security-guides/encrypted-secrets) where the name of the secret is `GH_TOKEN` and the value of the secret the API token. Then finally update the workflow file to use that repository secret by changing `GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}` to `GH_TOKEN: ${{ secrets.GH_TOKEN }}`. The name of the secret can really be anything. It just needs to match between when you create the secret name and when you refer to it in the workflow file.
1. If you want the resulting issue with the metrics in it to appear in a different repository other than the one the workflow file runs in, update the line `token: ${{ secrets.GITHUB_TOKEN }}` with your own GitHub API token stored as a repository secret. This process is the same as described in the step above. More info on creating secrets can be found [here](https://docs.github.com/en/actions/security-guides/encrypted-secrets).
1. Commit the workflow file to the default branch (often `master` or `main`)
1. Wait for the action to trigger based on the `schedule` entry or manually trigger the workflow as shown in the [documentation](https://docs.github.com/en/actions/using-workflows/manually-running-a-workflow).


### Configuration

Below are the allowed configuration options:

| field                 | required | default | description |
|-----------------------|----------|---------|-------------|
| `GH_TOKEN`            | True     |         | The GitHub Token used to scan the repository. Must have read access to all repository you are interested in scanning. |
| `SEARCH_QUERY`        | True     |         | The query by which you can filter issues/prs which must contain a `repo:`, `org:`, `owner:`, or a `user:` entry. For discussions, include `type:discussions` in the query. |
| `LABELS_TO_MEASURE`   | False    |         | A comma separated list of labels to measure how much time the label is applied. If not provided, no labels durations will be measured. Not compatible with discussions at this time. |
| `HIDE_AUTHOR` | False |         | If set to any value, the author will not be displayed in the generated markdown file. |
| `HIDE_TIME_TO_FIRST_RESPONSE` | False |         | If set to any value, the time to first response will not be displayed in the generated markdown file. |
| `HIDE_TIME_TO_CLOSE` | False |         | If set to any value, the time to close will not be displayed in the generated markdown file. |
| `HIDE_TIME_TO_ANSWER` | False |         | If set to any value, the time to answer a discussion will not be displayed in the generated markdown file. |
| `HIDE_LABEL_METRICS` | False |         | If set to any value, the time in label metrics will not be displayed in the generated markdown file. |
| `IGNORE_USERS` | False |         | A comma separated list of users to ignore when calculating metrics. (ie. `IGNORE_USERS: 'user1,user2'`). To ignore bots, append `[bot]` to the user (ie. `IGNORE_USERS: 'github-actions[bot]'`)  |


[Example workflows](example-workflows.md)

[Search Query](search-query.md)

[Measuring Time Spent](measure-time.md)

[Example Using Json Instead Markdown Output](example-using-json-instead-markdown-output.md)

[Assigning Teams Instead Of Individual](assign-team-instead-of-individual.md)

[Local Usage Without Docker](local-usage-without-docker.md)


## License

[MIT](LICENSE)
