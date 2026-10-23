# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

# [0.4.1-beta]

Fix invisible text labels on macOS when system dark mode is enabled by pinning light appearance mode (#51).
Fix garbled/clipped UI text on Tails OS: substitute an available system font when the "Outfit" font is not installed (#59).
Show a clear error popup and exit cleanly when the PC/SC service (pcscd) is unavailable (#60).
Fix Satodime vault reset possible without checking the confirmation checkbox (#40).
Fix authenticity check displaying a stale result when a card was checked after a genuine one.
Move label editing from the settings menus to the About screen, via a pen icon button next to the card label.
Add NFC enable/disable screen with radio state selector and blocked-state warning, accessible via a switch icon button next to the NFC status on the About screen.
Add Satochip "Reset seed" screen with backup confirmation checkbox, accessible via a seeded-state button (pen/trash icon) next to the seeded status on the About screen.


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
