#!/bin/bash

echo 
echo Running unittests
echo
python -m unittest discover
UNITTEST_EXIT=$?

echo 
echo Running pylint
echo
pylint -E -i y Tuber/
PYLINT_EXIT=$?

if [ $UNITTEST_EXIT -eq 0 -a $PYLINT_EXIT -eq 0 ]; then
    echo All tests OK!
    exit 0
else
    echo Failure!
    exit 1
fi
