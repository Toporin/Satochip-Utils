import customtkinter
import logging

from exceptions import ControllerError, SeedkeeperError
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

            self.label = master.create_label("Label*:", frame=self)
            self.label.place(relx=0.05, rely=0.20, anchor="nw")

            # mnemonic
            self.mnemonic_label_name = master.create_entry(frame=self)
            self.mnemonic_label_name.place(relx=0.04, rely=0.25, anchor="nw")

            def update_mnemonic():
                try:
                    mnemonic_length = int(self.radio_value.get())
                    mnemonic = master.controller.generate_random_seed(mnemonic_length)
                    self.mnemonic_textbox.configure(state='normal')
                    self.mnemonic_textbox.delete("1.0", customtkinter.END)
                    self.mnemonic_textbox.insert("1.0", mnemonic)
                    self.mnemonic_textbox.configure(state='disabled')
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
            self.radio_12.place(relx=0.05, rely=0.35, anchor="w")

            self.radio_24 = customtkinter.CTkRadioButton(
                self,
                text="24 words",
                variable=self.radio_value,
                value="24",
                command=lambda: update_mnemonic()
            )
            self.radio_24.place(relx=0.2, rely=0.35, anchor="w")

            self.mnemonic_textbox = master.create_textbox(frame=self)
            self.mnemonic_textbox.place(relx=0.045, rely=0.5, relheight=0.20, anchor="w")

            # use passphrase
            def toggle_passphrase():
                if self.use_passphrase.get():
                    self.passphrase_entry.configure(state="normal")
                else:
                    self.passphrase_entry.configure(state="disabled")

            self.passphrase_checkbox = customtkinter.CTkCheckBox(
                self,
                text="Use passphrase",
                variable=self.use_passphrase,
                command=lambda: toggle_passphrase()
            )
            self.passphrase_checkbox.place(relx=0.05, rely=0.66, anchor="w")

            self.passphrase_entry = master.create_entry(frame=self)
            self.passphrase_entry.place(relx=0.045, rely=0.73, anchor="w")
            self.passphrase_entry.configure(placeholder_text="Enter passphrase (optional)")
            self.passphrase_entry.configure(state='disabled')

            # action buttons
            def import_mnemonic_on_card():
                try:
                    logger.info("Saving mnemonic to card")
                    label = self.mnemonic_label_name.get()
                    mnemonic = self.mnemonic_textbox.get("1.0", "end").strip()
                    passphrase = self.passphrase_entry.get() if self.use_passphrase.get() else None

                    if not mnemonic:
                        raise ValueError("Mnemonic field is mandatory")
                    if not label:
                        raise ValueError("Label field is mandatory")
                    if self.use_passphrase.get() and not passphrase:
                        raise ValueError("Passphrase checked but not provided.")

                    # verify PIN
                    master.update_verify_pin()
                    # import
                    sid, fingerprint = master.controller.import_masterseed(label, mnemonic, passphrase)

                    master.show(
                        "SUCCESS",
                        f"Masterseed saved successfully with id: {sid}",
                        "Ok",
                        master.show_view_my_secrets,
                        "./pictures_db/generate_popup.png"
                    )

                # todo clean exceptions
                except ValueError as e:
                    logger.error(f"Validation error saving mnemonic to card: {str(e)}")
                    master.show("ERROR", str(e), "Ok", None,
                              "./pictures_db/generate_popup.png")
                except ControllerError as e:
                    logger.error(f"Controller error saving mnemonic to card: {str(e)}")
                    master.show("ERROR", f"Failed to save mnemonic: {str(e)}", "Ok", None,
                              "./pictures_db/generate_popup.png")
                except SeedkeeperError as e:
                    logger.error(f"SeedKeeper error saving mnemonic to card: {str(e)}")
                    master.show("ERROR", f"Failed to save mnemonic: {str(e)}", "Ok", None,
                              "./pictures_db/generate_popup.png")
                except Exception as e:
                    logger.error(f"Unexpected error saving mnemonic to card: {str(e)}")
                    master.show("ERROR", "An unexpected error occurred while saving the mnemonic",
                              "Ok", None, "./pictures_db/generate_popup.png")

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
