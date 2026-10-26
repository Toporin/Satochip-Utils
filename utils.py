import os
import sys
import unicodedata
from decimal import Decimal
from typing import Dict, Any
from PIL import Image, ImageTk
import customtkinter
import logging
import hashlib
import hmac
import tkinter
from mnemonic import Mnemonic
from pycryptotools.main import privtopub, bin_hash160

from constants import COIN_DECIMALS_DICT, ICON_PATH, CLIPBOARD_CLEAR_DELAY
from framePopup import FramePopup

logger = logging.getLogger(__name__)


def get_config_path():
    '''Get path for config file, depending whether app is running from sources or executable'''
    if hasattr(sys, "_MEIPASS"):
        abs_home = os.path.abspath(os.path.expanduser("~"))
        abs_dir_app = os.path.join(abs_home, f".satotools")
        if not os.path.exists(abs_dir_app):
            os.mkdir(abs_dir_app)
        cfg_path = os.path.join(abs_dir_app, "satotools.ini")
    else:
        cfg_path = os.path.abspath(".%ssatotools.ini" % os.sep)
    logger.debug(f"get_config_path cfg_path: {cfg_path}")
    return cfg_path

def get_fingerprint_from_authentikey_bytes(authentikey_bytes):
    logger.debug(f"getFingerprintFromAuthentikeyBytes for authentikeyBytes: {authentikey_bytes.hex()}")
    raw_secret = bytes([len(authentikey_bytes)]) + authentikey_bytes
    fingerprint = hashlib.sha256(raw_secret).hexdigest()[0:8]
    logger.debug(f"getFingerprintFromAuthentikeyBytes fingerprint: {fingerprint}")
    return fingerprint


def set_entry_visibility(entry: customtkinter.CTkEntry, visible: bool):
    # mask entry content with '*' when not visible
    entry.configure(show="" if visible else "*")


def set_textbox_visibility(textbox: customtkinter.CTkTextbox, text: str, visible: bool):
    # CTkTextbox has no 'show' option: replace content with '*' when not visible
    update_textbox(textbox, text if visible else '*' * len(text))


def update_textbox(textbox: customtkinter.CTkTextbox, new_text):
    textbox.configure(state='normal')  # allows to modify content
    textbox.delete("1.0", "end")
    textbox.insert("1.0", new_text)
    #textbox.configure(state='disabled')


def update_entry(entry: customtkinter.CTkEntry, new_text, make_readonly=True):
    entry.configure(state='normal')  # allows to modify content
    entry.delete(0, "end")
    entry.insert(0, new_text)
    if make_readonly:
        entry.configure(state='readonly')  # display-only, but selection/copy still possible


def make_textbox_readonly(textbox: customtkinter.CTkTextbox):
    """Make a textbox non-editable while keeping text selection and copy to clipboard.

    Blocks keyboard/mouse events that would modify the content; navigation,
    selection and copy shortcuts still work. Programmatic updates
    (delete/insert, e.g. via update_textbox) are not affected.
    """
    allowed_keysyms = {
        # navigation & selection
        "Left", "Right", "Up", "Down", "Home", "End", "Prior", "Next", "Insert",
        # modifiers (pressed alone, e.g. as part of a combo)
        "Shift_L", "Shift_R", "Control_L", "Control_R",
        "Alt_L", "Alt_R", "Meta_L", "Meta_R", "Super_L", "Super_R",
        "Caps_Lock", "Num_Lock", "Scroll_Lock",
        # misc non-editing keys
        "Escape",
    }
    copy_select_keysyms = {"c", "C", "a", "A"}

    def block_edit_events(event):
        keysym = event.keysym
        if keysym in allowed_keysyms:
            return  # navigation/selection keys & bare modifiers
        if keysym in copy_select_keysyms:
            if event.state & 0x4:  # Ctrl+C / Ctrl+A (Linux, Windows)
                return
            if sys.platform == "darwin" and event.state & 0x78:  # Cmd+C / Cmd+A (macOS)
                return
        # block any other key (printable chars, Delete, BackSpace, Tab...)
        # note: do NOT whitelist modifier bits here (e.g. 0x10): on X11, Num Lock
        # maps to Mod2 (0x10), which would let every keypress through
        return "break"

    # CTkTextbox does not proxy bind() to its internal tkinter.Text
    inner_textbox = getattr(textbox, "_textbox", textbox)
    inner_textbox.bind("<Key>", block_edit_events)
    inner_textbox.bind("<<Cut>>", lambda event: "break")
    inner_textbox.bind("<<Paste>>", lambda event: "break")
    # block middle-click paste (X11 PRIMARY selection)
    inner_textbox.bind("<ButtonRelease-2>", lambda event: "break")


