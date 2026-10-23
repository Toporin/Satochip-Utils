# Sato-Tools

Your one stop shop to manage your Satochip cards, including Satodime and Seedkeeper.
Change your PIN code, reset your card, setup your hardware wallet and many more...
Manage your crypto-related secrets using your Seedkeeper card, generate password like a pro. Backup your seedphrases and many more...

_________________

## Installation & running from source

### Requirements

- **Python 3.8 – 3.12** (some pinned dependencies, such as `pillow==10.3.0` and `pyscard==2.0.9`, may not install on newer versions)
- **Tkinter**, which `customtkinter` needs
- A **PC/SC smart card service** and a USB or NFC card reader

### 1. Install system dependencies

**Windows**
- Install Python from [python.org](https://www.python.org/downloads/). Tick *"Add python.exe to PATH"*. Tkinter is included.
- Nothing else is needed: Windows comes with a smart card service.

**Linux (Debian/Ubuntu)**
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip python3-tk \
                 pcscd libpcsclite-dev swig build-essential python3-dev
sudo systemctl enable --now pcscd
```
For Fedora: `sudo dnf install python3-tkinter pcsc-lite pcsc-lite-devel swig gcc python3-devel`, then `sudo systemctl enable --now pcscd`.

**macOS**
- macOS comes with a PC/SC service.
- With Homebrew Python, add Tkinter:
```bash
  brew install python@3.12 python-tk@3.12 swig
```
  (`swig` is only needed if `pyscard` has to be built from source.)

### 2. Get the code and install Python dependencies

```bash
git clone https://github.com/Toporin/Satochip-Utils.git
cd Satochip-Utils
python3 -m venv .venv
```

Activate the virtual environment:

| OS | Command |
|----|---------|
| Linux / macOS | `source .venv/bin/activate` |
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |
| Windows (cmd) | `.venv\Scripts\activate.bat` |

Then install:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Run

Plug in your card reader, activate the virtual environment, and run:
```bash
python satochip_utils.py
```
For verbose logs run:
```bash
python satochip_utils.py -v
```
On Windows, use `python` or `py`. On Linux/macOS, use `python3` if `python` is not available.

### Troubleshooting

- **No card or reader detected (Linux):** check that `pcscd` is running with `systemctl status pcscd`.
- **`ModuleNotFoundError: No module named 'tkinter'`:** install the Tk package for your OS (see step 1).
- **`pyscard` fails to build:** make sure `swig`, a C compiler and the PC/SC development headers are installed. Or use a Python version that has prebuilt `pyscard` wheels (3.8–3.12).


## Setup and manage your Satochip hardware wallet

> 🛒 [Buy your Satochip hardware wallet here 🔗](https://satochip.io/product/satochip/).
> 🛒 [Buy your smart card reader here 🔗](https://satochip.io/product/chip-card-reader/).

### Setup your card
Sato-Tools allows you to setup your **Satochip hardware wallet** by:
- Set a PIN code (from 4 to 16 chars)
- Set a label
- Seed your Satochip hardware wallet 

### Seed your Satochip hardware wallet
Here you can either **import** an existing **12 or 24 words BIP39 seedphrase** and optionally add a **passphrase**.
Or you can randomly **generate** a **12 or 24 words BIP39 seedphrase** and optionally add a **passphrase**.

**⚠️ The seedphrase is very important and necessary to recover your wallet. Don't share it, don't lose it. ⚠️**
_👉 Keep it in a safe place using a [Seedkeeper🔗](https://satochip.io/product/seedkeeper/)._

What's a seedphrase: [check this 🔗](https://satochip.io/whats-a-seedphrase/).
What's a passphrase: [check this 🔗](https://satochip.io/passphrase/).

### Manage your card
You can also: 
- Edit the PIN code
- Edit the label
- Check the authenticity of the card
- Factory reset your card
- Check the card's information

_________________

## Setup and manage your Seedkeeper

> 🛒 [Buy your Seedkeeper here 🔗](https://satochip.io/product/seedkeeper/).
> 🛒 [Buy your smart card reader here 🔗](https://satochip.io/product/chip-card-reader/).

### Setup your card
Sato-Tools allows you to setup your **Seedkeeper** by:
- Set a PIN code (from 4 to 16 chars)
- Set a label

### Manage your card
You can also: 
- Edit the PIN code
- Edit the label
- Check the authenticity of the card
- Factory reset your card
- Check the card's information

### Manage your secrets
Regarding your secrets, you can: 
- Generate and import strong passwords like a pro
- Generate and import BIP39 mnemonic seedphrases
- Import your existing seedphrases including the passphrase
- Manage your Bitcoin wallet descriptors
- Import some raw text into your Seedkeeper's secure memory

### Backup your Seedkeeper to another one
Create a carbon copy of your main Seedkeeper card to another one in just a few clicks.
_________________

## Manage your Satodime

> 🛒 [Buy your Satodime here 🔗](https://satochip.io/product/satodime/).
> 🛒 [Buy your smart card reader here 🔗](https://satochip.io/product/chip-card-reader/).

### Manage your card
You can: 
- Edit the label
- Check the authenticity of the card
- Check the card's information

_________________

## Factory reset explained

The factory reset feature allows you to reset your Satochip or Seedkeeper card to its factory state. 
This means that all private keys, saved information and settings (such as PIN code or label) will be deleted from the device.

Before starting the reset process, make sure you have a backup of the contents; either the seedphrase (from your Satochip hardware wallet) or any other password stored in your card.

The reset process is simple: plug in your card, launch Sato-Tools, click on "Reset my card" in settings, read the text and click on "Start".
Then follow the pop-up wizard and remove your card from the smart card reader, then insert it again. And do this several times. 

_________________

## More information…

💮 Join us on [Telegram](https://t.me/Satochip)

🐦 Follow us on [Twitter](https://twitter.com/satochip)

👾 Check out our [website](https://satochip.io/)

🔨 Take a look at the sources [GitHub](https://github.com/Toporin)