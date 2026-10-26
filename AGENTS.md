# AGENTS.md — Satochip-Utils

## Project overview

Satochip-Utils (product name "Sato-Tools") is a desktop GUI application to set up and manage
the Satochip family of javacard-based smart cards, from a standard PC/SC card reader:

- **Satochip** — hardware wallet (BIP39 seed import/generation, PIN/label management).
- **Seedkeeper** — secure secret manager (passwords, mnemonics, wallet descriptors, 2FA, card-to-card backup).
- **Satodime** — bearer crypto vaults (seal/unseal/reset vaults for BTC, ETH, BCH, LTC, Polygon, Counterparty).
- **Satocash** — Cashu e-cash token card (balances, import/export tokenv4).

License: GPLv3. Current version: `0.4.0-beta` (single source of truth in `version.py`).

## Tech stack

- **Python 3** (>= 3.8 per `setup.py`; CI builds on 3.10–3.12).
- **GUI**: `customtkinter` 5.2.2 (Tkinter wrapper) + `Pillow`. Fixed 1000x600 window.
- **Smart card communication**: `pysatochip` 0.18.5 (`CardConnector`, APDUs) on top of `pyscard` (PC/SC).
  Card insertion/removal is detected via pyscard's `CardMonitor`/`CardObserver`.
- **Blockchains**: `pycryptotools` 0.3.1 (coin/address/explorer logic), `mnemonic` (BIP39).
- **Misc**: `pyqrcode`, `cbor2` (Cashu token serialization).
- **Packaging**: PyInstaller (`package/satochip_utils.spec`); pinned PyInstaller 6.7.0 on Linux,
  5.13.2 on Windows/macOS (Windows build recompiles the bootloader from source).
- There is a local `.venv` (Python 3.12) at the repo root; system package `python3-pyscard`
  and `libpcsclite-dev` are needed on Linux for smartcard access.

## Repository layout

Flat layout — all application modules live at the repo root (no Python package directories).

- `satochip_utils.py` — entry point. Configures logging for the app and pysatochip (`-v`/`--verbose`
  for DEBUG, `-l`/`--log-file [PATH]` to also log to a file; modules must not call `setLevel`),
  chdirs to the application path, creates the `View` and starts the mainloop.
- `view.py` — `View(customtkinter.CTk)`, the main window. Owns every frame, all `show_*`
  navigation methods, popup dialogs (`show()`, `get_pin()`), and `update_status()` which reacts
  to card insertion/removal. Also holds shared widget factories (`create_label`, `create_button`,
  `create_entry`, `create_menu_button`, `create_frame`, ...).
- `controller.py` — `Controller`, the business-logic layer. Wraps `pysatochip.CardConnector`
  as `self.cc`, loads API keys from `api_keys.ini`, and implements all card operations:
  PIN setup/change, seed import, label edit, Seedkeeper secret import/export/decode,
  Satodime vault management, Satocash/Cashu token handling.
- `applicationMode.py` — `ApplicationMode` enum (`Normal`, `FactoryResetV1/V2/V3`,
  `SeedkeeperBackup`) controlling how card insert/remove events are handled.
- `constants.py` — UI colors, coin/Slip44 dicts, Seedkeeper secret type / instruction /
  response dictionaries, debug addresses.
- `utils.py` — helpers: config path resolution, images, QR codes, entry/textbox visibility.
- `frame*.py` — one module per screen, each defining a `customtkinter.CTkFrame` subclass.
  Naming conventions:
  - `frameCard*` — card settings screens (setup PIN, change PIN, edit label, switch NFC,
    authenticity, factory reset, about, import seed).
  - `frameMenu*` — left-hand navigation menus, one per card type/state (settings, no-card,
    Seedkeeper, Seedkeeper backup, Satodime, Satocash).
  - `frameSeedkeeper*` — secret generate/import/show/list, logs, backup screens.
  - `frameSatochip*` — Satochip-specific screens (reset seed).
  - `frameSatodime*` — overview, vault, seal/unseal/reset screens.
  - `frameSatocash*` — balances, token import/export screens.
  - `frameWidget*` — reusable widgets (header, labels, canvas table used by all lists, asset table, ...).
  - Note: `FrameSeedkeeperGenerateSecretSelectType.py` deviates with a leading capital F.
