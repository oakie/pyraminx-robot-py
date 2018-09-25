#!/bin/bash

/usr/bin/python3 $1
for f in /sys/class/tacho-motor/*/command; do
    echo reset > ${f}
done
