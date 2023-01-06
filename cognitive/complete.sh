#!/bin/bash
for dir in `find $1 -type d `
do
    if [[ $dir != $1 ]]
    then
        ls $dir | while read name ;
	do
	    #./cognitive --project "$dir"/"$name" $2
	    ./cognitive --generate "$dir"/"$name" $2
	    #./cognitive --make "$dir"/"$name" $2
	    ./cognitive --run "$dir"/"$name" $2
	    ./cognitive --analize "$dir"/"$name" $2
	    cp -a $4"result.txt" $3"$name""result.txt"
	done
    fi
done