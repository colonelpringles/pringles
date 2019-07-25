
local: test typecheck flake8 pylint

remote: test-cov typecheck flake8 pylint

install:
	pip install -r requirements-dev.txt
	pip install -r requirements.txt
	git submodule update --init --recursive
	make -C cdpp/src/

test:
	pytest

test-cov:
	pytest --cov colonel/ --cov-report term-missing

typecheck:
	mypy -p colonel --config-file=setup.cfg

flake8:
	flake8 --max-complexity 10 colonel/

pylint:
	pylint --errors-only --rcfile .pylintrc colonel/ # The errors only should be deleted in the future