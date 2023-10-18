#!/bin/dash
# This script checks if a file exists and gathers information about it.
# Covers the use of test command and nested if statements

echo "Enter a filename:"
read filename

if test -e "$filename"
then
    echo "$filename exists."

    if test -f "$filename"
    then
        echo "$filename is a regular file."
    elif test -d "$filename"
    then
        echo "$filename is a directory."
    else
        echo "$filename exists but is neither a regular file nor a directory."
    fi

    if test -r "$filename"
    then
        echo "$filename is readable."
    else
        echo "$filename is not readable."
    fi

    if test -w "$filename"
    then
        echo "$filename is writable."
    else
        echo "$filename is not writable."
    fi

    if test -x "$filename"
    then
        echo "$filename is executable."
    else
        echo "$filename is not executable."
    fi

    if test -s "$filename"
    then
        echo "$filename is not empty."
    else
        echo "$filename is empty."
    fi

else
    echo "$filename does not exist."
fi
