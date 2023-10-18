#!/bin/dash
# Prints different combinations of barbies that are best friends
# Covers nested for loops and test commands

barbie_names=("Barbie" "Skipper" "Stacie" "Chelsea" "Teresa")

for name1 in "Barbie" "Skipper" "Stacie" "Chelsea" "Teresa"
do
    for name2 in "Barbie" "Skipper" "Stacie" "Chelsea" "Teresa"
    do
        if test "$name1" != "$name2" 
        then
            echo "$name1 and $name2 are best of friends!"
        fi
    done
done

echo "All the barbies are bffs <3"
