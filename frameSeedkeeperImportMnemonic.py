import customtkinter
import logging

from exceptions import ControllerError, SeedkeeperError
from frameWidgetHeader import FrameWidgetHeader

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameSeedkeeperImportMnemonic(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameSeedkeeperImportMnemonic init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Creating header
            self.header = FrameWidgetHeader(
                "Import Bip39 mnemonic", "seed_popup.jpg",
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

            self.mnemonic_textbox = master.create_textbox(frame=self)
            self.mnemonic_textbox.place(relx=0.05, rely=0.33, relheight=0.15, anchor="nw")

            # use passphrase
            def toggle_passphrase():
                if self.use_passphrase.get():
                    self.passphrase_entry.place(relx=0.05, rely=0.58, anchor="nw")
                else:
                    self.passphrase_entry.place_forget()

            self.use_passphrase = customtkinter.BooleanVar(value=False)
            self.passphrase_checkbox = customtkinter.CTkCheckBox(
                self,
                text="Use passphrase",
                variable=self.use_passphrase,
                command=lambda: toggle_passphrase()
            )
            self.passphrase_checkbox.place(relx=0.05, rely=0.52, anchor="nw")

            self.passphrase_entry = master.create_entry(frame=self)
            self.passphrase_entry.configure(placeholder_text="Enter passphrase (optional)")

            # use descriptor
            def toggle_descriptor():
                if self.use_descriptor.get():
                    self.descriptor_textbox.place(relx=0.05, rely=0.74, relheight=0.15, anchor="nw")
                else:
                    self.descriptor_textbox.place_forget()

            self.use_descriptor = customtkinter.BooleanVar(value=False)
            self.descriptor_checkbox = customtkinter.CTkCheckBox(
                self,
                text="Use descriptor",
                variable=self.use_descriptor,
                command=lambda: toggle_descriptor()
            )
            self.descriptor_checkbox.place(relx=0.05, rely=0.67, anchor="nw")

            self.descriptor_textbox = master.create_textbox(frame=self)


            # action buttons
            def import_mnemonic_on_card():
                try:
                    logger.info("Saving mnemonic to card")
                    label = self.label_entry.get()
                    mnemonic = self.mnemonic_textbox.get("1.0", "end").strip()
                    passphrase = self.passphrase_entry.get() if self.use_passphrase.get() else None
                    descriptor = self.descriptor_textbox.get("1.0", "end") if self.use_descriptor.get() else None

                    if not mnemonic:
                        logger.warning("No mnemonic to save")
                        raise ValueError("Mnemonic field is mandatory")
                    if not label:
                        logger.warning("No label provide")
                        raise ValueError("Label field is mandatory")
                    if self.use_passphrase.get() and not passphrase:
                        logger.warning("Passphrase checkbox is checked but no passphrase provided")
                        raise ValueError("Passphrase checked but not provided.")

                    # todo: validate mnemonic format!!
                    # verify PIN
                    master.update_verify_pin()
                    # import
                    sid, fingerprint = master.controller.import_masterseed(label, mnemonic, passphrase, descriptor)

                    master.show(
                        "SUCCESS",
                        f"Masterseed saved successfully with id: {sid}",
                        "Ok",
                        master.show_seedkeeper_list_secrets,
                        "./pictures_db/generate_popup.png"
                    )

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
