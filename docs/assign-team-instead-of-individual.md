# Assigning teams instead of individuals

The assignee part of this workflow action comes from [a different GitHub action](https://github.com/peter-evans/create-issue-from-file) and currently GitHub issues don't support assigning groups.

By way of work around, you could use the [GitHub API to retrieve the members of the team](https://docs.github.com/en/rest/teams/members?apiVersion=2022-11-28#list-team-members) and then put them in a comma separated string that you provide as the assignee.

This requires setting up a new GitHub API token (referred to below as `CUSTOM_TOKEN`) which has `read:org` permissions assigned and single sign on authorization as needed.

To do this, create a [GitHub API token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic) with permissions to read the org (`read:org`).

Then take the value of the API token you just created, and [create a repository secret](https://docs.github.com/en/actions/security-guides/encrypted-secrets) where the name of the secret is `CUSTOM_TOKEN` and the value of the secret the API token.

That might look something like the workflow below where `ORG` is your organization name and `TEAM_SLUG` is the name of the team:

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
      uses: github/issue-metrics@v3
      env:
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
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