def show_qr_code(qr_data: str, parent, title: str = "QR code"):
    # Display the QR code in a popup window, sized to fit the screen (see issue #48)
    FramePopup(parent, title, "Scan this QR code", button_txt="Close", qr_msg=qr_data)


# last text copied by the app, and pending clipboard clear timer (only one at a time)
_clipboard_state = {"text": None, "after_id": None}


def copy_to_clipboard(widget, text: str):
    # use Tk clipboard: works on all OS without external tools (unlike pyperclip, which needs xclip/xsel on Linux)
    root = widget.winfo_toplevel()  # main window, outlives the frames that schedule the clear timer
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()  # keep clipboard content available after the call returns (needed on some X11 setups)

    # clear clipboard after a delay, as copied data may be sensitive (restart timer on each copy)
    if _clipboard_state["after_id"] is not None:
        root.after_cancel(_clipboard_state["after_id"])
    _clipboard_state["text"] = text
    _clipboard_state["after_id"] = root.after(
        CLIPBOARD_CLEAR_DELAY * 1000, lambda: clear_copied_from_clipboard(root)
    )


def clear_copied_from_clipboard(root):
    # clear clipboard only if it still contains the text copied by the app (keep data copied from elsewhere)
    if _clipboard_state["after_id"] is not None:
        root.after_cancel(_clipboard_state["after_id"])
        _clipboard_state["after_id"] = None
    if _clipboard_state["text"] is None:
        return
    try:
        current_text = root.clipboard_get()
    except tkinter.TclError:  # clipboard empty or not text
        current_text = None
    if current_text == _clipboard_state["text"]:
        root.clipboard_clear()
        root.update()
        logger.debug("Clipboard cleared")
    _clipboard_state["text"] = None


# scrollable areas (container, canvas) handled by the mouse wheel dispatcher below
_mousewheel_scroll_areas = []


def bind_mousewheel_scrolling(container, canvas):
    # Scroll canvas with the mouse wheel while the pointer is over container.
    # A single application-wide handler dispatches events to the area under the pointer, since
    # bind_all() is global: binding it per area would make the last created area grab all events.
    # Linux (X11, Tk 8.6) sends <Button-4>/<Button-5> instead of <MouseWheel>.
    _mousewheel_scroll_areas.append((container, canvas))
    canvas.bind_all("<MouseWheel>", _on_mousewheel)  # bind_all is not allowed on customtkinter widgets
    canvas.bind_all("<Button-4>", _on_mousewheel)  # bind_all is not allowed on customtkinter widgets
    canvas.bind_all("<Button-5>", _on_mousewheel)  # bind_all is not allowed on customtkinter widgets


def _on_mousewheel(event):
    # forget destroyed areas
    _mousewheel_scroll_areas[:] = [area for area in _mousewheel_scroll_areas if area[0].winfo_exists()]
    for container, canvas in _mousewheel_scroll_areas:
        if not container.winfo_ismapped():
            continue
        try:
            widget_under_pointer = container.winfo_containing(event.x_root, event.y_root)
        except KeyError:  # pointer over a widget unknown to tkinter (e.g. Tk internal)
            continue
        path = str(widget_under_pointer) if widget_under_pointer is not None else ""
        if path != str(container) and not path.startswith(str(container) + "."):
            continue
        # check if there's actually something to scroll
        bbox = canvas.bbox("all")
        if bbox is None or bbox[3] <= canvas.winfo_height():
            return
        if event.num == 4 or event.delta > 0:
            canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            canvas.yview_scroll(1, "units")
        return


