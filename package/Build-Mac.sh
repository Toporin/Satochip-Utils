#!/bin/sh

# Build the MacOS binary package release

# Requires Xcode developer tools
# Python 3.9
# If needed, python3 -m venv unibenv should trigger the dev tools installation


rm -Rf build
rm -Rf dist

echo Initializing venv ...
python3 -m venv unibenv
source unibenv/bin/activate

echo Installing pip dependencies ...
python -m pip install pip==21.2.1
python -m pip install .

python -m pip install pyinstaller==5.13.2

echo Building package ...
python -OO -m PyInstaller package/satochip_utils.spec
deactivate

rm -Rf dist/satochip_utils-bundle
ls -l dist/satochip_utils.app/Contents/MacOS/
chmod +x dist/satochip_utils.app/Contents/MacOS/satochip_utils
ls -l dist/satochip_utils.app/Contents/MacOS/

#echo DEBUG ls -l /usr/local/
#ls -l /usr/local/
#echo DEBUG ls -l /usr/local/Cellar/
#ls -l /usr/local/Cellar/
#echo DEBUG ls -l /usr/local/Cellar/
#ls -l /usr/local/Cellar/
#echo search tcl tk
#ls -R /usr/local/Cellar/tcl-tk/

#echo copy tcl lib
#ls -l /usr/local/Cellar/tcl-tk/8.6.14/lib/tcl8.6
#mkdir -p dist/satochip_utils.app/Contents/lib/tcl8.6
#cp -R /usr/local/Cellar/tcl-tk/8.6.14/lib/tcl8.6/ dist/satochip_utils.app/Contents/lib/tcl8.6
#ls -l dist/satochip_utils.app/Contents/lib/tcl8.6

#echo copy tk
#ls -l /usr/local/Cellar/tcl-tk/8.6.14/lib/tk8.6
#mkdir -p dist/satochip_utils.app/Contents/lib/tk8.6
#cp -R /usr/local/Cellar/tcl-tk/8.6.14/lib/tk8.6/ dist/satochip_utils.app/Contents/lib/tk8.6
#ls -l dist/satochip_utils.app/Contents/lib/tk8.6

#echo copy tcl lib to MacOs
#cp -R /usr/local/Cellar/tcl-tk/8.6.14/lib/tcl8.6 dist/satochip_utils.app/Contents/MacOS
#ls -l dist/satochip_utils.app/Contents/MacOS/

setopt +o nomatch
rm -Rf dist/satochip_utils.app/Contents/MacOS/*-info
rm -Rf dist/satochip_utils.app/Contents/Resources/*-info
setopt -o nomatch

echo Compilation done.
echo Binary result is in the dist folder.

echo Now need : code sign, notarization, dmg bundling, and notarization of the bundle.
echo DMG building requires biplist and dmgbuild.

python -m pip install biplist
python -m pip install dmgbuild
python -m dmgbuild -s package/dmg_build.py volume_name satochip_utils.dmg
ls -l
ls -l dist/