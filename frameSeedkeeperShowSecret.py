import customtkinter
import logging

from utils import show_qr_code, toggle_entry_visibility, toggle_textbox_visibility

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameSeedkeeperShowSecret(customtkinter.CTkFrame):
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
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            # y-offset
            rely= 0.15

            # Create field for label
            self.label_label = master.create_label("Label:", frame=self)
            self.label_label.place(relx=0.05, rely=rely, anchor="nw")
            rely+=0.05
            self.label_entry = master.create_entry(frame=self)
            self.label_entry.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.1

            # Create secret field
            self.secret_label = master.create_label("Secret:", frame=self)
            self.secret_label.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.05
            self.secret_textbox = master.create_textbox(frame=self)
            self.secret_textbox.place(relx=0.05, rely=rely, relheight=0.23, anchor="nw")

            # seed_qr label
            self.qr_label = master.create_label("", frame=self)
            self.qr_label.place(relx=0.8, rely=rely)
            rely+=0.1

            # Create action buttons

            # delete #todo in red?
            self.delete_button = master.create_button(
                text="Delete secret",
                command=lambda: None, # will be updated in update
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
                command= None, # will be updated in update
                frame=self
            )
            self.show_button.place(relx=0.95, rely=0.95, anchor="e")

            # place frame
            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"FrameSeedkeeperShowSecret init error: {e}", exc_info=True)


    def update(self, secret):
        logger.debug(f"update() secret: {secret}")
        self.label_entry.insert(0, secret['label'])

        # update header #todo!
        #self.header.configure(text=f"{secret.get('type')} details")

        # Decode secret
        secret = self.master.controller.decode_secret(secret)
        secret_decoded = secret['secret_decoded']
        self.secret_textbox.insert("1.0", '*' * len(secret_decoded)) # Masque la valeur

        # qr-code
        self.qr_button.configure(
            command=lambda params=(secret_decoded, self.qr_label): show_qr_code(params[0], params[1])
        )

        self.show_button.configure(
            command=lambda txt=secret_decoded: [
                toggle_textbox_visibility(self.secret_textbox, txt),
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
