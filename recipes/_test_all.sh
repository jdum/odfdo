#!/bin/bash

PYTHON="python3.12"

err=0
tot=0
for script in *.py ; do
    let tot++
    echo -en "${script} :"
    $("${PYTHON}" "${script}" &> /dev/null) && echo " passed." || { echo " failed !"; let err++ ; }
done
echo "-------------------------"
echo "total scripts: $tot, failed scripts: $err"
