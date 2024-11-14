import os
import sys
import tkinter
import unicodedata

import customtkinter
import logging
import hashlib
import pyqrcode
from mnemonic import Mnemonic

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_fingerprint_from_authentikey_bytes(authentikey_bytes):
    logger.debug(f"getFingerprintFromAuthentikeyBytes for authentikeyBytes: {authentikey_bytes.hex()}")
    raw_secret = bytes([len(authentikey_bytes)]) + authentikey_bytes
    fingerprint = hashlib.sha256(raw_secret).hexdigest()[0:8]
    logger.debug(f"getFingerprintFromAuthentikeyBytes fingerprint: {fingerprint}")
    return fingerprint


def toggle_entry_visibility(entry: customtkinter.CTkEntry):
    try:
        current_state = entry.cget("show")
        new_state = "" if current_state == "*" else "*"
        entry.configure(show=new_state)
    except Exception as e:
        logger.error(f"018 Error toggling passphrase visibility: {e}", exc_info=True)


def toggle_textbox_visibility(textbox: customtkinter.CTkTextbox, original_text):
    try:
        textbox.configure(state='normal')
        # get the current content of the textbox
        current_text = textbox.get("1.0", "end-1c")

        if current_text == '*' * len(original_text):
            # Si la textbox contient uniquement des étoiles, afficher le texte original
            textbox.delete("1.0", "end")
            textbox.insert("1.0", original_text)
            #textbox.configure(state='disabled')
        else:
            # Sinon, masquer le texte avec des étoiles
            textbox.delete("1.0", "end")
            textbox.insert("1.0", '*' * len(original_text))
            #textbox.configure(state='disabled')
    except Exception as e:
        logger.error(f"018 Error toggling mnemonic visibility: {e}", exc_info=True)


def update_textbox(textbox: customtkinter.CTkTextbox, new_text):
    textbox.configure(state='normal')  # allows to modify content
    textbox.delete("1.0", "end")
    textbox.insert("1.0", new_text)
    #textbox.configure(state='disabled')


def show_qr_code(qr_data: str, label: customtkinter.CTkLabel): #todo implement seedqr!!
    # Fonction pour générer et afficher le QR code
    qr = pyqrcode.create(qr_data, error='L')
    qr_xbm = qr.xbm(scale=3) #if len(mnemonic.split()) <= 12 else qr.xbm(scale=2) # todo: tune scale
    # Convert XBM code to Tkinter image
    qr_bmp = tkinter.BitmapImage(data=qr_xbm)
    label.configure(image=qr_bmp)
    label.image = qr_bmp  # prevent garbage collection
    label.place()


def reset_qr_code(label: customtkinter.CTkLabel):
    # define a small blank image to replace existing qr code
    qr_xbm = """
#define im_width 8
#define im_height 1
static char im_bits[] = {
0x00
};
"""
    # Convert XBM code to Tkinter image
    qr_bmp = tkinter.BitmapImage(data=qr_xbm)
    label.configure(image=qr_bmp)
    label.image = qr_bmp  # prevent garbage collection
    label.place()


def mnemonic_to_entropy_bytes(mnemonic) -> bytearray:
    MNEMONIC = Mnemonic("english")
    if not MNEMONIC.check(mnemonic):
        raise ValueError("Invalid mnemonic")

    # Generate entropy from mnemonic
    entropy = MNEMONIC.to_entropy(mnemonic)
    return entropy


def mnemonic_to_entropy_string(mnemonic) -> str:
    try:
        # get the english wordlist
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        logging.debug(f"Application path: {application_path}")

        # Construct the path to the wordlist directory
        wordlist_dir = os.path.join(application_path, 'wordlist')
        logger.info(f"wordlist directory: {wordlist_dir}")

        # Check if the directory exists
        wordlist_path = os.path.join(wordlist_dir, "english.txt")
        logger.info(f"wordlist path: {wordlist_path}")

        # load list from file
        wordlist = None
        if os.path.exists(wordlist_path) and os.path.isfile(wordlist_path):
            with open(wordlist_path, "r", encoding="utf-8") as f:
                wordlist = [w.strip() for w in f.readlines()]

        # compute standard SeedQR data
        if isinstance(mnemonic, str):
            words = mnemonic.split(" ")
        elif isinstance(mnemonic, list):
            words = mnemonic
        else:
            raise ValueError("Mnemonic should be a string or a list")

        if len(words) not in [12, 15, 18, 21, 24]:
            raise ValueError(
                "Number of words must be one of the following: [12, 15, 18, 21, 24], but it is not (%d)."
                % len(words)
            )
        # Look up all the words in the list and construct the
        # concatenation of the original entropy and the checksum.
        entropy_int_string = ""
        for word in words:
            # Find the words index in the wordlist
            ndx = wordlist.index(normalize_string(word))
            if ndx < 0:
                raise LookupError('Unable to find "%s" in word list.' % word)
            entropy_int_string += str(ndx).zfill(4)

        return entropy_int_string

    except Exception as ex:
        logger.error(f"Failed to convert mnemonic to entropy: {str(ex)}", exc_info=True)
        return f"Failed to convert mnemonic to entropy: {str(ex)}"

def normalize_string(txt) -> str:
    if isinstance(txt, bytes):
        utxt = txt.decode("utf8")
    elif isinstance(txt, str):
        utxt = txt
    else:
        raise TypeError("String value expected")

    return unicodedata.normalize("NFKD", utxt)