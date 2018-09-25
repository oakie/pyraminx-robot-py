#!/bin/bash

/usr/bin/python3 server.py
for f in /sys/class/tacho-motor/*/command; do
    echo reset > ${f}
done
