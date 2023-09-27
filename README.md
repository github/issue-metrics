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

This is a GitHub Action that searches for pull requests/issues/discussions in a repository and measures and reports on
several metrics. The issues/pull requests/discussions to search for can be filtered by using a search query.

The metrics that are measured are:
| Metric | Description |
|--------|-------------|
| Time to first response | The time between when an issue/pull request/discussion is created and when the first comment or review is made.* |
| Time to close | The time between when an issue/pull request/discussion is created and when it is closed.* |
| Time to answer | (Discussions only) The time between when a discussion is created and when it is answered. |
| Time in label | The time between when a label has a specific label applied to an issue/pull request/discussion and when it is removed. This requires the LABELS_TO_MEASURE env variable to be set. |

*For pull requests, these metrics exclude the time the PR was in draft mode.
*For Issue and pull requests, issue/pull request author's own comments and comments by bots are excluded.

This action was developed by the GitHub OSPO for our own use and developed in a way that we could open source it that it might be useful to you as well! If you want to know more about how we use it, reach out in an issue in this repository.

To find syntax for search queries, check out the [documentation on searching issues and pull requests](https://docs.github.com/en/issues/tracking-your-work-with-issues/filtering-and-searching-issues-and-pull-requests) or the [documentation on searching discussions](https://docs.github.com/en/search-github/searching-on-github/searching-discussions).

## Example use cases

- As a maintainer, I want to see metrics for issues and pull requests on the repository I maintain in order to ensure I am giving them the proper amount of attention.
- As a first responder on a repository, I want to ensure that users are getting contact from me in a reasonable amount of time.
- As an OSPO, I want to see how many open source repository requests are open/closed, and metrics for how long it takes to get through the open source process.
- As a product development team, I want to see metrics around how long pull request reviews are taking, so that we can reflect on that data during retrospectives.

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

### Example workflows

#### Calculated Time Example
This workflow searches for the issues created last month, and generates an issue with metrics.

```yaml
name: Monthly issue metrics
on:
  workflow_dispatch:
  schedule:
    - cron: '3 2 1 * *'

permissions:
  issues: write
  pull-requests: read

jobs:
  build:
    name: issue metrics
    runs-on: ubuntu-latest

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

#### Fixed Time Example
This workflow searches for the issues created between 2023-05-01..2023-05-31, and generates an issue with metrics.

```yaml
name: Monthly issue metrics
on:
  workflow_dispatch:

permissions:
  issues: write
  pull-requests: read

jobs:
  build:
    name: issue metrics
    runs-on: ubuntu-latest

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

#### Multiple Repositories Example

This workflow searches for the issues created last month, and generates an issue with metrics. It also searches for issues in a second repository and includes those metrics in the same issue.

```yaml
name: Monthly issue metrics (Multi Repo)
on:
  workflow_dispatch:

permissions:
  issues: write
  pull-requests: read

jobs:
  build:
    name: issue metrics
    runs-on: ubuntu-latest

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

## SEARCH_QUERY
Issues or Pull Requests? Open or closed?
This action can be configured to run metrics on discussions, pull requests and/or issues. It is also configurable by whether they were open or closed in the specified time window. Further query options are listed in the [documentation on searching issues and pull requests](https://docs.github.com/en/issues/tracking-your-work-with-issues/filtering-and-searching-issues-and-pull-requests) or the [documentation on searching discussions](https://docs.github.com/en/search-github/searching-on-github/searching-discussions). Search results are limited to 1000 results by the GitHub API. Here are some search query examples:

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

Discussions opened in May 2023 with category of engineering and label of question:
- `repo:owner/repo type:discussions created:2023-05-01..2023-05-31 category:engineering label:"question"`

Both issues and pull requests opened in May 2023:
- `repo:owner/repo created:2023-05-01..2023-05-31`

Both issues and pull requests closed in May 2023 (may have been open in May or earlier):
- `repo:owner/repo closed:2023-05-01..2023-05-31`

OK, but what if I want both open or closed issues and pull requests? Due to limitations in issue search (no ability for OR logic), you will need to run the action twice, once for opened and once for closed. Here is an example workflow that does this:

```yaml
name: Monthly issue metrics
on:
  workflow_dispatch:
  schedule:
    - cron: '3 2 1 * *'

permissions:
  issues: write
  pull-requests: read

jobs:
  build:
    name: issue metrics
    runs-on: ubuntu-latest

    steps:

    - name: Run issue-metrics tool for issues and prs opened in May 2023
      uses: github/issue-metrics@v2
      env:
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        SEARCH_QUERY: 'repo:owner/repo created:2023-05-01..2023-05-31 -reason:"not planned"'

    - name: Create issue for opened issues and prs
      uses: peter-evans/create-issue-from-file@v4
      with:
        title: Monthly issue metrics report  for opened issues and prs
        token: ${{ secrets.GITHUB_TOKEN }}
        content-filepath: ./issue_metrics.md
        assignees: <YOUR_GITHUB_HANDLE_HERE>

    - name: Run issue-metrics tool for issues and prs closed in May 2023
      uses: github/issue-metrics@v2
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

## Measuring time spent in labels

**Note**: The discussions API currently doesn't support the `LabeledEvent` so this action cannot measure the time spent in a label for discussions.

Sometimes it is helpful to know how long an issue or pull request spent in a particular label. This action can be configured to measure the time spent in a label. This is different from only wanting to measure issues with a specific label. If that is what you want, see the section on [configuring your search query](https://github.com/github/issue-metrics/blob/main/README.md#search_query-issues-or-pull-requests-open-or-closed).

Here is an example workflow that does this:

```yaml
name: Monthly issue metrics
on:
  workflow_dispatch:

permissions:
  issues: write
  pull-requests: read

jobs:
  build:
    name: issue metrics
    runs-on: ubuntu-latest

    steps:

    - name: Run issue-metrics tool
      uses: github/issue-metrics@v2
      env:
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        LABELS_TO_MEASURE: 'waiting-for-manager-approval,waiting-for-security-review'
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

| Metric | Value |
| --- | ---: |
| Average time to first response | 0:50:44.666667 |
| Average time to close | 6 days, 7:08:52 |
| Average time to answer | 1 day |
| Average time spent in waiting-for-manager-approval | 0:00:41 |
| Average time spent in waiting-for-security-review | 2 days, 4:25:03 |
| Number of items that remain open | 2 |
| Number of items closed | 1 |
| Total number of items created | 3 |

| Title | URL | Author | Time to first response | Time to close | Time to answer | Time spent in waiting-for-manager-approval | Time spent in waiting-for-security-review |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pull Request Title 1 | https://github.com/user/repo/pulls/1 | alice | 0:05:26 | None | None | None | None |
| Issue Title 2 | https://github.com/user/repo/issues/2 | bob | 2:26:07 | None | None | 0:00:41 | 2 days, 4:25:03 |

```

## Example issue_metrics.md output

Here is the output with no hidden columns:
```markdown
# Issue Metrics

| Metric | Value |
| --- | ---: |
| Average time to first response | 0:50:44.666667 |
| Average time to close | 6 days, 7:08:52 |
| Average time to answer | 1 day |
| Number of items that remain open | 2 |
| Number of items closed | 1 |
| Total number of items created | 3 |

| Title | URL | Author | Time to first response | Time to close | Time to answer |
| --- | --- | --- | --- | --- | --- |
| Discussion Title 1 | https://github.com/user/repo/discussions/1 | None | 0:00:41 | 6 days, 7:08:52 | 1 day |
| Pull Request Title 2 | https://github.com/user/repo/pulls/2 | bob | 0:05:26 | None | None |
| Issue Title 3 | https://github.com/user/repo/issues/3 | carol | 2:26:07 | None | None |

```

Here is the output with all hidable columns hidden:
```markdown
# Issue Metrics

| Metric | Value |
| --- | ---: |
| Number of items that remain open | 2 |
| Number of items closed | 1 |
| Total number of items created | 3 |

| Title | URL | Author |
| --- | --- | --- |
| Discussion Title 1 | https://github.com/user/repo/discussions/1 | None |
| Pull Request Title 2 | https://github.com/user/repo/pulls/2 | bob |
| Issue Title 3 | https://github.com/user/repo/issues/3 | carol |

```

## Example using the JSON output instead of the markdown output

There is JSON output available as well. You could use it for any number of possibilities, but here is one example that demonstrates retreiving the JSON output and then printing it out.

```yaml
name: Monthly issue metrics
on:
  workflow_dispatch:
  schedule:
    - cron: '3 2 1 * *'

permissions:
  issues: write
  pull-requests: read

jobs:
  build:
    name: issue metrics
    runs-on: ubuntu-latest

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

## Assigning teams instead of individuals

The assignee part of this workflow action comes from [a different GitHub action](https://github.com/peter-evans/create-issue-from-file) and currently GitHub issues don't support assigning groups.

By way of work around, you could use the [GitHub API to retrieve the members of the team](https://docs.github.com/en/rest/teams/members?apiVersion=2022-11-28#list-team-members) and then put them in a comma separated string that you provide as the assignee. This requires setting up a new GitHub API token (referred to below as `CUSTOM_TOKEN`) which has `read:org` permissions assigned and single sign on authorization as needed. To do this, create a [GitHub API token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic) with permissions to read the org (`read:org`). Then take the value of the API token you just created, and [create a repository secret](https://docs.github.com/en/actions/security-guides/encrypted-secrets) where the name of the secret is `CUSTOM_TOKEN` and the value of the secret the API token.

That might look something like the workflow below where `ORG` is your organization name and `TEAM_SLUG` is the name of the team:

```yaml
name: Monthly issue metrics
on:
  workflow_dispatch:
  schedule:
    - cron: '3 2 1 * *'

permissions:
  issues: write
  pull-requests: read

jobs:
  build:
    name: issue metrics
    runs-on: ubuntu-latest

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

## Local usage without Docker

1. Make sure you have at least Python3.11 installed
1. Copy `.env-example` to `.env`
1. Fill out the `.env` file with a _token_ from a user that has access to the organization to scan (listed below). Tokens should have admin:org or read:org access.
1. Fill out the `.env` file with the _search_query_ to filter issues by
1. `pip3 install -r requirements.txt`
1. Run `python3 ./issue_metrics.py`, which will output issue metrics data

## License

[MIT](LICENSE)
