# Configuring the `SEARCH_QUERY`

Issues or Pull Requests? Open or closed?
This action can be configured to run metrics on discussions, pull requests and/or issues. It is also configurable by whether they were open or closed in the specified time window.

Further query options are listed in the documentation on [searching issues and pull requests](https://docs.github.com/en/issues/tracking-your-work-with-issues/filtering-and-searching-issues-and-pull-requests) or [searching discussions](https://docs.github.com/en/search-github/searching-on-github/searching-discussions). Search results are limited to 1000 results by the GitHub API.

## Examples

Issues opened in May 2023:

- `repo:owner/repo is:issue created:2023-05-01..2023-05-31`

Issues closed in May 2023 (may have been open in May or earlier):

- `repo:owner/repo is:issue closed:2023-05-01..2023-05-31`

Pull requests opened in May 2023:

- `repo:owner/repo is:pr created:2023-05-01..2023-05-31`

Pull requests closed in May 2023 (may have been open in May or earlier):

- `repo:owner/repo is:pr closed:2023-05-01..2023-05-31`

Discussions opened in May 2023:

- `repo:owner/repo type:discussions created:2023-05-01..2023-05-31`

Discussions opened in May 2023 with category of `engineering` and label of `question`:

- `repo:owner/repo type:discussions created:2023-05-01..2023-05-31 category:engineering label:"question"`

Both issues and pull requests opened in May 2023:

- `repo:owner/repo created:2023-05-01..2023-05-31`

Both issues and pull requests closed in May 2023 (may have been open in May or earlier):

- `repo:owner/repo closed:2023-05-01..2023-05-31`

## Reporting on opened and closed issues/PRs

OK, but what if I want both open or closed issues and pull requests? Due to limitations in issue search (no ability for OR logic), you will need to run the action twice, once for opened and once for closed. Here is an example workflow that does this:

```yaml
name: Monthly issue metrics
on:
  workflow_dispatch:
  schedule:
    - cron: '3 2 1 * *'

permissions:
  contents: read

jobs:
  build:
    name: issue metrics
    runs-on: ubuntu-latest
    permissions:
      issues: write
        pull-requests: read

    steps:

    - name: Run issue-metrics tool for issues and prs opened in May 2023
      uses: github/issue-metrics@v3
      env:
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        SEARCH_QUERY: 'repo:owner/repo created:2023-05-01..2023-05-31 -reason:"not planned"'

    - name: Create issue for opened issues and prs
      uses: peter-evans/create-issue-from-file@v4
      with:
        title: Monthly issue metrics report for opened issues and prs
        token: ${{ secrets.GITHUB_TOKEN }}
        content-filepath: ./issue_metrics.md
        assignees: <YOUR_GITHUB_HANDLE_HERE>

    - name: Run issue-metrics tool for issues and prs closed in May 2023
      uses: github/issue-metrics@v3
      env:
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        SEARCH_QUERY: 'repo:owner/repo closed:2023-05-01..2023-05-31 -reason:"not planned"'

    - name: Create issue for closed issues and prs
      uses: peter-evans/create-issue-from-file@v4
      with:
        title: Monthly issue metrics report for closed issues and prs
        content-filepath: ./issue_metrics.md
        assignees: <YOUR_GITHUB_HANDLE_HERE>
```
