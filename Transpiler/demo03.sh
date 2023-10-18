#!/bin/dash
# Takes an input string and outputs a message
# Covers the use of while loops and string concatenation 

while true
do
    echo "Enter a name (type 'stop' to exit):"
    read input_string

    if test "$input_string" = "stop" 
    then
        echo "Exiting..."
        exit 0
    fi

    echo "The provided input is: $input_string"
    echo "Hello, ${input_string}!!"
    echo "Hope you are doing well."

done
