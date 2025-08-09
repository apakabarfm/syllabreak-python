install:
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt

test:
	venv/bin/pytest syllabreak/
	venv/bin/pytest test_readme.py

lint:
	venv/bin/ruff check syllabreak/
	venv/bin/ruff format --check syllabreak/

format:
	venv/bin/ruff check --fix syllabreak/
	venv/bin/ruff format syllabreak/