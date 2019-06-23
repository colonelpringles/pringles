
local: test typecheck flake8 pylint

remote: test-cov typecheck flake8 pylint

test:
	pytest

test-cov:
	pytest --cov colonel/ --cov-report term-missing

typecheck:
	mypy -p colonel

flake8:
	flake8 --max-complexity 10 colonel/

pylint:
	pylint --errors-only --rcfile .pylintrc colonel/ # The errors only should be deleted in the future