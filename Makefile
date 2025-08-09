install:
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt

test:
	venv/bin/pytest syllabreak/