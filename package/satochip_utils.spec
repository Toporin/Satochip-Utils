# -*- mode: python ; coding: utf-8 -*-

import os
import sys
import platform
from package.build_win_verinfo import fill_version_info

from version import VERSION

current_path = os.path.dirname(os.path.abspath("satochip_utils.spec"))
sys.path.append(current_path)

ICON = "../satochip_utils.ico"
FILE_DESCRIPTION = "Satochip-Utils application executable"
COMMENTS = "Simple GUI tool to configure Satochip/Satodime/Seedkeeper cards."

os_system = platform.system()
if os_system == "Windows":
    os_platform = "win"
elif os_system == "Linux":
    os_platform = "linux"
elif os_system == "Darwin":
    os_platform = "mac"
else:
    raise Exception("Unknown platform target")
plt_arch = platform.machine().lower()
BIN_PKG_NAME = f"Satochip-Utils-{os_platform}-{plt_arch}-{VERSION}"

pkgs_remove = [
#    "sqlite3",
#    "tcl85",
#    "tk85",
#    "_sqlite3",
#    "_tkinter",
#    "libopenblas",
#    "libdgamln",
#    "libdbus",
]

datai = [
    (ICON, "gui/"),
    ("../pysatochip/cert/*", "pysatochip/cert/"),
    ("../pictures_db/*", "pictures_db/"),
]

hiddeni = []
if os_platform == "linux":
    hiddeni += ["PIL._tkinter_finder"]

a = Analysis(
    ["../satochip_utils.py"],
    pathex=[current_path],
    binaries=[],
    datas=datai,
    hiddenimports=hiddeni,
    hookspath=[],
    runtime_hooks=[],
#    excludes=[
#        "_gtkagg",
#        "_tkagg",
#        "curses",
#        "pywin.debugger",
#        "pywin.debugger.dbgcon",
#        "pywin.dialogs",
#        "libopenblas",
#        "libdgamln",
#    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

for pkg in pkgs_remove:
    a.binaries = [x for x in a.binaries if not x[0].startswith(pkg)]

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

if os_platform == "win":
    fill_version_info(BIN_PKG_NAME, VERSION, FILE_DESCRIPTION, COMMENTS)
    version_info_file = "version_info"
else:
    version_info_file = None

exe_options = [a.scripts]

if os_platform == "mac":
    bins_apart = True
    BIN_PKG_NAME = "satochip_utils"
else:
    bins_apart = False
    exe_options += [a.binaries, a.zipfiles, a.datas]

exe = EXE(
    pyz,
    *exe_options,
    [],
    exclude_binaries=bins_apart,
    name=BIN_PKG_NAME,
    icon=ICON,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    version=version_info_file,
)

if os_platform == "mac":
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name="satochip_utils-bundle",
    )

    app = BUNDLE(
        coll,
        name="satochip_utils.app",
        icon=ICON,
        bundle_identifier="io.satochip.utils",
        version=VERSION,
        info_plist={
            "NSPrincipalClass": "NSApplication",
            "NSHighResolutionCapable": True,
            "NSAppleScriptEnabled": False,
            "CFBundleIdentifier": "io.satochip.utils",
            "CFBundleName": "satochip_utils",
            "CFBundleDisplayName": "satochip_utils",
            "CFBundleVersion": VERSION,
            "CFBundleShortVersionString": VERSION,
            "LSEnvironment": {
                "LANG": "en_US.UTF-8",
                "LC_CTYPE": "en_US.UTF-8",
            },
            "NSHumanReadableCopyright": "Copyright (C) 2024 Satochip",
        },
    )