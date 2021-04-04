
TEST_ARGS=--cov=.
TEST_TARGET=test/
test:
	pytest $(TEST_ARGS) $(TEST_TARGET)

.PHONY: test
