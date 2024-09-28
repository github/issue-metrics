# Verify Token Access to Repository

GitHub PAT token access can be confusing. Here's a quick way to test if the token you're using is authorized to access your repository.

**Remove this snippet after you've verified your token.**

- Make sure you follow the token setup instructions [here](https://github.com/github/issue-metrics/tree/main?tab=readme-ov-file#use-as-a-github-action) first.

- Replace `{owner/repo}` with your own repository information.

- Add this snippet to your workflow.yml.

```yml
- name: Check GitHub token permissions
    run: |
      curl -H "Authorization: token ${{ secrets.GH_TOKEN }}" https://api.github.com/repos/{owner/repo}
```

- Go to your repository Actions in GitHub and run your job.
- In the job run details, click into the results of `Check GitHub token permissions`
- You should see your token details with no errors.

Example of the snippet in the full workflow:

```yml
name: Monthly issue metrics
on:
  workflow_dispatch:
  schedule:
    - cron: "3 2 1 * *"

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
      - name: Check GitHub token permissions
        run: |
          curl -H "Authorization: token ${{ secrets.GH_TOKEN }}" https://api.github.com/{owner/repo}
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
          GH_TOKEN: ${{ secrets.GH_TOKEN }}
          SEARCH_QUERY: "repo:{owner/repo} is:issue created:${{ env.last_month }}"
```
