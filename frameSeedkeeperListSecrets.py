import time

import customtkinter
import logging

from constants import (DEFAULT_BG_COLOR, BG_MAIN_MENU, BG_HOVER_BUTTON,
                       TEXT_COLOR, BUTTON_TEXT_COLOR, HIGHLIGHT_COLOR)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameSeedkeeperListSecrets(customtkinter.CTkFrame):
    """
         This class manages to:
             - Show a list of all secrets stored on the card.
             - Select and display details about each secret from the list.
             - Include specific widgets and buttons according to the secret type/subtype.
             - This method is built using a structural encapsulation approach, meaning that each function within it contains everything necessary for its operation, ensuring modularity and self-sufficiency.
    """
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameSeedkeeperListSecrets init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Creating header
            self.header = master.create_an_header(
                "My secrets",
                "generate_popup.png",
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            # Creating secrets table

            # Introduce table
            self.label_text = master.create_label(text="Click on a secret to manage it:", frame=self)
            self.label_text.place(relx=0.05, rely=0.15, anchor="nw")

            # Define headers
            self.headers = ["Id", "Type of secret", "Label"]
            rely = 0.3
            absx = 33.5

            # Create header labels
            # self.header_frame = customtkinter.CTkFrame(
            #     self, width=600, bg_color=DEFAULT_BG_COLOR,
            #     corner_radius=0, fg_color=DEFAULT_BG_COLOR)
            # self.header_frame.place(relx=0.05, rely=rely, relwidth=0.9, anchor="w")

            self.header_widths = [50, 200, 350]  # Define specific widths for each header
            for col, width in zip(self.headers, self.header_widths):
                self.header_button = customtkinter.CTkButton(
                    self, text=col,
                    font=customtkinter.CTkFont(size=14, family='Outfit', weight="bold"),
                    corner_radius=0, state='disabled', text_color='white',
                    fg_color=BG_MAIN_MENU, width=width
                )
                #self.header_button.pack(side="left", expand=True, fill="both")
                #self.header_button.place(relx=0.05, rely=rely, anchor="w")
                self.header_button.place(x=absx, rely=0.23, anchor="nw")
                absx=absx+width+2

            self.table_frame = master._create_scrollable_frame(
                self, width=600, height=400, x=33.5, y=175
            )

            self.secret_rows = []

            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            error_msg = f"FrameSeedkeeperListSecrets init: Failed to create secrets frame: {e}"
            logger.error(error_msg, exc_info=True)

    def update(self, secret_headers):
        # todo: add flag to skip update

        # def _on_mouse_on_secret(event, buttons):
        #     for button in buttons:
        #         button.configure(fg_color=HIGHLIGHT_COLOR, cursor="hand2")
        #
        # def _on_mouse_out_secret(event, buttons):
        #     for button in buttons:
        #         button.configure(fg_color=button.default_color)

        # clear rows
        if len(self.secret_rows)>0:
            for i, row in enumerate(self.secret_rows):
                self.secret_rows[i].destroy()
            self.secret_rows=[]

        # Create rows of labels with alternating colors
        #rely = 0.3
        for i, secret in enumerate(secret_headers):
            try:
                #rely += 0.06
                row_frame = customtkinter.CTkFrame(
                    self.table_frame, width=750,
                    bg_color=DEFAULT_BG_COLOR,
                    fg_color=DEFAULT_BG_COLOR
                )
                row_frame.pack(pady=2, fill="x")

                fg_color = DEFAULT_BG_COLOR if i % 2 == 0 else BG_HOVER_BUTTON
                text_color = TEXT_COLOR if i % 2 == 0 else BUTTON_TEXT_COLOR

                #buttons = []
                secret_type = None
                if secret['type'] == "Masterseed" and secret['subtype'] == '0x1':
                    secret_type = "Mnemonic seedphrase"
                values = [secret['id'], secret['type'] if not secret_type else secret_type, secret['label']]
                for value, width in zip(values, self.header_widths):
                    cell_button = customtkinter.CTkButton(
                        row_frame, text=value,
                        text_color=text_color, fg_color=fg_color,
                        font=customtkinter.CTkFont(size=14, family='Outfit'),
                        hover_color=HIGHLIGHT_COLOR, corner_radius=0, width=width
                    )
                    cell_button.default_color = fg_color  # Store the default color
                    cell_button.pack(side='left', expand=True, fill="both")
                    #cell_button.bind("<Enter>", lambda event, btns=buttons: _on_mouse_on_secret(event, btns))
                    #cell_button.bind("<Leave>", lambda event, btns=buttons: _on_mouse_out_secret(event, btns))
                    cell_button.configure(command=lambda s=secret: self.master.show_view_secret(s))
                    #buttons.append(cell_button)

                # add row to list (keep ref to destroy them on card removal)
                self.secret_rows += [row_frame]

                logger.debug(f"016 Row created for secret ID: {secret['id']}")
            except Exception as e:
                logger.error(f"017 Error creating row for secret {secret['id']}: {str(e)}")

        # update status flag
        # todo detect changes in secret_headers to update list when needed
        self.master.seedkeeper_secret_headers_need_update = False

