.PHONY: test
test:
	pytest -v --cov=. --cov-config=.coveragerc --cov-fail-under=80 --cov-report term-missing

.PHONY: clean
clean:
	rm -rf .pytest_cache .coverage __pycache__
