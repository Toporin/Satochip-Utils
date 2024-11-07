import customtkinter
import logging
from utils import toggle_entry_visibility, show_qr_code

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
                "Password details",
                "secrets_icon_popup.png",
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
            self.login_label = master.create_label("Login:", frame=self)
            self.login_label.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.05
            self.login_entry = master.create_entry(frame=self)
            self.login_entry.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.08

            # url
            self.url_label = master.create_label("Url:", frame=self)
            self.url_label.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.05
            self.url_entry = master.create_entry(frame=self)
            self.url_entry.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.08

            # password
            self.password_label = master.create_label("Password:", frame=self)
            self.password_label.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.05
            self.password_entry = master.create_entry(show_option="*", frame=self)
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
                command=lambda: None,  # will be updated in update()
                frame=self
            )
            self.qr_button.place(relx=0.75, rely=0.95, anchor="e")
            # show
            self.show_button = master.create_button(
                text="Show",
                command=None,  # will be updated in update
                frame=self
            )
            self.show_button.place(relx=0.95, rely=0.95, anchor="e")

            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"init error: {e}", exc_info=True)

    def update(self, secret):
        # Decode secret
        secret = self.master.controller.decode_password(secret)
        password = secret.get('password')[1:]
        self.label_entry.insert(0, secret.get('label'))
        self.login_entry.insert(0, secret.get('login'))
        self.url_entry.insert(0, secret.get('url'))
        self.password_entry.insert(0, password)

        # qr-code
        self.qr_button.configure(
            command=lambda params=(password, self.qr_label): show_qr_code(params[0], params[1])
        )

        self.show_button.configure(
            command=lambda txt=password: [
                toggle_entry_visibility(self.password_entry),
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