# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

# [0.4.1-beta]

Fix invisible text labels on macOS when system dark mode is enabled by pinning light appearance mode (#51).
Fix garbled/clipped UI text on Tails OS: substitute an available system font when the "Outfit" font is not installed (#59).
Show a clear error popup and exit cleanly when the PC/SC service (pcscd) is unavailable (#60).
Fix Satodime vault reset possible without checking the confirmation checkbox (#40).
Fix Satodime ownership status not refreshed when another card is inserted: the previous card's ownership (and unlock secret) was kept, so the new card showed "You are the owner" and vault operations failed (#43).
Fix crash when inserting a Satodime with more vaults than the previously inserted one (vault data was not resized).
Satodime vaults are now numbered from 1 in the UI (menu, vault screens and popups), matching the mobile apps (#38).
Fix Seedkeeper secret details screens: output fields are now read-only (selection and copy to clipboard still work) (#47).
Fix large QR codes not fitting on screen: Seedkeeper "QR code" and "SeedQR" buttons now open the QR code in a popup, scaled to fit the screen (#48).
Add QR code buttons next to the Satodime vault "Private key:" and "WIF:" labels, showing the key as a QR code in a popup (#36).
Seedkeeper mnemonic details: add QR code buttons next to the "Mnemonic:" and "Passphrase:" labels, so the passphrase can be exported as a separate QR code; remove the duplicate "QR code" button (SeedQR is kept) (#53).
Seedkeeper mnemonic details: display the BIP32 master fingerprint of the seed (including passphrase), so wallets such as SeedSigner can be checked (#53).
Seedkeeper password and data/descriptor details: add QR code buttons next to the "Login:", "Url:", "Password:" and "Secret:" labels, and remove the duplicate "QR code" button.
Fix Seedkeeper password details: the URL field was shown or hidden depending on the login instead of the URL.
Fix "copy to clipboard" crashing on Linux when xclip/xsel is not installed: use the Tk clipboard instead of pyperclip (dependency removed).
Add "copy to clipboard" icon buttons next to every QR code icon (Seedkeeper mnemonic, passphrase, password, login, URL and secret fields; Satodime private key and WIF).
Clear data copied to the clipboard by the app after 30 seconds, and when the app is closed (only if the clipboard still holds that data).
Seedkeeper secret details: secrets (mnemonic, passphrase, password, secret data) are now hidden by default; the bottom-right button shows "Show" and switches to "Hide" once the secret is displayed. The hidden state is reset each time a secret is opened (#45).
Seedkeeper secret details: the "export not allowed" message is always displayed in plaintext, with the Show/Hide button disabled.
Seedkeeper secret list: add a search field (filter by label) and a secret type filter (All, Mnemonic, Password, Descriptors, Data); the list updates as you type (#31).
About screen: show the NDEF status (unsupported, disabled, dynamic or the actual NDEF content) and add a button to configure it. The new "Configure NDEF" screen can disable NDEF, set a URL, an Android app (AAR), a predefined choice, a raw hex NDEF or (Satodime only) a dynamic NDEF (#58).
Seedkeeper secret list: draw the table on a single canvas, so that long lists display and filter instantly (displaying many secrets was very slow and could crash with an X BadAlloc error on Linux).
Use the same canvas table for all lists (Seedkeeper card logs and backup result, Satocash balances, Satodime tokens/NFTs): long lists now display instantly. Satodime asset tables no longer duplicate their rows on each refresh, and their last rows are no longer cut off.
Fix mouse wheel scrolling in lists: scrolling now works on Linux, and applies to the list under the pointer (the last created list used to capture all mouse wheel events).
Fix authenticity check displaying a stale result when a card was checked after a genuine one.
Move label editing from the settings menus to the About screen, via a pen icon button next to the card label.
Add NFC enable/disable screen with radio state selector and blocked-state warning, accessible via a switch icon button next to the NFC status on the About screen.
Add Satochip "Reset seed" screen with backup confirmation checkbox, accessible via a seeded-state button (pen/trash icon) next to the seeded status on the About screen.
Add `-l`/`--log-file [PATH]` option to write logs to a file (default `~/.satotools/satotools.log` for binaries, where no console is shown).
Fix logging: `-v`/`--verbose` now controls the level of all app modules and pysatochip (DEBUG logs were always shown, while pysatochip DEBUG logs were never shown); uncaught exceptions are now logged.
Stop logging sensitive data: Satocash token contents (proofs) and Seedkeeper secret values are no longer written to logs.


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
