import hashlib

import customtkinter
import logging

from constants import BUTTON_COLOR
from frameWidgetLabel import FrameWidgetLabel

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameWidgetPrivkeyTab(customtkinter.CTkTabview):
    def __init__(self, master, width, height, **kwargs):
        super().__init__(master, width=width, height=height, **kwargs)

        logger.debug("init")

        try:
            # create tabs
            tab_privkey = self.add("Private key")
            tab_wif = self.add("WIF")
            tab_entropy = self.add("Entropy")

            # set token as default
            self.set("Private key")

            # set content frame
            # tab_privkey
            self.privkey_label = FrameWidgetLabel(master=tab_privkey, text="Private key:")
            self.privkey_label.configure(fg_color=BUTTON_COLOR)
            self.privkey_label.place(relx=0.05, rely=0.05, anchor="nw")
            self.privkey_entry = customtkinter.CTkEntry(
                tab_privkey, width=500, height=37, corner_radius=10,
                bg_color=BUTTON_COLOR, fg_color=BUTTON_COLOR, border_color=BUTTON_COLOR,
                show="", text_color='grey'
            )
            #self.privkey_entry = master.create_entry(frame=tab_privkey)
            self.privkey_entry.place(relx=0.05, rely=0.15, anchor="nw")

            # tab_wif
            self.wif_label = FrameWidgetLabel(master=tab_wif, text="WIF:")
            self.wif_label.configure(fg_color=BUTTON_COLOR)
            self.wif_label.place(relx=0.05, rely=0.05, anchor="nw")
            self.wif_entry = customtkinter.CTkEntry(
                tab_wif, width=500, height=37, corner_radius=10,
                bg_color=BUTTON_COLOR, fg_color=BUTTON_COLOR, border_color=BUTTON_COLOR,
                show="", text_color='grey'
            )
            #self.wif_entry = master.create_entry(frame=tab_wif)
            self.wif_entry.place(relx=0.05, rely=0.15, anchor="nw")

            # tab_entropy
            rely = 0.00
            self.entropy_label = FrameWidgetLabel(master=tab_entropy, text="Entropy:")
            self.entropy_label.configure(fg_color=BUTTON_COLOR)
            self.entropy_label.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.1
            self.entropy_entry = customtkinter.CTkEntry(
                tab_entropy, width=500, height=37, corner_radius=10,
                bg_color=BUTTON_COLOR, fg_color=BUTTON_COLOR, border_color=BUTTON_COLOR,
                show="", text_color='grey'
            )
            self.entropy_entry.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.1
            # user entropy
            self.user_entropy_label = FrameWidgetLabel(master=tab_entropy, text="User entropy:")
            self.user_entropy_label.configure(fg_color=BUTTON_COLOR)
            self.user_entropy_label.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.1
            self.user_entropy_entry = customtkinter.CTkEntry(
                tab_entropy, width=500, height=37, corner_radius=10,
                bg_color=BUTTON_COLOR, fg_color=BUTTON_COLOR, border_color=BUTTON_COLOR,
                show="", text_color='grey'
            )
            self.user_entropy_entry.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.1
            # authentikey
            self.authentikey_entropy_label = FrameWidgetLabel(master=tab_entropy, text="Authentikey entropy:")
            self.authentikey_entropy_label.configure(fg_color=BUTTON_COLOR)
            self.authentikey_entropy_label.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.1
            self.authentikey_entropy_entry = customtkinter.CTkEntry(
                tab_entropy, width=500, height=37, corner_radius=10,
                bg_color=BUTTON_COLOR, fg_color=BUTTON_COLOR, border_color=BUTTON_COLOR,
                show="", text_color='grey'
            )
            self.authentikey_entropy_entry.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.1
            # chip entropy
            self.chip_entropy_label = FrameWidgetLabel(master=tab_entropy, text="Card entropy:")
            self.chip_entropy_label.configure(fg_color=BUTTON_COLOR)
            self.chip_entropy_label.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.1
            self.chip_entropy_entry = customtkinter.CTkEntry(
                tab_entropy, width=500, height=37, corner_radius=10,
                bg_color=BUTTON_COLOR, fg_color=BUTTON_COLOR, border_color=BUTTON_COLOR,
                show="", text_color='grey'
            )
            self.chip_entropy_entry.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.1
            # sha256
            self.hash_entropy_label = FrameWidgetLabel(master=tab_entropy, text="Sha256 of entropy (corresponds to the private key):")
            self.hash_entropy_label.configure(fg_color=BUTTON_COLOR)
            self.hash_entropy_label.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.1
            self.hash_entropy_entry = customtkinter.CTkEntry(
                tab_entropy, width=500, height=37, corner_radius=10,
                bg_color=BUTTON_COLOR, fg_color=BUTTON_COLOR, border_color=BUTTON_COLOR,
                show="", text_color='grey'
            )
            self.hash_entropy_entry.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.1

        except Exception as e:
            logger.error(f"Init error : {e}", exc_info=True)

    def update_tab(self, privkey_bytes: bytes, entropy_bytes: bytes, wif:str):

        privkey_hex= "0x" + privkey_bytes.hex()
        self.privkey_entry.delete(0, "end")
        self.privkey_entry.insert(0, privkey_hex)

        self.wif_entry.delete(0, "end")
        self.wif_entry.insert(0, wif)

        # entropy
        entropy_hex = entropy_bytes.hex()
        entropy_user_hex = entropy_hex[0:64]
        entropy_authentikey_hex = entropy_hex[64:128]
        entropy_card_hex = entropy_hex[128:192]
        entropy_hash_hex = hashlib.sha256(entropy_bytes).digest().hex()
        self.entropy_entry.delete(0, "end")
        self.entropy_entry.insert(0, entropy_hex)
        # user
        self.user_entropy_entry.delete(0, "end")
        self.user_entropy_entry.insert(0, entropy_user_hex)
        # authentikey
        self.authentikey_entropy_entry.delete(0, "end")
        self.authentikey_entropy_entry.insert(0, entropy_authentikey_hex)
        # card
        self.chip_entropy_entry.delete(0, "end")
        self.chip_entropy_entry.insert(0, entropy_card_hex)
        # hash
        self.hash_entropy_entry.delete(0, "end")
        self.hash_entropy_entry.insert(0, entropy_hash_hex)


