#!/bin/dash
# tests variables in double quotes in test with variable and inline comment

a=1
b=1

if test "$a" -eq "$b"   # are comments preserved?
then    # are comments preserved?
    echo quotes work!   
fi