#!/bin/dash
# Program that creates a directory and optional subdirectory if they dont exist
# Covers the use of subprocess and input command

echo "Enter a directory name:"
read dirname

if test -d "$dirname"  
then
    echo "Directory $dirname exists."  
else
    echo "Directory $dirname does not exist. Creating it..."
    mkdir "$dirname"
    echo "Directory $dirname created."
fi

echo "Do you want to create a subdirectory? (yes/no)"
read create_subdir

if test "$create_subdir" = "yes" 
then
    echo "Enter the name of the subdirectory:"
    read subdirname
    mkdir "$dirname/$subdirname"
    echo "Subdirectory $dirname/$subdirname created."
else
    echo "No subdirectory created."
fi