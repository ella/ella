#!/bin/bash

cd $(dirname $0)
ls */*/manage.py */manage.py | while read i; do
	echo $i
	output=`mktemp`
	if $i &>$output test; then
		echo OK
	else
		echo ERROR
		if [ "$1" '==' '-v' ]; then
			cat $output
		fi
	fi
	rm $output
done

