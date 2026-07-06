.PHONY: test validate freshness check

test:
	python3 -m unittest discover -s tests -v

validate:
	python3 scripts/validate.py

freshness:
	python3 scripts/validate.py --strict-freshness

check: test validate freshness
