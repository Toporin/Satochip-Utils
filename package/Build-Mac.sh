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
chmod +x dist/satochip_utils.app/Contents/MacOS/satochip_utils
setopt +o nomatch
rm -Rf dist/satochip_utils.app/Contents/MacOS/*-info
rm -Rf dist/satochip_utils.app/Contents/Resources/*-info
setopt -o nomatch

echo Compilation done.
echo Binary result is in the dist folder.

echo Now need : code sign, notarization, dmg bundling, and notarization of the bundle.
echo DMG building requires biplist and dmgbuild.