default: build

build: dist/taskflow dist/taskflowd

dist/taskflow: main.py taskflow/*.py taskflow/**/*.py taskflow.spec
	pyinstaller taskflow.spec

dist/taskflowd: daemon.py taskflow/*.py taskflow/**/*.py taskflowd.spec
	pyinstaller taskflowd.spec

install:
	cp dist/taskflow /usr/bin/taskflow
	cp dist/taskflowd /usr/bin/taskflowd
	chmod a+x /usr/bin/taskflow
	chmod a+x /usr/bin/taskflowd
	mkdir -p /etc/taskflow
	test -f "/etc/taskflow/settings.yml" || cp ./etc/default-settings.yml /etc/taskflow/settings.yml

TEST_ARGS=--cov=.
TEST_TARGET=test/
test:
	pytest $(TEST_ARGS) $(TEST_TARGET)

.PHONY: test build default
