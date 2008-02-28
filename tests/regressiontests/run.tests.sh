#!/bin/bash

cd $(dirname $0)
ls */*/manage.py */manage.py | while read i; do echo $i; $i test &>/dev/null && echo OK || echo ERROR; done

