install-script:
	python3 runners/install.py --name LiveRemote

watch:
	python3 runners/watch.py --version 'Live 11.1.20'

close-set:
	pkill -x Ableton Live 11 Suite

open-set:
	open set/oscdevset.als

reload:
	just install-script && just close-set && just open-set
