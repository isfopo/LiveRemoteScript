install-script:
	python3 scripts/install.py --name LiveRemote

watch:
	python3 scripts/watch.py --version 'Live 11.1.6'

close-set:
	pkill -x Ableton Live 11 Suite

open-set:
	open set/oscdevset.als

reload:
	make install-script && make close-set && make open-set
