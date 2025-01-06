import webbrowser

import customtkinter
import logging
from PIL import Image, ImageTk

from constants import ICON_PATH, BG_BUTTON, MAIN_MENU_COLOR, HOVER_COLOR
from constants import (HIGHLIGHT_COLOR, BG_MAIN_MENU, DEFAULT_BG_COLOR,
                       BG_HOVER_BUTTON, TEXT_COLOR, BUTTON_TEXT_COLOR)
from controller import Controller
from frameWidgetLabel import FrameWidgetLabel
from utils import convert_name_to_photo_image

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameWidgetOwnership(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("init")

        # Creating new frame
        bg_color = "whitesmoke"
        self.configure(
            width=750, height=35,
            bg_color=bg_color, fg_color=bg_color
        )

        # ownership status
        self.ownership_status = FrameWidgetLabel(master=self, text="Ownership status")
        self.ownership_status.pack(pady=5, side='left', fill="both")

        # ownership info tip
        self.photo_image = convert_name_to_photo_image("info_icon.png")
        self.ownership_info_url = "https://satochip.io/satodime-ownership-explained/"
        self.ownership_info_button = customtkinter.CTkButton(
            self, width=28, height=28, text="",
            border_spacing=0,
            image=self.photo_image,
            bg_color=bg_color, fg_color=bg_color,
            hover_color=bg_color,
            command=lambda: webbrowser.open(self.ownership_info_url, new=2)
        )
        self.ownership_info_button.pack(pady=5, side='left', fill="both")

        # ownership action button
        self.ownership_button = customtkinter.CTkButton(
            self,
            width=28, height=35, corner_radius=100,
            text="",
            font=customtkinter.CTkFont(family="Outfit", size=18, weight="normal"),
            border_spacing=0,
            bg_color=bg_color, fg_color=MAIN_MENU_COLOR,
            hover_color=HOVER_COLOR, cursor="hand2",
            command=lambda: None  # updated later
        )
        #master.create_button("", lambda: None, frame=self)  # updated later
        #self.ownership_button.configure(font=customtkinter.CTkFont(size=15))
        self.ownership_button.pack(pady=5, side='left', fill="both")  # pack(side='left', expand=True, fill="both")

    def update_frame(self, ownership_value: str, controller: Controller):
        logger.debug(f"update_frame")

        self.ownership_status.configure(text=ownership_value)

        # update transfert button
        def satodime_transfer_card():
            is_success = controller.satodime_transfer_card()
            if is_success:  # update status
                self.ownership_status.configure(text="Card has no owner")
                self.ownership_button.configure(
                    text="Take ownership",
                    command=lambda: satodime_take_card_ownership(),
                )

        def satodime_take_card_ownership():
            is_success = controller.satodime_take_card_ownership()
            if is_success:  # update status
                self.ownership_status.configure(text="You are the owner")
                self.ownership_button.configure(
                    text="Transfer ownership",
                    command=lambda: satodime_transfer_card(),
                )

        if controller.cc.setup_done:
            self.ownership_button.configure(
                text="Transfer ownership",
                command=lambda: satodime_transfer_card(),
            )
        else:
            self.ownership_button.configure(
                text="Take ownership",
                command=lambda: satodime_take_card_ownership(),
            )


