current_dir := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))

default: mk-bin mk-etc

mk-bin:
	mkdir -p bin
	ln -sf ${current_dir}src/tud_restart ${current_dir}bin/tud_restart

mk-etc:
	mkdir -p etc
	ln -sf $(current_dir)src/docker-compose.yml $(current_dir)etc/docker-compose.yml

clean:
	rm -rf bin
	rm -rf etc

clean-pyc:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	name '*~' -exec rm --force  {}

