
local: test typecheck flake8 pylint

remote: test-cov typecheck flake8 pylint

install:
	pip install -r requirements-dev.txt
	pip install -r requirements.txt
	git submodule update --init --recursive
	make -C cdpp/src/
	printf 'Installation completed \u2705\n'

test:
	pytest

test-cov:
	pytest --cov pringles/ --cov-report term-missing

typecheck:
	mypy -p pringles --config-file=setup.cfg

flake8:
	flake8 --max-complexity 10 pringles/

pylint:
	pylint --errors-only --rcfile .pylintrc pringles/ # The errors only should be deleted in the future