def create_icon_button(master, anchor_widget, icon_name: str, command=None, bg_color="whitesmoke"):
    # small icon button, placed just right of anchor_widget (hidden whenever anchor_widget is hidden)
    icon = convert_name_to_photo_image(icon_name, 24, 24)
    button = customtkinter.CTkButton(
        master, width=24, height=24, text="",
        border_spacing=0,
        image=icon,
        bg_color=bg_color, fg_color=bg_color,
        hover_color=bg_color, cursor="hand2",
        command=command
    )
    button.place(in_=anchor_widget, relx=1.0, x=5, rely=0.5, anchor="w")
    return button


def create_qr_button(master, label: customtkinter.CTkLabel, command=None, bg_color="whitesmoke"):
    # QR code icon button, placed just right of the given label
    return create_icon_button(master, label, "qr_code_icon.png", command, bg_color)


def create_copy_button(master, qr_button: customtkinter.CTkButton, command=None, bg_color="whitesmoke"):
    # copy to clipboard icon button, placed just right of the given QR code button
    return create_icon_button(master, qr_button, "copy_icon.png", command, bg_color)


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
        logger.debug(f"Application path: {application_path}")

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


def get_master_fingerprint(seed: bytes) -> str:
    # BIP32 master key fingerprint: first 4 bytes of hash160(compressed master pubkey)
    master_privkey = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()[:32]
    master_pubkey = privtopub(master_privkey + b"\x01")  # '01' suffix for compressed pubkey
    return bin_hash160(master_pubkey)[:4].hex()


def bip39_mnemonic_to_seed(mnemonic: str, passphrase: str = "") -> bytes:
    return Mnemonic.to_seed(mnemonic, passphrase)


def electrum_mnemonic_to_seed(mnemonic: str, passphrase: str = "") -> bytes:
    # Electrum normalization: NFKD, lowercase, no accents, single spaces (CJK specifics not handled)
    def normalize_electrum(txt):
        txt = unicodedata.normalize("NFKD", txt).lower()
        txt = "".join(c for c in txt if not unicodedata.combining(c))
        return " ".join(txt.split())
    return hashlib.pbkdf2_hmac(
        "sha512",
        normalize_electrum(mnemonic).encode("utf-8"),
        b"electrum" + normalize_electrum(passphrase).encode("utf-8"),
        2048
    )


def format_asset_balances(asset: Dict[str, Any]) -> (str, str):
    # update balance
    balance_dec = asset.get('balance', None)
    symbol = asset.get('symbol', asset.get('name', ""))
    # logger.debug(f"balance_dec: {balance_dec} {symbol}")
    balance_str = f""
    balance2_str = f""
    if balance_dec is None:
        return balance_str, balance2_str

    # native devise
    precision = COIN_DECIMALS_DICT.get(symbol, 2)
    balance_str = "{:.{}f}".format(balance_dec, precision)
    balance_str = f"{balance_str} {symbol}"

    # in second devise  # default mostly to USD currently, todo: select devise...
    rate_dec = asset.get('exchange_rate', None)
    symbol2 = asset.get('currency', '')
    # logger.debug(f"rate_dec: {rate_dec} {symbol2}")
    if balance_dec == Decimal(0):
        balance2_str = f"0.00 USD"
        # logger.debug(f"balance2_str: {balance2_str}")
    if rate_dec is not None:
        balance2_dec = balance_dec * rate_dec
        precision2 = COIN_DECIMALS_DICT.get(symbol2, 2)
        balance2_str = "{:.{}f}".format(balance2_dec, precision2)
        balance2_str = f"{balance2_str} {symbol2}"
        # logger.debug(f"balance2_str: {balance2_str}")

    return balance_str, balance2_str


def convert_name_to_photo_image(filename, sizex=25, sizey=25):
    icon_path = f"{ICON_PATH}{filename}"
    image = Image.open(icon_path)
    image = image.resize((sizex, sizey), Image.LANCZOS)
    photo_image = customtkinter.CTkImage(image)
    return photo_image