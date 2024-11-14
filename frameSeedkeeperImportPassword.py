import customtkinter
import logging

from frameWidgetHeader import FrameWidgetHeader
from constants import BG_BUTTON

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameSeedkeeperImportPassword(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameSeedkeeperImportPassword init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Creating header
            self.header = FrameWidgetHeader(
                "Import password", "password_popup.jpg",
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

            # login field (opt)
            self.login_label = master.create_label("Login:", frame=self)
            self.login_label.place(relx=0.05, rely=0.32, anchor="nw")

            self.login_entry = master.create_entry(frame=self)
            self.login_entry.configure(width=500)
            self.login_entry.configure(placeholder_text="Enter login (optional)")
            self.login_entry.place(relx=0.15, rely=0.32, anchor="nw")

            # url field (opt)
            self.url_label = master.create_label("Url:", frame=self)
            self.url_label.place(relx=0.05, rely=0.44, anchor="nw")

            self.url_entry = master.create_entry(frame=self)
            self.url_entry.configure(width=500)
            self.url_entry.configure(placeholder_text="Enter url (optional)")
            self.url_entry.place(relx=0.15, rely=0.44, anchor="nw")

            # password generation
            self.password_label = master.create_label("Password:", frame=self)
            self.password_label.place(relx=0.05, rely=0.56, anchor="nw")

            self.password_text_box = customtkinter.CTkTextbox(
                self, corner_radius=20, bg_color="whitesmoke", fg_color=BG_BUTTON,
                border_color=BG_BUTTON, border_width=1, width=500, height=83,
                text_color="grey",
                font=customtkinter.CTkFont(family="Outfit", size=13, weight="normal")
            )
            self.password_text_box.place(relx=0.15, rely=0.68, anchor="w")

            # action buttons
            # password import to card
            def _save_password_to_card():
                try:
                    logger.info("Saving login/password to card")
                    label = self.label_entry.get()
                    login = self.login_entry.get()
                    url = self.url_entry.get()
                    password = self.password_text_box.get("1.0", "end").strip()

                    if not label:
                        logger.warning("No label provided for password encryption.")
                        raise ValueError("The label field is mandatory.")

                    if password:
                        # verify PIN
                        master.update_verify_pin()
                        # import
                        sid, fingerprint = master.controller.import_password(label, password, login, url)
                        master.show("SUCCESS",
                                  f"Password saved successfully\nID: {sid}\nFingerlogger.debug: {fingerprint}",
                                  "Ok", master.show_view_my_secrets, "./pictures_db/generate_popup.png")
                    else:
                        logger.warning("No password to save")
                        raise ValueError("No password generated")
                except Exception as e:
                    logger.error(f"Failed to save password to card: {e}", exc_info=True)
                    master.show(
                        "Error",
                        f"Failed to import secret: {e}",
                        "Ok", None,
                        "./pictures_db/about_popup.jpg"  # todo change icon
                    )

            self.save_button = master.create_button(
                "Import to card",
                command=_save_password_to_card,
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
