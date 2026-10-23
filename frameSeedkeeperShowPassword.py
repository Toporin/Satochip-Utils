import customtkinter
import logging

from framePopup import FramePopup
from frameWidgetHeader import FrameWidgetHeader
from utils import toggle_entry_visibility, show_qr_code, create_qr_button, update_entry

logger = logging.getLogger(__name__)


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
            self.header = FrameWidgetHeader(
                "Password details",
                "password_icon.png",
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            # y-offset
            rely = 0.15

            # Create field for label login, url and password
            self.label_label = master.create_label("Label:", frame=self)
            self.label_label.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.05
            self.label_entry = master.create_entry(frame=self)
            self.label_entry.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.08

            # login
            self.login_label_rely= rely
            self.login_label = master.create_label("Login:", frame=self)
            self.login_label.place(relx=0.05, rely=rely, anchor="nw")
            self.login_qr_button = create_qr_button(self, self.login_label)  # command set in update_frame()
            rely += 0.05
            self.login_entry_rely = rely
            self.login_entry = master.create_entry(frame=self)
            self.login_entry.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.08

            # url
            self.url_label_rely = rely
            self.url_label = master.create_label("Url:", frame=self)
            self.url_label.place(relx=0.05, rely=rely, anchor="nw")
            self.url_qr_button = create_qr_button(self, self.url_label)  # command set in update_frame()
            rely += 0.05
            self.url_entry_rely = rely
            self.url_entry = master.create_entry(frame=self)
            self.url_entry.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.08

            # password
            self.password_label = master.create_label("Password:", frame=self)
            self.password_label.place(relx=0.05, rely=rely, anchor="nw")
            self.password_qr_button = create_qr_button(self, self.password_label)  # command set in update_frame()
            rely += 0.05
            self.password_entry = master.create_entry(frame=self)
            self.password_entry.place(relx=0.05, rely=rely, anchor="nw")

            rely += 0.08

            # Create action buttons
            # delete #todo in red?
            self.delete_button = master.create_button(
                text="Delete secret",
                command=lambda: None,  # will be updated in update
                frame=self
            )
            self.delete_button.place(relx=0.75, rely=0.95, anchor="e")
            # show
            self.show_button = master.create_button(
                text="Hide",
                command=None,  # will be updated in update
                frame=self
            )
            self.show_button.place(relx=0.95, rely=0.95, anchor="e")

            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"init error: {e}", exc_info=True)

    def update_frame(self, secret):
        # Decode secret (if export allowed)
        if secret['export_rights'] == 0x02:
            secret['password'] = 'Export failed: export not allowed by SeedKeeper policy.'
        else:
            secret = self.master.controller.decode_password(secret)

        # update label
        label = secret.get('label', "")
        update_entry(self.label_entry, label)
        # update login (opt)
        login = secret.get('login', "")
        if login == "":
            self.login_label.place_forget()
            self.login_entry.place_forget()
        else:
            self.login_label.place(relx=0.05, rely=self.login_label_rely)
            self.login_entry.place(relx=0.05, rely=self.login_entry_rely)
            update_entry(self.login_entry, login)
        # update url (opt)
        url = secret.get('url', "")
        if url == "":
            self.url_label.place_forget()
            self.url_entry.place_forget()
        else:
            self.url_label.place(relx=0.05, rely=self.url_label_rely)
            self.url_entry.place(relx=0.05, rely=self.url_entry_rely)
            update_entry(self.url_entry, url)
        # update password
        password = secret.get('password')
        update_entry(self.password_entry, password)

        # qr-codes (use decoded values, as the widgets may be masked)
        self.login_qr_button.configure(
            command=lambda data=login: show_qr_code(data, self.master, "Login")
        )
        self.url_qr_button.configure(
            command=lambda data=url: show_qr_code(data, self.master, "Url")
        )
        self.password_qr_button.configure(
            command=lambda data=password: show_qr_code(data, self.master, "Password")
        )

        self.show_button.configure(
            command=lambda txt=password: [
                self.show_button.configure(
                    text="Show" if self.show_button.cget("text") == "Hide" else "Hide"
                ),
                toggle_entry_visibility(self.password_entry),
            ]
        )

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
