clean:
	find lib/ src/ -name '*.pyc' -delete
	rm -fr test/files.ifnimidi.com/

DEFAULT_GOAL := clean
.PHONY: clean

