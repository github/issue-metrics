# justfile docs https://just.systems/man/en/
# justfile cheatsheet https://cheatography.com/linux-china/cheat-sheets/justfile/
set dotenv-load := true
set export

host := `uname -a`
python_exe := `which python`
pip_exe := `which pip3`
project_path := invocation_directory()
module_path := join(project_path, 'odious-ado')
api_path := join(project_path, 'api')

###
# need to add readme to docs and run a full suite of test etc
# absolute_path  parent_directory justfile_directory
# https://github.com/python-poetry/poetry python package and venv manager.
###
bt := '0'

export RUST_BACKTRACE_1 := bt
export JUST_LOG := "warn"

sys-info:
    @echo '{{host}}'

python:
    @echo 'Python:' `poetry run python --version`
    @echo 'Python Path:' `poetry env info`
    @echo 'Python Path:' `which python`

@dev deps="install":
    pip install poetry pip pre-commit --upgrade
    poetry install --with docs

set-hooks: dev
    poetry run pre-commit install --install-hooks # uninstall: `pre-commit uninstall`


load-test deps="no": (dev deps)
    @echo "Starting locust - swarming target"
    poetry install --with load
    poetry run locust -f tests/load/locustfile

unit-test deps="no": (dev deps)
    @echo 'unit-tests'
    poetry run pytest

type-checks deps="no": (dev deps)
    @echo 'type checking'
    poetry run mypy {{ module_path }} {{ api_path }}

format deps="no": (dev deps)
    @echo 'black formatting'
    poetry run black {{ module_path }} {{ api_path }}

lint deps="no": (dev deps)
    @echo "linting code base"
    poetry run flake8 {{ module_path }} {{ api_path }} \
    --max-line-length 100 \
    --ignore=F401,E731,F403,E501,W503 \
    --count

coverage-report:
    @echo "Building test coverage report"
    poetry run pytest --cov={{ module_path }}  --cov-config=.coveragerc --cov-report html

sphinx deps="no": (dev deps)
    @echo "Building application documentation"
    mkdir -p docs/html
    touch docs/.nojekyll
    cd docs/ && poetry run sphinx-build -b html . _build
    cp -r docs/_build/* docs/html

docs deps="no": (dev deps)
    @echo "Run auto build and start http server."
    poetry run sphinx-autobuild docs docs/_build/html
