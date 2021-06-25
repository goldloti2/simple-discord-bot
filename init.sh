#!/bin/bash

if ![-d "log/discord"]
then
	mkdir log log/discord
fi

if ![-f "settings/setting.py"]
then
    echo "Start initialize."
	mkdir settings
	python tools/gen_setting.py
	echo "initialize done."
else
	echo "already initialized."
fi