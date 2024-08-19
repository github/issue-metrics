<!-- markdownlint-disable MD013 -->
<!-- omit in toc -->

# Contributing to issue-metrics

First off, thanks for taking the time to contribute! :heart:

All types of contributions are encouraged and valued. See the [Table of Contents](#table-of-contents) for different ways to help and details about how this project handles them. Please make sure to read the relevant section before making your contribution. It will make it a lot easier for us project owners and smooth out the experience for all involved. The team looks forward to your contributions. :tada:

<!-- omit in toc -->

## Table of Contents

- [I Have a Question](#i-have-a-question)
- [I Want To Contribute](#i-want-to-contribute)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)
- [Releases](#releases)

## I Have a Question

Before you ask a question, it is best to search for existing [Issues](https://github.com/github/issue-metrics/issues) that might help you. In case you have found a suitable issue and still need clarification, you can write your question in this issue.

If you then still feel the need to ask a question and need clarification, we recommend the following:

- Open an [Issue](https://github.com/github/issue-metrics/issues/new).
- Provide as much context as you can about what you're running into.
- Provide project and platform versions (Node.js, npm, etc), depending on what seems relevant.

We will then take care of the issue as soon as possible.

## I Want To Contribute

> ### Legal Notice <!-- omit in toc -->
>
> When contributing to this project, you must agree that you have authored 100% of the content, that you have the necessary rights to the content and that the content you contribute may be provided under the project license.

## Reporting Bugs

<!-- omit in toc -->

### Before Submitting a Bug Report

A good bug report shouldn't leave others needing to chase you up for more information. Therefore, we ask you to investigate carefully, collect information and describe the issue in detail in your report. Please complete the following steps in advance to help us fix any potential bug as fast as possible.

- Make sure that you are using the latest version.
- Determine if your bug is really a bug and not an error on your side e.g. using incompatible environment components/versions (Make sure that you have read the documentation. If you are looking for support, you might want to check [this section](#i-have-a-question)).
- To see if other users have experienced (and potentially already solved) the same issue you are having, check if there is not already a bug report existing for your bug or error in the [bug tracker](https://github.com/github/issue-metrics/issues).
- Collect information about the bug:
  - Stack trace (Traceback)
  - OS, Platform and Version (Windows, Linux, macOS, x86, ARM)
  - Version of the interpreter, compiler, SDK, runtime environment, package manager, depending on what seems relevant.
  - Possibly your input and the output
- Can you reliably reproduce the issue? And can you also reproduce it with older versions?

<!-- omit in toc -->

### How Do I Submit a Good Bug Report?

Please submit a bug report using our [GitHub Issues template](https://github.com/github/issue-metrics/issues/new?template=bug_report.yml).

## Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for issue-metrics, **including completely new features and minor improvements to existing functionality**. Following these guidelines will help maintainers and the community to understand your suggestion and find related suggestions.

<!-- omit in toc -->

### Before Submitting an Enhancement

- Make sure that you are using the latest version.
- Read the documentation carefully and find out if the functionality is already covered, maybe by an individual configuration.
- Perform a [search](https://github.com/github/issue-metrics/issues) to see if the enhancement has already been suggested. If it has, add a comment to the existing issue instead of opening a new one.
- Find out whether your idea fits with the scope and aims of the project. It's up to you to make a strong case to convince the project's developers of the merits of this feature or to develop the feature yourself and contribute it to the project.

<!-- omit in toc -->

### How Do I Submit a Good Enhancement Suggestion?

Please submit an enhancement suggestion using our [GitHub Issues template](https://github.com/github/issue-metrics/issues/new?template=feature_request.yml).

### Pull Request Standards

We are using [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) to standardize our pull request titles. This allows us to automatically generate labels and changelogs and follow semantic versioning. Please follow the commit message format when creating a pull request. What pull request title prefixes are expected are in the [pull_request_template.md](.github/pull_request_template.md) that is shown when creating a pull request.

## Releases

Releases are automated if a pull request is labelled with our [SemVer related labels](.github/release-drafter.yml) or with the `vuln` or `release` labels.

You can also manually initiate a release you can do so through the GitHub Actions UI. If you have permissions to do so, you can navigate to the [Actions tab](https://github.com/github/issue-metrics/actions/workflows/release.yml) and select the `Run workflow` button. This will allow you to select the branch to release from and the version to release.
