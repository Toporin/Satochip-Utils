import customtkinter
import logging

from constants import TYPE_MASTERSEED, TYPE_DIC
from framePopup import FramePopup
from frameWidgetHeader import FrameWidgetHeader
from utils import (show_qr_code, create_qr_button, create_copy_button, copy_to_clipboard,
                   set_entry_visibility, set_textbox_visibility,
                   update_textbox, update_entry, make_textbox_readonly,
                   mnemonic_to_entropy_string)

logger = logging.getLogger(__name__)


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
                "seed_popup.png",
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            # y-offset
            rely = 0.15

            # Create field for label
            self.label_label = master.create_label("Label:", frame=self)
            self.label_label.place(relx=0.05, rely=rely, anchor="nw")
            # Create field for master fingerprint, on the same row as label (right-aligned with other fields)
            self.fingerprint_label = master.create_label("Fingerprint:", frame=self)
            self.fingerprint_label.place(relx=0.59, rely=rely, anchor="nw")
            rely += 0.05
            self.label_entry = master.create_entry(width=385, frame=self)
            self.label_entry.place(relx=0.05, rely=rely, anchor="nw")
            self.fingerprint_entry = master.create_entry(width=150, frame=self)
            self.fingerprint_entry.place(relx=0.59, rely=rely, anchor="nw")
            rely += 0.08

            # Create passphrase field
            self.passphrase_label_rely = rely
            self.passphrase_label = master.create_label("Passphrase:", frame=self)
            self.passphrase_label.place(relx=0.05, rely=rely, anchor="nw")
            self.passphrase_qr_button = create_qr_button(self, self.passphrase_label)  # command set in update_frame()
            self.passphrase_copy_button = create_copy_button(self, self.passphrase_qr_button)  # command set in update_frame()
            rely += 0.05
            self.passphrase_entry_rely = rely
            self.passphrase_entry = master.create_entry(frame=self)
            self.passphrase_entry.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.08

            # Create mnemonic field
            self.mnemonic_label = master.create_label("Mnemonic:", frame=self)
            self.mnemonic_label.place(relx=0.05, rely=rely, anchor="nw")
            self.mnemonic_qr_button = create_qr_button(self, self.mnemonic_label)  # command set in update_frame()
            self.mnemonic_copy_button = create_copy_button(self, self.mnemonic_qr_button)  # command set in update_frame()
            rely += 0.05
            self.mnemonic_textbox = master.create_textbox(frame=self)
            self.mnemonic_textbox.place(relx=0.05, rely=rely, relheight=0.15, anchor="nw")
            make_textbox_readonly(self.mnemonic_textbox)  # display-only, selection/copy kept

            rely += 0.16

            # Create descriptor field
            self.descriptor_label_rely = rely
            self.descriptor_label = master.create_label("Descriptor:", frame=self)
            self.descriptor_label.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.05
            self.descriptor_textbox_rely = rely
            self.descriptor_textbox = master.create_textbox(frame=self)
            self.descriptor_textbox.place(relx=0.05, rely=rely, relheight=0.20, anchor="nw")
            make_textbox_readonly(self.descriptor_textbox)  # display-only, selection/copy kept
            # self.descriptor_box = FrameWidgetCustomTextbox(self, label="Secret:", content="MyContent", height=120)
            # self.descriptor_box.place(relx=0.0, rely=rely, anchor="nw")

            # Create action buttons

            # delete
            self.delete_button = master.create_button(
                text="Delete secret",
                command=lambda: None,  # will be updated in update
                frame=self
            )
            self.delete_button.place(relx=0.55, rely=0.95, anchor="e")

            # seed_qr button #todo use icons on the side?
            self.seedqr_button = master.create_button(
                text="SeedQR",
                command=lambda: None,  # will be updated in update_frame()
                frame=self
            )
            self.seedqr_button.place(relx=0.75, rely=0.95, anchor="e")

            # show
            self.secret_visible = False  # secrets are hidden by default (#45)
            self.exportable = True  # updated in update_frame()
            self.show_button = master.create_button(
                text="Show",
                command=lambda: self.set_secret_visibility(not self.secret_visible),
                frame=self
            )
            self.show_button.place(relx=0.95, rely=0.95, anchor="e")

            # place frame
            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"init error: {e}", exc_info=True)

    def set_secret_visibility(self, visible: bool):
        # show secret in plaintext or masked; the button proposes the opposite action
        # an 'export not allowed' message is not a secret: always shown, with show/hide button disabled
        visible = visible or not self.exportable
        self.secret_visible = visible
        set_textbox_visibility(self.mnemonic_textbox, self.mnemonic, visible)
        set_entry_visibility(self.passphrase_entry, visible)
        self.show_button.configure(
            text="Hide" if visible and self.exportable else "Show",
            state="normal" if self.exportable else "disabled"
        )

    def update_frame(self, secret):
        logger.debug(f"update_frame() start")
        # update label
        update_entry(self.label_entry, secret['label'])

        # update header
        if secret.get('type') == TYPE_MASTERSEED:
            if secret.get('subtype') == 0x00:
                self.header.button.configure(text="   Masterseed details")  # should not happen here
            else:
                self.header.button.configure(text="   Bip39 mnemonic details")
        else:
            self.header.button.configure(text=f"   {TYPE_DIC.get(secret.get('type'), 'Mnemonic')} details")

        # Decode secret to mnemonic (if export allowed)
        self.exportable = (secret['export_rights'] != 0x02)
        if secret['export_rights'] == 0x02:
            secret['mnemonic'] = 'Export failed: export not allowed by SeedKeeper policy.'
        else:
            if secret.get('type') == TYPE_MASTERSEED:
                if secret.get('subtype') == 0x00:
                    secret = self.master.controller.decode_masterseed(secret)  # should not happen here
                else:
                    secret = self.master.controller.decode_masterseed_mnemonic(secret)
            else:
                secret = self.master.controller.decode_mnemonic(secret)
        # update passphrase
        passphrase = secret.get('passphrase', "")
        if passphrase == "":
            self.passphrase_label.place_forget()
            self.passphrase_entry.place_forget()
        else:
            self.passphrase_label.place(relx=0.05, rely=self.passphrase_label_rely, anchor="nw")
            self.passphrase_entry.place(relx=0.05, rely=self.passphrase_entry_rely, anchor="nw")
            update_entry(self.passphrase_entry, passphrase)
        # update master fingerprint (empty if export not allowed)
        update_entry(self.fingerprint_entry, secret.get('master_fingerprint', ""))
        # update mnemonic
        mnemonic = secret.get('mnemonic', "")
        self.mnemonic = mnemonic  # used by set_secret_visibility()
        # update descriptor
        descriptor = secret.get('descriptor', "")
        if descriptor == "":
            self.descriptor_label.place_forget()
            self.descriptor_textbox.place_forget()
        else:
            self.descriptor_label.place(relx=0.05, rely=self.descriptor_label_rely)
            self.descriptor_textbox.place(relx=0.05, rely=self.descriptor_textbox_rely, relheight=0.20,)
            update_textbox(self.descriptor_textbox, descriptor)

        # seedqr-code
        self.seedqr_button.configure(
            command=lambda data=mnemonic: show_qr_code(mnemonic_to_entropy_string(data), self.master, "SeedQR")
        )

        # qr-codes & copy to clipboard (use decoded values, as the widgets may be masked)
        self.mnemonic_qr_button.configure(
            command=lambda data=mnemonic: show_qr_code(data, self.master, "Mnemonic")
        )
        self.mnemonic_copy_button.configure(
            command=lambda data=mnemonic: copy_to_clipboard(self, data)
        )
        self.passphrase_qr_button.configure(
            command=lambda data=passphrase: show_qr_code(data, self.master, "Passphrase")
        )
        self.passphrase_copy_button.configure(
            command=lambda data=passphrase: copy_to_clipboard(self, data)
        )

        # mnemonic & passphrase are hidden by default
        self.set_secret_visibility(False)

        # delete button
        self.delete_button.configure(
            command=lambda:
                FramePopup(
                    self.master,
                    "WARNING",
                    "Do you really want to delete this secret? \nThis operation is irreversible!",
                    "Yes",
                    lambda sid=secret['id']: self.master.controller.seedkeeper_reset_secret(sid),
                    './pictures_db/error_popup_red.png',
                    button2_txt="Cancel",
                    cmd2=lambda: None,
                )
        )
