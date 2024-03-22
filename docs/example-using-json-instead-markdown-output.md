# Example using the JSON output instead of the Markdown output

There is JSON output available as well. You could use it for any number of possibilities, but here is one example that demonstrates retrieving the JSON output and then printing it out.

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
    - name: Run issue-metrics tool
      id: issue-metrics
      uses: github/issue-metrics@v2
      env:
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        SEARCH_QUERY: 'repo:owner/repo is:issue created:2023-05-01..2023-05-31 -reason:"not planned"'

    - name: Print output of issue metrics tool
      run: echo "${{ steps.issue-metrics.outputs.metrics }}"

```