- `pictures_db/` — PNG/JPG assets loaded at runtime via relative paths (`./pictures_db/...`).
- `wordlist/english.txt` — BIP39 wordlist (also bundled into `pycryptotools/` in the spec as a hack).
- `pysatochip/cert/` — root/sub CA certificates used for card authenticity verification
  (this directory ships certificates only; the library itself comes from pip).
- `package/` — PyInstaller spec and per-platform build scripts (see Build & release).
- `setup.py` / `setup.cfg` / `requirements.txt` — packaging metadata and lint config.

## Runtime architecture / event flow

The app follows a View/Controller split:

1. `satochip_utils.py` instantiates `View`, which instantiates `Controller(self)`.
2. `Controller` creates a `pysatochip.CardConnector` passing itself as the client.
3. pyscard's `CardMonitor` fires on card insertion/removal; the connector calls back through
   `Controller.request('update_status', True|False)` → `View.update_status(...)`.
   Note: these callbacks arrive from the observer thread, not the Tk main thread — frames are
   therefore only (re)created lazily when they already exist or from safe paths.
4. `View.update_status()` picks the menu/frames to display based on `controller.cc.card_type`
   (`"Satochip"`, `"SeedKeeper"`, `"Satodime"`, `"Satocash"`) and the current `ApplicationMode`.
5. Frames call `master.controller.<operation>(...)` for actions; errors and results are shown
   with `View.show(title, msg, button_txt, cmd, icon_path)` popups. PIN entry goes through
   `Controller.PIN_dialog()` / `View.get_pin()`.
6. When frozen by PyInstaller, resources are resolved under `sys._MEIPASS`; when run from source,
   relative to the repo root (`satochip_utils.py` chdirs there at startup).

## Running from source

```bash
# Linux: needs PC/SC and Tk system packages
sudo apt install libpcsclite-dev pcscd python3-tk   # plus python3-pyscard recommended

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt    # or: pip install .
python satochip_utils.py           # add -v / --verbose for DEBUG logs
```

Optional: copy `api_keys (sample).ini` to `api_keys.ini` and fill in block-explorer API keys
(Etherscan, Ethplorer, BscScan) to enable Satodime balance/NFT lookups.

## Build & release

Binary packaging uses PyInstaller driven by `package/satochip_utils.spec`, which bundles
`pictures_db/`, `wordlist/`, `pysatochip/cert/`, icons and `*.ini` files, and names artifacts
`Satochip-Utils-<os>-<arch>-<VERSION>` (VERSION imported from `version.py`).

- Linux: `bash package/Build-Linux.sh` (Ubuntu 22.04 only; script checks), legacy 20.04 variant
  `package/Build-Linux-legacy.sh` (manual builds only; no longer in CI since GitHub retired
  the ubuntu-20.04 runners). Each creates a venv, `pip install .`, installs pinned
  PyInstaller, runs the spec; result in `dist/`.
- Windows: `package/Build-Windows.bat` (downloads and recompiles the PyInstaller bootloader,
  fills Windows version info via `package/build_win_verinfo.py`).
- macOS: `package/Build-Mac.sh` (produces `satochip_utils.app` + DMG via `package/dmg_build.py`).
  When `MACOS_SIGN_IDENTITY` and the `MACOS_NOTARY_*` env vars are set (CI release builds), the
  script also code-signs and notarizes the app bundle and the DMG (hardened runtime,
  entitlements from `package/entitlements.plist`).

