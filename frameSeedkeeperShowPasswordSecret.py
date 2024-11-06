import binascii
import time

import customtkinter
import logging

from constants import (DEFAULT_BG_COLOR, BG_MAIN_MENU, BG_HOVER_BUTTON,
                       TEXT_COLOR, BUTTON_TEXT_COLOR, HIGHLIGHT_COLOR)
from exceptions import ControllerError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameSeedkeeperShowPasswordSecret(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameSeedkeeperShowSecret init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Creating header
            self.header = master.create_an_header(
                "Secret details",
                "secrets_icon_popup.png",
                frame=self
            )

            # Create field for label login, url and password
            self.label_label = master.create_label("Label:", frame=self)
            self.label_label.place(relx=0.045, rely=0.2)
            self.label_entry = master.create_entry(frame=self)
            #self.label_entry.insert(0, secret_details['label'])
            self.label_entry.place(relx=0.045, rely=0.27)

            # login
            self.login_label = master.create_label("Login:", frame=self)
            self.login_label.place(relx=0.045, rely=0.34)
            self.login_entry = master.create_entry(frame=self)
            self.login_entry.place(relx=0.045, rely=0.41)

            # url
            self.url_label = master.create_label("Url:", frame=self)
            self.url_label.place(relx=0.045, rely=0.48)
            self.url_entry = master.create_entry(frame=self)
            self.url_entry.place(relx=0.045, rely=0.55)

            # password
            self.password_label = master.create_label("Password:", frame=self)
            self.password_label.place(relx=0.045, rely=0.7, anchor="w")
            self.password_entry = master.create_entry(show_option="*", frame=self)
            self.password_entry.configure(width=500)
            self.password_entry.place(relx=0.04, rely=0.77, anchor="w")

            def _toggle_password_visibility(password_entry):
                # todo: only hides secret, not login/url/... fields
                try:
                    # login
                    # login_current_state = login_entry.cget("show")
                    # login_new_state = "" if login_current_state == "*" else "*"
                    # login_entry.configure(show=login_new_state)
                    # # url
                    # url_current_state = url_entry.cget("show")
                    # url_new_state = "" if url_current_state == "*" else "*"
                    # url_entry.configure(show=url_new_state)
                    # password
                    password_current_state = password_entry.cget("show")
                    password_new_state = "" if password_current_state == "*" else "*"
                    password_entry.configure(show=password_new_state)
                except Exception as e:
                    logger.error(f"018 Error toggling password visibility: {e}", exc_info=True)

            # Create action buttons
            self.show_button = master.create_button(
                text="Show",
                command=lambda: _toggle_password_visibility(self.password_entry),
                frame=self
            )
            self.show_button.place(relx=0.9, rely=0.8, anchor="se")

            self.delete_button = master.create_button(
                text="Delete secret",
                command=lambda: None,
                # [
                #     master.show(
                #         "WARNING",
                #         "Are you sure to delete this secret ?!\n Click Yes for delete the secret or close popup",
                #         "Yes",
                #         lambda: [master.controller.cc.seedkeeper_reset_secret(secret_details['id']),
                #                  master.show_view_my_secrets()],
                #         './pictures_db/secrets_icon_popup.png'),
                #     master.show_view_my_secrets()
                # ],
                frame=self
            )
            self.delete_button.place(relx=0.75, rely=0.98, anchor="se")

            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"init error: {e}", exc_info=True)

    def update(self, secret):

        # Decode secret
        try:
            logger.debug("006 Decoding secret to show")
            self.decoded_login_password = self.master.controller.decode_password(
                secret,
                binascii.unhexlify(secret['secret'])
            )
        except ValueError as e:
            self.master.show("ERROR", f"Invalid secret format: {str(e)}", "Ok")
        except ControllerError as e:
            self.master.show("ERROR", f"Failed to decode secret: {str(e)}", "Ok")

        # update secret field
        logger.debug(f"006 Decoded secret to show: {self.decoded_login_password}")
        self.label_entry.insert(0, self.decoded_login_password['label'])
        self.login_entry.insert(0, self.decoded_login_password['login'])
        self.url_entry.insert(0, self.decoded_login_password['url'])
        self.password_entry.insert(0, self.decoded_login_password['password'][1:])

        # update delete_button command
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