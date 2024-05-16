.PHONY: lint test coverage

lint:
	python3 -m pylint check_brevisone.py
test:
	python3 -m unittest -v -b test_check_brevisone.py
coverage:
	python3 -m coverage run -m unittest test_check_brevisone.py
	python3 -m coverage report -m --include check_brevisone.py
