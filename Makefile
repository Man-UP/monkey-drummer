clean:
	find src/ -name '*.pyc' -delete
	find lib/ -name '*.pyc' -delete

DEFAULT_GOAL := clean
.PHONY: clean

