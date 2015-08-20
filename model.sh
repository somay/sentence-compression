#!/bin/sh
grep "。" | awk -v FS="。" '{i=1; while (i < NF) { print $i; i++ } }' | juman -b | awk '! /EOS/ {ORS=" "; print $1} /EOS/ {ORS="\n"; print "<END>"}' | python3 model.py
