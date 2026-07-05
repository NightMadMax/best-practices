.PHONY: test validate check

test:
	python3 -m unittest discover -s tests -v

validate:
	python3 scripts/validate.py

check: test validate
