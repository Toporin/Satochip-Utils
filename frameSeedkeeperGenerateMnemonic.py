import customtkinter
import logging

from frameWidgetHeader import FrameWidgetHeader

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameSeedkeeperGenerateMnemonic(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameSeedkeeperGenerateMnemonic init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Creating header
            self.header = FrameWidgetHeader(
                "Generate Bip39 mnemonic", "generate_popup.png",
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            # label
            self.label = master.create_label("Label*:", frame=self)
            self.label.place(relx=0.05, rely=0.15, anchor="nw")

            self.label_entry = master.create_entry(frame=self)
            self.label_entry.configure(placeholder_text="Enter label")
            self.label_entry.place(relx=0.05, rely=0.20, anchor="nw")

            # mnemonic
            self.mnemonic_label = master.create_label("Mnemonic*:", frame=self)
            self.mnemonic_label.place(relx=0.05, rely=0.28, anchor="nw")

            def update_mnemonic():
                try:
                    mnemonic_length = int(self.radio_value.get())
                    mnemonic = master.controller.generate_random_seed(mnemonic_length)
                    #self.mnemonic_textbox.configure(state='normal')
                    self.mnemonic_textbox.delete("1.0", customtkinter.END)
                    self.mnemonic_textbox.insert("1.0", mnemonic)
                    #self.mnemonic_textbox.configure(state='disabled') # also disable copy-paste on some linux distro
                except Exception as e:
                    logger.error(f"Error generating mnemonic: {e}", exc_info=True)

            self.radio_value = customtkinter.StringVar(value="12")
            self.use_passphrase = customtkinter.BooleanVar(value=False)

            self.radio_12 = customtkinter.CTkRadioButton(
                self,
                text="12 words",
                variable=self.radio_value,
                value="12",
                command=lambda: update_mnemonic()
            )
            self.radio_12.place(relx=0.05, rely=0.34, anchor="nw")

            self.radio_24 = customtkinter.CTkRadioButton(
                self,
                text="24 words",
                variable=self.radio_value,
                value="24",
                command=lambda: update_mnemonic()
            )
            self.radio_24.place(relx=0.2, rely=0.34, anchor="nw")

            self.mnemonic_textbox = master.create_textbox(frame=self)
            self.mnemonic_textbox.place(relx=0.05, rely=0.40, relheight=0.1, anchor="nw")

            # use passphrase
            def toggle_passphrase():
                if self.use_passphrase.get():
                    self.passphrase_entry.place(relx=0.05, rely=0.60, anchor="nw")
                else:
                    self.passphrase_entry.place_forget()

            self.passphrase_checkbox = customtkinter.CTkCheckBox(
                self,
                text="Use passphrase",
                variable=self.use_passphrase,
                command=lambda: toggle_passphrase()
            )
            self.passphrase_checkbox.place(relx=0.05, rely=0.55, anchor="w")

            self.passphrase_entry = master.create_entry(frame=self)
            self.passphrase_entry.configure(placeholder_text="Enter passphrase (optional)")

            # use descriptor
            def toggle_descriptor():
                if self.use_descriptor.get():
                    self.descriptor_textbox.place(relx=0.05, rely=0.75, relheight=0.15, anchor="nw")
                else:
                    self.descriptor_textbox.place_forget()

            self.use_descriptor = customtkinter.BooleanVar(value=False)
            self.descriptor_checkbox = customtkinter.CTkCheckBox(
                self,
                text="Use descriptor",
                variable=self.use_descriptor,
                command=lambda: toggle_descriptor()
            )
            self.descriptor_checkbox.place(relx=0.05, rely=0.68, anchor="nw")
            self.descriptor_textbox = master.create_textbox(frame=self)

            # action buttons

            def import_mnemonic_on_card():
                try:
                    logger.info("Saving mnemonic to card")
                    label = self.label_entry.get()
                    mnemonic = self.mnemonic_textbox.get("1.0", "end").strip()
                    passphrase = self.passphrase_entry.get() if self.use_passphrase.get() else None
                    descriptor = self.descriptor_textbox.get("1.0", "end") if self.use_descriptor.get() else None

                    # import
                    sid, fingerprint = master.controller.import_masterseed_mnemonic(label, mnemonic, passphrase, descriptor)
                    master.show(
                        "SUCCESS",
                        f"Mnemonic saved successfully with id: {sid}",
                        "Ok",
                        master.show_seedkeeper_list_secrets,
                        "./pictures_db/generate_popup.png"
                    )

                except Exception as ex:
                    logger.error(f"Failed to import mnemonic to card: {ex}", exc_info=True)
                    master.show(
                        "Error",
                        f"Failed to import mnemonic: \n{ex}",
                        "Ok", None,
                        "./pictures_db/about_popup.jpg"  # todo change icon
                    )

            self.save_button = master.create_button(
                "Save on card",
                command=lambda: import_mnemonic_on_card(),
                frame=self
            )
            self.save_button.place(relx=0.85, rely=0.95, anchor="center")

            self.back_button = master.create_button(
                "Back",
                command=lambda: master.show_generate_secret(),
                frame=self
            )
            self.back_button.place(relx=0.65, rely=0.95, anchor="center")

            # place frame
            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"Init error : {e}", exc_info=True)
