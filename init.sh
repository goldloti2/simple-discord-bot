#!/bin/bash

if ![-f "settings/setting.py"]
then
    echo "Start initialize."
	mkdir settings
	python tools/gen_setting.py
	echo "initialize done."
else
	echo "already initialized."
fi