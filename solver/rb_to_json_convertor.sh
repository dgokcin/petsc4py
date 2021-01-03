#!/bin/bash

while read -r line
do
 # get base
 name="${line}"
 sed s/\'/\"/g ${name}.rb > ${name}.tmp
 sed "s/^[ \t]*//" -i ${name}.tmp
 #replace the last ", with ,
 line=$(grep -n ':' ${name}.tmp | tail -n 1 | cut -d ':' -f 1)
 sed -i -r ${line}'s/(.*)\",/\1\"/' ${name}.tmp

 # replace ' with "
 awk -F: '{if (NF==2){print "    \""$1"\": "$2;} else {print $0;}}' ${name}.tmp > ${name}.json
 rm -f ${name}.tmp

 # fix \, line problem.
 grep -n -w -- \", ${name}.json | sed s/:/\|/ | grep -v ':' | sed s/\|/:/ | cut -d ':' -f 1 | tac > line.lst

 while read -r num
 do
  sed -i ${num}d ${name}.json
  ((num--))
  sed -i ${num}'s/$/\",/' ${name}.json
 done < line.lst

 rm -f line.lst

 note=$(grep -n 'notes:' ${name}.json | cut -d ':' -f 1)
 if [ ! -z "$note" ]
 then
  sed -i ${note}d ${name}.json
 fi

done < $1

