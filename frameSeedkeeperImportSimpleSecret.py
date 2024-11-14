import customtkinter
import logging

from frameWidgetHeader import FrameWidgetHeader
from constants import BG_BUTTON

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameSeedkeeperImportSimpleSecret(customtkinter.CTkFrame):
    def __init__(self, master, secret_type: str):
        super().__init__(master)

        logger.debug("FrameSeedkeeperImportSimpleSecret init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Creating header
            self.header = FrameWidgetHeader(
                f"Import {secret_type}", "password_popup.jpg",
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            # label
            self.label = master.create_label("Label*:", frame=self)
            self.label.place(relx=0.05, rely=0.20, anchor="nw")

            self.label_entry = master.create_entry(frame=self)
            self.label_entry.configure(width=500)
            self.label_entry.configure(placeholder_text="Enter label")
            self.label_entry.place(relx=0.15, rely=0.20, anchor="nw")

            # secret textbox
            self.secret_label = master.create_label(f"{secret_type}:", frame=self)
            if secret_type == "descriptor":
                self.secret_label.configure(text="Wallet descriptor*:")
            elif secret_type == "data":
                self.secret_label.configure(text="Data*:")
            self.secret_label.place(relx=0.05, rely=0.30, anchor="nw")

            self.secret_textbox = customtkinter.CTkTextbox(
                self, corner_radius=20, bg_color="whitesmoke", fg_color=BG_BUTTON,
                border_color=BG_BUTTON, border_width=1, width=500, height=200,
                text_color="grey",
                font=customtkinter.CTkFont(family="Outfit", size=13, weight="normal")
            )
            self.secret_textbox.place(relx=0.15, rely=0.36, anchor="nw")

            # action buttons
            # password import to card
            def _save_secret_to_card():
                try:
                    logger.info(f"Saving {secret_type} to card")
                    label = self.label_entry.get()
                    secret = self.secret_textbox.get("1.0", "end").strip()

                    if not label:
                        logger.warning("No label provided for password encryption.")
                        raise ValueError("The label field is mandatory.")

                    if secret:
                        # todo clean exception mgmt
                        # verify PIN
                        master.update_verify_pin()
                        # import
                        sid = 0
                        if secret_type == "descriptor":
                            sid, fingerprint = master.controller.import_wallet_descriptor(label, secret)
                        elif secret_type == "data":
                            sid, fingerprint = master.controller.import_data(label, secret)
                        else:
                            raise ValueError(f"Unsupported secret for import: {secret_type}")

                        master.show(
                            "SUCCESS",
                            f"Secret imported successfully\nID: {sid}",
                            "Ok",
                            master.show_view_my_secrets,
                            "./pictures_db/generate_popup.png"  # todo change icon
                        )
                    else:
                        logger.warning("No secret to save")
                        raise ValueError("No secret generated")
                except Exception as e:
                    logger.error(f"Failed to save {secret_type} to card: {e}", exc_info=True)
                    master.show(
                        "Error",
                        f"Failed to import secret: {e}",
                        "Ok", None,
                        "./pictures_db/about_popup.jpg"  # todo change icon
                    )

            self.save_button = master.create_button(
                "Import to card",
                command=_save_secret_to_card,
                frame=self
            )
            self.save_button.place(relx=0.85, rely=0.95, anchor="center")

            # back button
            self.back_button = master.create_button(
                "Back",
                command=master.show_import_secret,
                frame=self
            )
            self.back_button.place(relx=0.65, rely=0.95, anchor="center")

            # place frame
            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"Init error : {e}", exc_info=True)
