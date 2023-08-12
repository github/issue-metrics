# Odious ADO

Goodbye microsoft thanks for not a good project management tool!

Official documentation: [odious-ado]()

Please note: This is not complete but is kind of in the ballpark.

<!-- start elevator-pitch -->

The project has three components an API, SDK, and CLI. All of which are still a work in progress and
will need to be continually improved to meeting the requirements of the original spec.

<!-- end elevator-pitch -->

<!-- start quickstart -->

## Working On the Code Base (Local Development Environment)

There are pre-commit hook that should be setup and followed. However, at this time they can just be bypassed.

### Installation

A few prerequisite dependencies:
* [just](https://github.com/casey/just) a makefile replacement in rust.
* [pyenv](https://github.com/pyenv/pyenv#installation) python version manager.

After installing [just](https://github.com/casey/just) and [pyenv](https://github.com/pyenv/pyenv#installation).

---
### Use one of the following methods

* Follow the steps below. Both tools must be in your shell path.

```shell
pyenv install 3.11.3
# pyenv will change the local python version based on the .python-version file in root.
just dev install
# After running the just command running the following to verify configuration.
poetry run odious-ado --help
```

* Follow these steps to use pyenv to manage python virtual envs.

```shell
# install python
pyenv install 3.11.3

# create a python virtual env
pyenv virtualenv 3.11.3 odious-ado

# activate that python env for usage
pyenv activate odious-ado

# create a new local wheel to be used for the project 
poetry install

# pyenv will change the local python version based on the .python-version file in root.
just dev

# verify the python template install
python-template version
``` 