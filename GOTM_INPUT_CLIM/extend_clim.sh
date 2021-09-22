#!/bin/bash

# This scripts expands the climatology files to have them valid over the range Jan 2014 -> Dec 2020
# So it just copies the files, change the years, and concatenate all years in a single file with the same name.
# A. Capet 17/09/2021

for v in Temp Sal1 PO41 NO3 NO2 Chl O2\(1\) Si1 Alk CO2 POC PON POP DOC DON DOP TP
do
    vo=$v'_clim.txt'
    for y in 2015 2016 2017 2018 2019 2020
    do
	sed s:2014-:$y-: $vo >$vo.$y 
    done
    cat $vo* > $vo.ext
    mv $vo.ext $vo
    rm $vo.*
done

