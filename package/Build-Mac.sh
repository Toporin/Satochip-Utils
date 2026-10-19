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
#python -m pip install pip==21.2.1
python -m ensurepip --upgrade
python -m pip install --upgrade setuptools
python -m pip install --upgrade --force-reinstall Pillow
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

# Code signing & notarization of the app bundle.
# Only performed when MACOS_SIGN_IDENTITY is set (CI release builds); requires the
# signing certificate in the keychain and the notarization credentials in
# MACOS_NOTARY_KEY / MACOS_NOTARY_KEY_ID / MACOS_NOTARY_ISSUER_ID.
if [ -n "$MACOS_SIGN_IDENTITY" ]; then
    set -e
    echo "Code signing the app bundle with identity: $MACOS_SIGN_IDENTITY"
    APP_PATH="dist/satochip_utils.app"
    # sign nested libraries first (inside-out)
    find "$APP_PATH/Contents" \( -name "*.so" -o -name "*.dylib" \) -print0 | xargs -0 codesign -f --timestamp --options runtime --sign "$MACOS_SIGN_IDENTITY"
    # sign the main executable then the whole bundle, with hardened runtime and entitlements
    codesign -f --timestamp --options runtime --entitlements package/entitlements.plist --sign "$MACOS_SIGN_IDENTITY" "$APP_PATH/Contents/MacOS/satochip_utils"
    codesign -f --timestamp --options runtime --entitlements package/entitlements.plist --sign "$MACOS_SIGN_IDENTITY" "$APP_PATH"
    codesign --verify --deep --strict --verbose=2 "$APP_PATH"
    echo "Notarizing the app bundle..."
    echo "$MACOS_NOTARY_KEY" | base64 --decode -o notary_key.p8
    ditto -c -k --sequesterRsrc --keepParent "$APP_PATH" satochip_utils.zip
    xcrun notarytool submit satochip_utils.zip --key notary_key.p8 --key-id "$MACOS_NOTARY_KEY_ID" --issuer "$MACOS_NOTARY_ISSUER_ID" --wait
    xcrun stapler staple -v "$APP_PATH"
    rm -f satochip_utils.zip
    set +e
fi

echo DMG bundling.
echo DMG building requires biplist and dmgbuild.

python -m pip install biplist
python -m pip install dmgbuild
python -m dmgbuild -s package/dmg_build.py volume_name satochip_utils.dmg

# Code signing & notarization of the dmg.
if [ -n "$MACOS_SIGN_IDENTITY" ]; then
    set -e
    echo "Code signing the dmg..."
    codesign -f --timestamp --options runtime --sign "$MACOS_SIGN_IDENTITY" dist/satochip_utils.dmg
    echo "Notarizing the dmg..."
    xcrun notarytool submit dist/satochip_utils.dmg --key notary_key.p8 --key-id "$MACOS_NOTARY_KEY_ID" --issuer "$MACOS_NOTARY_ISSUER_ID" --wait
    xcrun stapler staple -v dist/satochip_utils.dmg
    rm -f notary_key.p8
    set +e
fi

ls -l
ls -l dist/