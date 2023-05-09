.PHONY: lint test coverage

lint:
	python -m pylint check_brevisone.py
test:
	python -m unittest -v -b test_check_brevisone.py
coverage:
	python -m coverage run -m unittest test_check_brevisone.py
	python -m coverage report -m --include check_brevisone.py
