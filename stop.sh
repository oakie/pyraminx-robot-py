#!/bin/bash

for f in /sys/class/tacho-motor/*/command; do
    echo reset > ${f}
done
