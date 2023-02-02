@echo off
echo.
echo Notes about how to run findRig on Windoze 10
echo.
echo Already should have matplotlib, basemap installed from demos.
echo.
echo To run script directly:
echo.
        findRig.py
echo.
echo Compile with - works on both windoz and linux:
echo.
        pyinstaller --onefile findRig.py
echo.
echo To run compiled binary - works on both windows and linux:
echo.
        dist\findRig.exe 
echo.
echo     Run Inno Setup Compiler end follow the prompts to create an installer
echo     This installer works on Windoz 10 end Bottles!
echo.
