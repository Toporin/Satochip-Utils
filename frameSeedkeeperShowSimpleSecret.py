import customtkinter
import logging

from constants import TYPE_DIC
from framePopup import FramePopup
from frameWidgetHeader import FrameWidgetHeader
from utils import show_qr_code, create_qr_button, create_copy_button, copy_to_clipboard, \
    toggle_entry_visibility, toggle_textbox_visibility, update_textbox, update_entry, make_textbox_readonly

logger = logging.getLogger(__name__)


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
            self.header = FrameWidgetHeader(
                "Secret details",
                "password_icon.png",
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
            self.secret_qr_button = create_qr_button(self, self.secret_label)  # command set in update_frame()
            self.secret_copy_button = create_copy_button(self, self.secret_qr_button)  # command set in update_frame()
            rely += 0.05
            self.secret_textbox = master.create_textbox(frame=self)
            self.secret_textbox.place(relx=0.05, rely=rely, relheight=0.23, anchor="nw")
            make_textbox_readonly(self.secret_textbox)  # display-only, selection/copy kept

            rely+=0.1

            # Create action buttons

            # delete #todo in red?
            self.delete_button = master.create_button(
                text="Delete secret",
                command=lambda: None, # will be updated in update
                frame=self
            )
            self.delete_button.place(relx=0.75, rely=0.95, anchor="e")
            # show
            self.show_button = master.create_button(
                text="Hide",
                command= None, # will be updated in update
                frame=self
            )
            self.show_button.place(relx=0.95, rely=0.95, anchor="e")

            # place frame
            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"FrameSeedkeeperShowSecret init error: {e}", exc_info=True)

    def update_frame(self, secret):
        logger.debug(f"update_frame() secret id: {secret.get('id')} type: {secret.get('type')}")
        update_entry(self.label_entry, secret['label'])

        # update header
        self.header.button.configure(text=f"   {TYPE_DIC.get(secret.get('type'), 'Unknown secret')} details")

        # Decode secret and update textbox (if export allowed)
        if secret['export_rights'] == 0x02:
            secret_decoded = 'Export failed: export not allowed by SeedKeeper policy.'
        else:
            secret = self.master.controller.decode_secret(secret)
            secret_decoded = secret['secret_decoded']
        update_textbox(self.secret_textbox, secret_decoded)

        # qr-code & copy to clipboard (use decoded value, as the widget may be masked)
        self.secret_qr_button.configure(
            command=lambda data=secret_decoded: show_qr_code(data, self.master, "Secret")
        )
        self.secret_copy_button.configure(
            command=lambda data=secret_decoded: copy_to_clipboard(self, data)
        )

        self.show_button.configure(
            command=lambda txt=secret_decoded: [
                self.show_button.configure(
                    text="Show" if self.show_button.cget("text") == "Hide" else "Hide"
                ),
                toggle_textbox_visibility(self.secret_textbox, txt),
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