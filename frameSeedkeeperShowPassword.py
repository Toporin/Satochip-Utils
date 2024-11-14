import customtkinter
import logging

from frameWidgetHeader import FrameWidgetHeader
from utils import toggle_entry_visibility, show_qr_code, reset_qr_code

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
            self.header = FrameWidgetHeader(
                "Password details",
                "secrets_popup.png",
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
            rely += 0.05
            self.login_entry_rely = rely
            self.login_entry = master.create_entry(frame=self)
            self.login_entry.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.08

            # url
            self.url_label_rely = rely
            self.url_label = master.create_label("Url:", frame=self)
            self.url_label.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.05
            self.url_entry_rely = rely
            self.url_entry = master.create_entry(frame=self)
            self.url_entry.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.08

            # password
            self.password_label = master.create_label("Password:", frame=self)
            self.password_label.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.05
            self.password_entry = master.create_entry(frame=self)
            self.password_entry.place(relx=0.05, rely=rely, anchor="nw")

            # qr label
            self.qr_label = master.create_label("", frame=self)
            self.qr_label.place(relx=0.95, rely=rely, anchor="e")
            rely += 0.08

            # Create action buttons
            # delete #todo in red?
            self.delete_button = master.create_button(
                text="Delete secret",
                command=lambda: None,  # will be updated in update
                frame=self
            )
            self.delete_button.place(relx=0.55, rely=0.95, anchor="e")
            # seed_qr button #todo use icons on the side?
            self.qr_button = master.create_button(
                text="QR code",
                command=lambda: None,  # will be updated in update_frame()
                frame=self
            )
            self.qr_button.place(relx=0.75, rely=0.95, anchor="e")
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
        # Decode secret
        secret = self.master.controller.decode_password(secret)
        # update label
        label = secret.get('label', "")
        self.label_entry.delete(0, "end")
        self.label_entry.insert(0, label)
        # update login (opt)
        login = secret.get('login', "")
        if login == "":
            self.login_label.place_forget()
            self.login_entry.place_forget()
        else:
            self.login_label.place(relx=0.05, rely=self.login_label_rely)
            self.login_entry.place(relx=0.05, rely=self.login_entry_rely)
            self.login_entry.delete(0, "end")
            self.login_entry.insert(0, login)
        # update url (opt)
        url = secret.get('url', "")
        if login == "":
            self.url_label.place_forget()
            self.url_entry.place_forget()
        else:
            self.url_label.place(relx=0.05, rely=self.url_label_rely)
            self.url_entry.place(relx=0.05, rely=self.url_entry_rely)
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, url)
        # update password
        password = secret.get('password')
        self.password_entry.delete(0, "end")
        self.password_entry.insert(0, password)

        # qr-code
        reset_qr_code(self.qr_label)
        self.qr_button.configure(
            command=lambda params=(password, self.qr_label): show_qr_code(params[0], params[1])
        )

        self.show_button.configure(
            command=lambda txt=password: [
                self.show_button.configure(
                    text="Show" if self.show_button.cget("text") == "Hide" else "Hide"
                ),
                toggle_entry_visibility(self.password_entry),
            ]
        )

        self.delete_button.configure(
            command=lambda:
                self.master.show(
                    "WARNING",
                    "Are you sure to delete this secret ?!\n Click Yes for delete the secret or close popup",
                    "Yes",
                    lambda sid=secret['id']: self.master.controller.seedkeeper_reset_secret(sid),
                    './pictures_db/secrets_popup.png'
                ),
        )