# Authenticating with a GitHub App Installation

Authenticating as an app installation lets your app access resources that are owned by the user or organization that installed the app. Authenticating as an app installation is ideal for automation workflows that don't involve user input.

[Documentation](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/about-authentication-with-a-github-app#authentication-as-an-app-installation) for more details.

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
        GH_APP_ID: ${{ secrets.GITHUB_APP_ID }}
        GH_APP_INSTALLATION_ID: ${{ secrets.GITHUB_APP_INSTALLATION_ID }}
        GH_APP_PRIVATE_KEY: ${{ secrets.GH_APP_PRIVATE_KEY }}
        SEARCH_QUERY: 'repo:owner/repo is:issue created:${{ env.last_month }} -reason:"not planned"'

    - name: Get user names from team
      run: |
          teamMembers="$(gh api /orgs/ORG/teams/TEAM_SLUG/members | jq -r '.[].login' | paste -sd, -)"
          echo 'TEAM_MEMBERS='$teamMembers >> $GITHUB_ENV
        env:
          GITHUB_TOKEN: ${{ secrets.CUSTOM_TOKEN }}

    - name: Create issue
      uses: peter-evans/create-issue-from-file@v4
      with:
        title: Monthly issue metrics report
        token: ${{ secrets.GITHUB_TOKEN }}
        content-filepath: ./issue_metrics.md
        assignees: ${{ env.TEAM_MEMBERS }}
```
