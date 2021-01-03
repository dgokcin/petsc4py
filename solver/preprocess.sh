#!/bin/bash

while read -r line
do
    path=$(echo ${line} | awk -F'/' '{print $1"/"$2"/";}')
    name=$(echo ${line} | awk -F'/' '{print $3;}')
    tar xvzf ${line}.tar.gz -C ${path}
    python3 preprocessor.py -m ${line}.json
    rm -rf ${path}${name}/
done < $1

