#!/bin/dash
# checks if variables work inside globs

suffix="txt"

for file in *."$suffix" 
do
    echo "The file $file exists"
done
