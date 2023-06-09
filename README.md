# Issue Metrics Action

[![CodeQL](https://github.com/github/issue-metrics/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/github/issue-metrics/actions/workflows/codeql-analysis.yml) [![Docker Image CI](https://github.com/github/issue-metrics/actions/workflows/docker-image.yml/badge.svg)](https://github.com/github/issue-metrics/actions/workflows/docker-image.yml) [![Python package](https://github.com/github/issue-metrics/actions/workflows/python-package.yml/badge.svg)](https://github.com/github/issue-metrics/actions/workflows/python-package.yml)

This is a GitHub Action that searches for pull requests/issues in a repository and measures
the time to first response for each issue. It then calculates the average time
to first response and writes the issues with their time to first response and time to close
to a Markdown file. The issues to search for can be filtered by using a search query.

This action was developed by the GitHub OSPO for our own use and developed in a way that we could open source it that it might be useful to you as well! If you want to know more about how we use it, reach out in an issue in this repository.

To find syntax for search queries, check out the [documentation](https://docs.github.com/en/issues/tracking-your-work-with-issues/filtering-and-searching-issues-and-pull-requests).

## Support

If you need support using this project or have questions about it, please [open up an issue in this repository](https://github.com/github/issue-metrics/issues). Requests made directly to GitHub staff or support team will be redirected here to open an issue. GitHub SLA's and support/services contracts do not apply to this repository.

## Use as a GitHub Action

1. Create a repository to host this GitHub Action or select an existing repository.
1. Create the env values from the sample workflow below (GH_TOKEN, REPOSITORY_URL, ISSUE_SEARCH_QUERY) with your information as repository secrets. More info on creating secrets can be found [here](https://docs.github.com/en/actions/security-guides/encrypted-secrets).
Note: Your GitHub token will need to have read access to the repository in the organization that you want evaluated
1. Copy the below example workflow to your repository and put it in the `.github/workflows/` directory with the file extension `.yml` (ie. `.github/workflows/issue-metrics.yml`)

### Example workflow

```yaml
name: Monthly issue metrics
on:
  workflow_dispatch:
  schedule:
    - cron: '3 2 1 * *'

jobs:
  build:
    name: issue metrics
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Run issue-metrics tool
      uses: docker://ghcr.io/github/issue-metrics:v1
      env:
        GH_TOKEN: ${{ secrets.GH_TOKEN }}
        REPOSITORY_URL: https://github.com/owner/repo
        ISSUE_SEARCH_QUERY: 'is:issue created:2023-05-01..2023-05-31 -reason:"not planned"'

    - name: Create issue
      uses: peter-evans/create-issue-from-file@v4
      with:
        title: Monthly issue metrics report
        content-filepath: ./issue_metrics.md
        assignees: <YOUR_GITHUB_HANDLE_HERE>

```

### Example issue_metrics.md output

```markdown
# Issue Metrics

| Metric | Value |
| --- | ---: |
| Average time to first response | 0:50:44.666667 |
| Average time to close | 6 days, 7:08:52 |
| Number of issues that remain open | 2 |
| Number of issues closed | 1 |
| Total number of issues created | 3 |

| Title | URL | Time to first response | Time to close 
| --- | --- | ---: | ---: |
| Issue Title 1 | https://github.com/user/repo/issues/1 | 0:00:41 | 6 days, 7:08:52 |
| Issue Title 2 | https://github.com/user/repo/issues/2 | 0:05:26 | None |
| Issue Title 3 | https://github.com/user/repo/issues/3 | 2:26:07 | None |

```

## Local usage without Docker

1. Copy `.env-example` to `.env`
1. Fill out the `.env` file with a _token_ from a user that has access to the organization to scan (listed below). Tokens should have admin:org or read:org access.
1. Fill out the `.env` file with the _repository_url_ of the repository to scan
1. Fill out the `.env` file with the _issue_search_query_ to filter issues by
1. `pip install -r requirements.txt`
1. Run `python3 ./issue_metrics.py`, which will output issue metrics data

## License

[MIT](LICENSE)
