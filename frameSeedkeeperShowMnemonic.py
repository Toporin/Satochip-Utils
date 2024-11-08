import binascii
import time
import tkinter

import pyqrcode
import customtkinter
import logging

from exceptions import ControllerError
from frameWidgetCustomTextbox import FrameWidgetCustomTextbox
from frameWidgetHeader import FrameWidgetHeader
from utils import show_qr_code, toggle_entry_visibility, toggle_textbox_visibility, reset_qr_code, update_textbox

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameSeedkeeperShowMnemonic(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameSeedkeeperShowMnemonic init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Creating header
            self.header = FrameWidgetHeader(
                "Mnemonic details",
                "secrets_icon_popup.png",
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            # y-offset
            rely= 0.15

            # Create field for label
            self.label_label = master.create_label("Label:", frame=self)
            self.label_label.place(relx=0.05, rely=rely, anchor="nw")
            rely+=0.05
            self.label_entry = master.create_entry(frame=self)
            self.label_entry.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.08

            # Create passphrase field
            self.passphrase_label_rely = rely
            self.passphrase_label = master.create_label("Passphrase:", frame=self)
            self.passphrase_label.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.05
            self.passphrase_entry_rely = rely
            self.passphrase_entry = master.create_entry(frame=self)
            self.passphrase_entry.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.08

            # Create mnemonic field
            self.mnemonic_label = master.create_label("Mnemonic:", frame=self)
            self.mnemonic_label.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.05
            self.mnemonic_textbox = master.create_textbox(frame=self)
            self.mnemonic_textbox.place(relx=0.05, rely=rely, relheight=0.15, anchor="nw")

            # qr label
            self.qr_label = master.create_label("", frame=self)
            self.qr_label.place(relx=0.8, rely=rely)
            rely+=0.16

            # Create descriptor field
            self.descriptor_label_rely = rely
            self.descriptor_label = master.create_label("Descriptor:", frame=self)
            self.descriptor_label.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.05
            self.descriptor_textbox_rely = rely
            self.descriptor_textbox = master.create_textbox(frame=self)
            self.descriptor_textbox.place(relx=0.05, rely=rely, relheight=0.20, anchor="nw")
            #self.descriptor_box = FrameWidgetCustomTextbox(self, label="Secret:", content="MyContent", height=120)
            #self.descriptor_box.place(relx=0.0, rely=rely, anchor="nw")

            # Create action buttons

            # delete #todo in red?
            self.delete_button = master.create_button(
                text="Delete secret",
                command=lambda: None, # will be updated in update
                frame=self
            )
            self.delete_button.place(relx=0.55, rely=0.95, anchor="e")
            # seed_qr button #todo use icons on the side?
            self.qr_button = master.create_button(
                text="SeedQR",
                command=lambda: None,  # will be updated in update()
                frame=self
            )
            self.qr_button.place(relx=0.75, rely=0.95, anchor="e")
            # show
            self.show_button = master.create_button(
                text="Hide", # secret is shown by default
                command= None, # will be updated in update
                frame=self
            )
            self.show_button.place(relx=0.95, rely=0.95, anchor="e")

            # place frame
            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"init error: {e}", exc_info=True)

    def update_frame(self, secret):
        logger.debug(f"update() secret: {secret}")
        self.label_entry.delete(0, "end")
        self.label_entry.insert(0, secret['label'])

        # update header
        if secret.get('type') == "Masterseed":
            if secret.get('subtype') == 0x00:
                self.header.button.configure(text="   Masterseed details") # should not happen here
            else:
                self.header.button.configure(text="   Bip39 mnemonic details")
        else:
            self.header.button.configure(text=f"   {secret.get('type')} details")

        # Decode seed to mnemonic
        if secret.get('type') == "Masterseed":
            if secret.get('subtype') == 0x00:
                secret = self.master.controller.decode_masterseed(secret)  # should not happen here
            else:
                secret = self.master.controller.decode_masterseed_mnemonic(secret)
        else:
            secret = self.master.controller.decode_mnemonic(secret)
        # update passphrase
        passphrase = secret.get('passphrase', "")
        if passphrase=="":
            self.passphrase_label.place_forget()
            self.passphrase_entry.place_forget()
        else:
            self.passphrase_label.place(relx=0.05, rely=self.passphrase_label_rely, anchor="nw")
            self.passphrase_entry.place(relx=0.05, rely=self.passphrase_entry_rely, anchor="nw")
            self.passphrase_entry.delete(0, "end")
            self.passphrase_entry.insert(0, passphrase)
        # update mnemonic
        mnemonic = secret.get('mnemonic',"")
        update_textbox(self.mnemonic_textbox, mnemonic)
        # update descriptor
        descriptor = secret.get('descriptor',"")
        if descriptor=="":
            self.descriptor_label.place_forget()
            self.descriptor_textbox.place_forget()
        else:
            self.descriptor_label.place(relx=0.05, rely=self.descriptor_label_rely)
            self.descriptor_textbox.place(relx=0.05, rely=self.descriptor_textbox_rely, relheight=0.20,)
            update_textbox(self.descriptor_textbox, descriptor)

        # qr-code
        reset_qr_code(self.qr_label)
        self.qr_button.configure(
            command=lambda params=(mnemonic, self.qr_label): show_qr_code(params[0], params[1])
        )

        self.show_button.configure(
            command=lambda txt=mnemonic: [
                self.show_button.configure(
                    text="Show" if self.show_button.cget("text") == "Hide" else "Hide"
                ),
                toggle_textbox_visibility(self.mnemonic_textbox, txt),
                toggle_entry_visibility(self.passphrase_entry)
            ]
        )

        self.delete_button.configure(
            command=lambda: [
                self.master.show(
                    "WARNING",
                    "Are you sure to delete this secret ?!\n Click Yes for delete the secret or close popup",
                    "Yes",
                    lambda id=secret['id']: [
                        logger.debug(f"FrameSeedkeeperShowSecret update delete secret with id: {id}"),
                        self.master.controller.cc.seedkeeper_reset_secret(id),
                    ],
                    './pictures_db/secrets_icon_popup.png'),
                self.master.show_view_my_secrets()
            ],
        )