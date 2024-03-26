# Example workflows

## Calculated Time Example

This workflow searches for the issues created last month, and generates an issue with metrics.

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

    - name: Get dates for last month
      shell: bash
      run: |
        # Calculate the first day of the previous month
        first_day=$(date -d "last month" +%Y-%m-01)

        # Calculate the last day of the previous month
        last_day=$(date -d "$first_day +1 month -1 day" +%Y-%m-%d)

        #Set an environment variable with the date range
        echo "$first_day..$last_day"
        echo "last_month=$first_day..$last_day" >> "$GITHUB_ENV"

    - name: Run issue-metrics tool
      uses: github/issue-metrics@v2
      env:
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        SEARCH_QUERY: 'repo:owner/repo is:issue created:${{ env.last_month }} -reason:"not planned"'

    - name: Create issue
      uses: peter-evans/create-issue-from-file@v4
      with:
        title: Monthly issue metrics report
        token: ${{ secrets.GITHUB_TOKEN }}
        content-filepath: ./issue_metrics.md
        assignees: <YOUR_GITHUB_HANDLE_HERE>

```

## Fixed Time Example

This workflow searches for the issues created between 2023-05-01..2023-05-31, and generates an issue with metrics.

```yaml
name: Monthly issue metrics
on:
  workflow_dispatch:

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

    - name: Run issue-metrics tool
      uses: github/issue-metrics@v2
      env:
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        SEARCH_QUERY: 'repo:owner/repo is:issue created:2023-05-01..2023-05-31 -reason:"not planned"'

    - name: Create issue
      uses: peter-evans/create-issue-from-file@v4
      with:
        title: Monthly issue metrics report
        token: ${{ secrets.GITHUB_TOKEN }}
        content-filepath: ./issue_metrics.md
        assignees: <YOUR_GITHUB_HANDLE_HERE>

```

## Multiple Repositories Example

This workflow searches for the issues created last month, and generates an issue with metrics. It also searches for issues in a second repository and includes those metrics in the same issue.

```yaml
name: Monthly issue metrics (Multi Repo)
on:
  workflow_dispatch:

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
      - name: Get dates for last month
        shell: bash
        run: |
          # Calculate the first day of the previous month
          first_day=$(date -d "last month" +%Y-%m-01)

          # Calculate the last day of the previous month
          last_day=$(date -d "$first_day +1 month -1 day" +%Y-%m-%d)

          #Set an environment variable with the date range
          echo "$first_day..$last_day"
          echo "last_month=$first_day..$last_day" >> "$GITHUB_ENV"

      - name: Get issue metrics
        uses: github/issue-metrics@v2
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SEARCH_QUERY: 'repo:owner/repo1 repo:owner/repo2 is:issue created:${{ env.last_month }} -reason:"not planned"'

      - name: Create issue
        uses: peter-evans/create-issue-from-file@v4
        with:
          title: Monthly issue metrics report (dev)
          token: ${{ secrets.GITHUB_TOKEN }}
          content-filepath: ./issue_metrics.md
          assignees: <YOUR_GITHUB_HANDLE_HERE>
```
