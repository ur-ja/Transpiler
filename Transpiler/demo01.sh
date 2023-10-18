#!/bin/dash
# This script checks all .py files and prints information about them
# Covers the use of backticks and globbing inside a for loop

for file in *.py
do
    word_count=`wc -w < "$file"`
    line_count=`wc -l < "$file"`
    char_count=`wc -m < "$file"`
    longest_line=`wc -L < "$file"`
    file_size=`ls -lh "$file"`
    file_type=`file "$file"`
    owner=`ls -l "$file"`
    group=`ls -l "$file"`
    echo "File: $file"
    echo "Word Count: $word_count"
    echo "Line Count: $line_count"
    echo "Character Count: $char_count"
    echo "Longest Line Length: $longest_line"
    echo "File Size: $file_size"
    echo "File type: $file_type"
    echo "File Owner: $owner"
    echo "File Group: $group"
done