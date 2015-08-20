#!/bin/sh
if [ $# -lt 2 ]
    then
    echo '[ERROR] Two options are needed. 
First is a file to store trigram model in pickle format.
Seocnd is a file for start-of-sentence probabilities in pickle format'
    exit 1
fi
grep "。" | awk -v FS="。" '{i=1; while (i < NF) { print $i; i++ } }' | juman -b | awk '! /EOS/ {ORS=" "; print $1} /EOS/ {ORS="\n"; print "<END>"}' | python3 model.py --lm $1 --start $2
