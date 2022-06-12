install-script:
	python3 install.py --name LiveRemote

watch:
	python3 watch.py --version 'Live 11.1.1'

close-set:
	pkill -x Ableton Live 11 Suite

open-set:
	open set/oscdevset.als

reload:
	make install-script && make close-set && make open-set
