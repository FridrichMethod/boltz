#!/bin/bash

hhfilter -i "$1" -id 80 -cov 50 -qid 20 -o "$2"
