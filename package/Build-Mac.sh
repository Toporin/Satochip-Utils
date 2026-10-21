#!/bin/sh

# Build the MacOS binary package release

# Requires Xcode developer tools
# Python 3.9
# If needed, python3 -m venv unibenv should trigger the dev tools installation


# stop at first error (otherwise a failed build goes unnoticed until much later)
set -e

rm -Rf build
rm -Rf dist

echo Initializing venv ...
python3 -m venv unibenv
source unibenv/bin/activate

echo Installing pip dependencies ...
#python -m pip install pip==21.2.1
python -m ensurepip --upgrade
# setuptools >= 81 no longer ships pkg_resources, which PyInstaller 5.13.2 requires
python -m pip install --upgrade "setuptools<81"
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

# the *-info glob may match nothing; only zsh needs nomatch disabled
if [ -n "$ZSH_VERSION" ]; then
    setopt +o nomatch
fi
rm -Rf dist/satochip_utils.app/Contents/MacOS/*-info
rm -Rf dist/satochip_utils.app/Contents/Resources/*-info
if [ -n "$ZSH_VERSION" ]; then
    setopt -o nomatch
fi

echo Compilation done.
echo Binary result is in the dist folder.

# Submit $1 to the Apple notary service; on rejection, dump the notary log
# (which lists the exact issues) and abort.
notarize() {
    xcrun notarytool submit "$1" --key notary_key.p8 --key-id "$MACOS_NOTARY_KEY_ID" --issuer "$MACOS_NOTARY_ISSUER_ID" --wait --output-format json | tee notary_submit.json
    NOTARY_STATUS=$(python3 -c "import json; print(json.load(open('notary_submit.json')).get('status', ''))" 2>/dev/null || true)
    if [ "$NOTARY_STATUS" != "Accepted" ]; then
        SUBMISSION_ID=$(python3 -c "import json; print(json.load(open('notary_submit.json'))['id'])" 2>/dev/null || true)
        echo "ERROR: notarization of $1 failed (status: ${NOTARY_STATUS:-submission error})"
        if [ -n "$SUBMISSION_ID" ]; then
            xcrun notarytool log "$SUBMISSION_ID" --key notary_key.p8 --key-id "$MACOS_NOTARY_KEY_ID" --issuer "$MACOS_NOTARY_ISSUER_ID" || true
        fi
        exit 1
    fi
    rm -f notary_submit.json
}

# Code signing & notarization of the app bundle.
# Only performed when MACOS_SIGN_IDENTITY is set (CI release builds); requires the
# signing certificate in the keychain and the notarization credentials in
# MACOS_NOTARY_KEY / MACOS_NOTARY_KEY_ID / MACOS_NOTARY_ISSUER_ID.
if [ -n "$MACOS_SIGN_IDENTITY" ]; then
    echo "Code signing the app bundle with identity: $MACOS_SIGN_IDENTITY"
    APP_PATH="dist/satochip_utils.app"
    # sign all nested Mach-O binaries first (inside-out); filtering by content,
    # not extension, as e.g. the bundled Python framework library (Contents/MacOS/Python)
    # has no extension and would otherwise keep its original (python.org) signature
    find "$APP_PATH/Contents" -type f -print0 | while IFS= read -r -d '' f; do
        if file "$f" | grep -q Mach-O; then
            codesign -f --timestamp --options runtime --sign "$MACOS_SIGN_IDENTITY" "$f"
        fi
    done
    # sign the main executable then the whole bundle, with hardened runtime and entitlements
    codesign -f --timestamp --options runtime --entitlements package/entitlements.plist --sign "$MACOS_SIGN_IDENTITY" "$APP_PATH/Contents/MacOS/satochip_utils"
    codesign -f --timestamp --options runtime --entitlements package/entitlements.plist --sign "$MACOS_SIGN_IDENTITY" "$APP_PATH"
    codesign --verify --deep --strict --verbose=2 "$APP_PATH"
    echo "Notarizing the app bundle..."
    echo "$MACOS_NOTARY_KEY" | base64 --decode -o notary_key.p8
    ditto -c -k --sequesterRsrc --keepParent "$APP_PATH" satochip_utils.zip
    notarize satochip_utils.zip
    xcrun stapler staple -v "$APP_PATH"
    rm -f satochip_utils.zip
fi

echo DMG bundling.
echo DMG building requires biplist and dmgbuild.

python -m pip install biplist
python -m pip install dmgbuild
python -m dmgbuild -s package/dmg_build.py volume_name satochip_utils.dmg

# Code signing & notarization of the dmg.
if [ -n "$MACOS_SIGN_IDENTITY" ]; then
    echo "Code signing the dmg..."
    codesign -f --timestamp --options runtime --sign "$MACOS_SIGN_IDENTITY" dist/satochip_utils.dmg
    echo "Notarizing the dmg..."
    notarize dist/satochip_utils.dmg
    xcrun stapler staple -v dist/satochip_utils.dmg
    rm -f notary_key.p8
fi

ls -l
ls -l dist/