CI (`.github/workflows/build.yml`) builds four targets (windows-2022, ubuntu-22.04,
macos-15-intel x86_64, macos-latest arm64) on pushes to `master`, `dev`, `test_*`,
`satodime-integration`, `satocash-integration`, on any tag and on manual `workflow_dispatch`.
It injects the GitHub secret `API_KEYS` into `api_keys.ini` before building. On tag pushes and
manual dispatches (SIGN flag), the Windows exe is code-signed with Azure Artifact Signing
(`Azure/artifact-signing-action`, `AZURE_*` secrets) and the macOS app+DMG are signed/notarized
with a Developer ID certificate (`MACOS_*` secrets, keychain set up in the workflow); artifacts
are uploaded with a `-signed` suffix in that case, `-unsigned` otherwise. Linux builds are not
signed.

Releases follow Semantic Versioning; changes are tracked in `CHANGELOG.md`
(Keep a Changelog format). Bump `version.py` to cut a release.

## Code style conventions

- Language: code, docstrings and UI strings are in English (a few legacy comments are in French).
- Linting config in `setup.cfg`: flake8 `max-line-length = 100` (W503, E203, E501 ignored);
  pylint with docstring checks disabled. The black section is commented out — no enforced formatter.
- Per-module logging idiom: `logger = logging.getLogger(__name__)` then
  `logger.setLevel(logging.DEBUG)` at module top. Logging format includes file/line/function.
- Frame classes: subclass `customtkinter.CTkFrame`, take `master` (the View) as constructor arg,
  build widgets in `__init__` inside a broad `try/except` that logs with
  `logger.error(f"...: {e}", exc_info=True)`. Layout uses `.place()` with relative
  `relx`/`rely` coordinates; content frames are 750x600 with a `FrameWidgetHeader` at the top.
- Widgets are created through the View's factory helpers (`master.create_label(...)`,
  `master.create_button(...)`, `master.create_entry("*", ...)`) rather than directly.
- Card operations live in `Controller`; frames stay thin and delegate. New card features should
  follow this split.

## Testing

There is currently **no test suite** in this repository (no `tests/` directory, no pytest/unittest
configuration, no CI test job). CI only builds the binaries. Verification is manual: run the app
against a real card (or a card reader + `DEBUG_ADDR` entries in `constants.py` for UI-level
Satodime explorer checks; `DEBUG_EXPLORER` flag in `controller.py`).

## Configuration & security considerations

- `api_keys.ini` — block-explorer API keys. **Never commit it** (gitignored); only
  `api_keys (sample).ini` is tracked. CI injects it from a secret at build time.
- `satotools.ini` — runtime config file, gitignored. Location depends on run mode:
  `~/.satotools/satotools.ini` when frozen, `./.satotools.ini` next to the sources otherwise
  (see `utils.get_config_path()`).
- The app manipulates highly sensitive material: BIP39 seedphrases, passphrases, PIN codes
  (4–16 chars, entered via popup dialogs), private keys, Cashu tokens. Avoid logging secrets;
  existing code logs operations but not secret values — keep it that way.
- Card authenticity is verified on-device using the certificate chain in `pysatochip/cert/`;
  this directory must ship with the app (the PyInstaller spec bundles it).
- Factory reset (in `frameCardFactoryReset.py` / `ApplicationMode.FactoryResetV*`) wipes all keys
  and settings from the card; it requires repeated card removal/insertion cycles. Treat changes
  to this flow with extra care.
- Smartcard APDUs and secure channel handling are delegated to the `pysatochip` library —
  prefer fixing/extending behavior there rather than reimplementing card protocol code here.

## Git workflow

Main branches: `master` (releases) and `dev`, plus feature branches
(e.g. `satodime-integration`, `satocash-integration`) merged back via merge commits.
Tags trigger the full CI build matrix. The local checkout may carry a `-e` editable install
comment for the sibling `pysatochip` repo in `requirements.txt` — keep it commented in commits.
