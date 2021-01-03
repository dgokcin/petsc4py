#!/bin/bash

touch sjf_${1}
echo -n > sjf_${1}

while read -r line
do
    nnz=$(grep 'nonzeros' ${line}.json | cut -d ':' -f 2 | sed s/\"//g)
    echo ${line},${nnz} >> sjf_${1}
done < $1

sort -n -t"," -k2 sjf_${1} | awk -F, '{print $1;}' > ${1}
rm -f scf_${1}

