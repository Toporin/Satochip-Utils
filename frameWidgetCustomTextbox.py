import time

import customtkinter
import logging
from PIL import Image, ImageTk

from constants import ICON_PATH, BG_BUTTON

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameWidgetCustomTextbox(customtkinter.CTkFrame):
    def __init__(self, master, label="", content="", width=555, height=37):
        super().__init__(master)
        try:
            logger.debug("FrameWidgetHeader init")

            self.configure(
                width=750, height=40,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            rely = 0.0

            # label
            self.label = customtkinter.CTkLabel(
                self,
                text=label,
                bg_color="whitesmoke",
                fg_color="whitesmoke",
                font=customtkinter.CTkFont(family="Outfit", size=18, weight="normal")
            )
            self.label.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.05

            # textbox
            self.textbox = customtkinter.CTkTextbox(
                self,
                width=width, height=height, corner_radius=10,
                bg_color='white', fg_color=BG_BUTTON, border_color=BG_BUTTON,
                text_color='grey', wrap='word'
            )
            self.textbox.insert("1.0", content)
            self.textbox.place(relx=0.05, rely=rely, anchor="nw")

        except Exception as e:
            logger.error(f"An unexpected error occurred in init: {e}", exc_info=True)

    def update_frame(self, label, content):

        self.label.configure(text=label)
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", content)
