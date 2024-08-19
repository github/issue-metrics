# Measuring time spent in labels

**Note**: The discussions API currently doesn't support the `LabeledEvent` so this action cannot measure the time spent in a label for discussions.

Sometimes it is helpful to know how long an issue or pull request spent in a particular label. This action can be configured to measure the time spent in a label. This is different from only wanting to measure issues with a specific label. If that is what you want, see the section on [configuring your search query](https://github.com/github/issue-metrics/blob/main/README.md#search_query-issues-or-pull-requests-open-or-closed).

Here is an example workflow that does this:

```yaml
name: Monthly issue metrics
on:
  workflow_dispatch:

permissions:
  content: read

jobs:
  build:
    name: issue metrics
    runs-on: ubuntu-latest
    permissions:
      issues: write
      pull-requests: read

    steps:
      - name: Run issue-metrics tool
        uses: github/issue-metrics@v3
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          LABELS_TO_MEASURE: "waiting-for-manager-approval,waiting-for-security-review"
          SEARCH_QUERY: 'repo:owner/repo is:issue created:2023-05-01..2023-05-31 -reason:"not planned"'

      - name: Create issue
        uses: peter-evans/create-issue-from-file@v4
        with:
          title: Monthly issue metrics report
          token: ${{ secrets.GITHUB_TOKEN }}
          content-filepath: ./issue_metrics.md
          assignees: <YOUR_GITHUB_HANDLE_HERE>
```

then the report will look like this:

```markdown
# Issue Metrics

| Metric                                             |           Value |
| -------------------------------------------------- | --------------: |
| Average time to first response                     |  0:50:44.666667 |
| Average time to close                              | 6 days, 7:08:52 |
| Average time to answer                             |           1 day |
| Average time spent in waiting-for-manager-approval |         0:00:41 |
| Average time spent in waiting-for-security-review  | 2 days, 4:25:03 |
| Number of items that remain open                   |               2 |
| Number of items closed                             |               1 |
| Total number of items created                      |               3 |

| Title                | URL                                   | Time to first response | Time to close | Time to answer | Time spent in waiting-for-manager-approval | Time spent in waiting-for-security-review |
| -------------------- | ------------------------------------- | ---------------------- | ------------- | -------------- | ------------------------------------------ | ----------------------------------------- |
| Pull Request Title 1 | https://github.com/user/repo/pulls/1  | 0:05:26                | None          | None           | None                                       | None                                      |
| Issue Title 2        | https://github.com/user/repo/issues/2 | 2:26:07                | None          | None           | 0:00:41                                    | 2 days, 4:25:03                           |
```

## Example issue_metrics.md output

Here is the output with no hidden columns:

```markdown
# Issue Metrics

| Metric                           |           Value |
| -------------------------------- | --------------: |
| Average time to first response   |  0:50:44.666667 |
| Average time to close            | 6 days, 7:08:52 |
| Average time to answer           |           1 day |
| Number of items that remain open |               2 |
| Number of items closed           |               1 |
| Total number of items created    |               3 |

| Title                | URL                                        | Time to first response | Time to close   | Time to answer |
| -------------------- | ------------------------------------------ | ---------------------- | --------------- | -------------- |
| Discussion Title 1   | https://github.com/user/repo/discussions/1 | 0:00:41                | 6 days, 7:08:52 | 1 day          |
| Pull Request Title 2 | https://github.com/user/repo/pulls/2       | 0:05:26                | None            | None           |
| Issue Title 3        | https://github.com/user/repo/issues/3      | 2:26:07                | None            | None           |
```

Here is the output with all hidable columns hidden:

```markdown
# Issue Metrics

| Metric                           | Value |
| -------------------------------- | ----: |
| Number of items that remain open |     2 |
| Number of items closed           |     1 |
| Total number of items created    |     3 |

| Title                | URL                                        |
| -------------------- | ------------------------------------------ |
| Discussion Title 1   | https://github.com/user/repo/discussions/1 |
| Pull Request Title 2 | https://github.com/user/repo/pulls/2       |
| Issue Title 3        | https://github.com/user/repo/issues/3      |
```
