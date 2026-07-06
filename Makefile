.PHONY: test validate freshness metrics catalog check

test:
	python3 -m unittest discover -s tests -v

validate:
	python3 scripts/validate.py

freshness:
	python3 scripts/validate.py --strict-freshness

metrics:
	python3 scripts/practice_metrics.py

catalog:
	python3 scripts/search_practices.py

check: test validate freshness
