@echo OFF

if not exist log\discord mkdir log log\discord 

if not exist settings\setting.json goto Initialize
goto Already

:Initialize
    echo Start initialize.
	mkdir settings
	python tools\gen_setting.py
	echo initialize done.
    goto End

:Already
	echo already initialized.
	goto End

:End
	pause
	exit /b 0