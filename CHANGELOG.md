# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

# [0.4.2]

Uses pysatochip v0.18.8.

## Bug fixes

- Card authenticity check: genuine cards whose Card Manager is not selected at power-up (e.g. Seedkeeper Pro) were reported as not authentic ("Certificate subject ... does not match the card serial number da39a3ee..."), because the card serial number was read as empty. Fixed in pysatochip v0.18.8.

## Build

- **macOS:** the DMG build failed with dmgbuild 2.0, which dropped the UDBZ (bzip2) image format. The DMG now uses the ULFO format (LZFSE compression, macOS 10.11+) and dmgbuild is pinned to 2.0.0.

# [0.4.1]

Uses pysatochip v0.18.7 & pycryptotools v0.4.1.

## Highlights

- **Seedkeeper:** secrets are now hidden by default, the secret list gains search and type filters, and every sensitive field gets QR code and copy-to-clipboard buttons.
- **Satodime:** balances load in the background, there's a new refresh button, and vaults are now numbered from 1 to match the mobile apps.
- **About screen:** new controls for NDEF, NFC, card label and Satochip seed reset.
- **Faster, more stable UI:** long lists display instantly, the app no longer hangs on close, and many Linux, macOS and Tails display issues are fixed.

## New features

### Seedkeeper
- Search field and secret type filter (All, Mnemonic, Password, Descriptors, Data) in the secret list, updating as you type (#31)
- Secrets (mnemonic, passphrase, password, data) hidden by default, with a Show/Hide button that resets each time a secret is opened (#45)
- QR code and copy buttons next to the Mnemonic, Passphrase, Login, URL, Password and Secret fields; the passphrase can now be exported as its own QR code (#53)
- BIP32 master fingerprint shown for mnemonics (passphrase included), so you can check it against wallets such as SeedSigner (#53)
- Large QR codes open in a popup scaled to fit the screen (#48)

### Satodime
- Refresh button on the Balance row to fetch up-to-date balances and assets without restarting (#35)
- QR code and copy buttons for the vault private key and WIF (#36)
- Vaults numbered from 1 in the UI (#38)
- "Open in explorer" button is disabled with a tooltip when no explorer link is available
- Removed the "Buy" (Paybis) button from the sealed vault screen

### Card management (About screen)
- NDEF status display and a new "Configure NDEF" screen: disable, URL, Android app (AAR), predefined choice, raw hex, or dynamic NDEF on Satodime (#58)
- NFC enable/disable screen, with a warning when NFC is blocked
- Satochip "Reset seed" screen with a backup confirmation checkbox
- Card label editing moved here from the settings menus

### Logging
- New `-l/--log-file [PATH]` option (default `~/.satotools/satotools.log` for binaries)
- `-v/--verbose` now controls log levels for all modules, including pysatochip; uncaught exceptions are logged

## Security & privacy
- Clipboard data copied by the app is cleared after 30 seconds and on exit (only if it's still the app's data)
- Seedkeeper secret values and Satocash token proofs are no longer written to logs
- Seedkeeper detail fields are now read-only (#47)
- Satodime vault reset now requires the confirmation checkbox (#40)

## Performance
- All lists (Seedkeeper secrets, logs and backup results, Satocash balances, Satodime assets) are drawn on a single canvas and display instantly; this also fixes an X BadAlloc crash on Linux with many secrets
- Satodime balances are fetched in the background: vaults appear immediately, card removal isn't delayed, and the window no longer freezes during refresh
- The app closes instantly instead of hanging for several seconds

## Bug fixes
- Satodime ownership status not refreshed when a different card is inserted (#43)
- Crash when inserting a Satodime with more vaults than the previous card
- Duplicated and cut-off rows in Satodime asset tables
- Password details showing or hiding the URL field based on the login instead of the URL
- Authenticity check showing a stale result after checking a genuine card
- Mouse wheel scrolling now works on Linux and scrolls the list under the pointer

## Platform fixes
- **macOS:** invisible text labels in system dark mode (#51)
- **Tails OS:** garbled or clipped text when the Outfit font is missing (#59)
- **Linux:** copy to clipboard no longer crashes without xclip/xsel (pyperclip dependency removed); hand cursor now shown over clickable elements
- Clear error message and clean exit when the PC/SC service (pcscd) is unavailable (#60)

# [0.4.0-beta]

Add Satocash integration.
Add binaries code signing in CI: Windows via Azure Artifact Signing, macOS via Apple Developer ID signing + notarization (on tag pushes and manual workflow dispatch).

# [0.3.0-beta]

Add Satodime integration.

## [0.2.1] - 2024-11

Various minor patch, improvements and UI adjustments.
Add GPLv3 license.

## [0.2.0] - 2024-11

Add seedkeeper integration

## [0.1.0] - 2024-07

### Added

- Initial version of satochip-utils: unified functionalities of various Satochip tools into a single application.
