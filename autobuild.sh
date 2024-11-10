#!/bin/bash

get_ts () {
    stat -c %Y $1
}

ts=$(get_ts $1)
while [ 1 ]; do
    if [ "$ts" != $(get_ts $1) ]; then
	pip install .
	ts=$(get_ts $1)
    else
	sleep 1
    fi
done
