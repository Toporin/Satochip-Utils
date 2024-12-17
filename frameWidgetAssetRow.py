import webbrowser

import customtkinter
import logging
from PIL import Image, ImageTk

from constants import ICON_PATH
from constants import (HIGHLIGHT_COLOR, BG_MAIN_MENU, DEFAULT_BG_COLOR,
                       BG_HOVER_BUTTON, TEXT_COLOR, BUTTON_TEXT_COLOR)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameWidgetAssetRow(customtkinter.CTkFrame):
    def __init__(self, master, width: int, height: int):
        super().__init__(master)

        # logger.debug("init")

        try:
            # Creating new frame
            self.configure(
                width=width, height=height,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )
            self.width = width
            self.height = height
            width_icon= int(0.05*width)
            width_name = int(0.4*width)
            width_balance = int(0.3 * width)
            width_balance2 = int(0.25 * width)

            # clickable image with icon/nft
            # load icon image
            bg_color = "whitesmoke"
            self.icon_path = f"{ICON_PATH}{'about_popup.jpg'}" # todo change...
            self.image = Image.open(self.icon_path)
            self.image = self.image.resize((24, 24), Image.LANCZOS)
            self.photo_image = ImageTk.PhotoImage(self.image)
            # create button
            self.button_icon = customtkinter.CTkButton(
                self, width=width_icon, height=height, text="",
                border_spacing=0,
                image=self.photo_image,
                bg_color=bg_color, fg_color=bg_color,
                hover_color=bg_color,
                anchor="w",
            )
            self.button_icon.image = self.photo_image  # keep a reference of image
            self.button_icon.place(x=0, rely=0, anchor="nw")

            # asset name
            self.button_name = customtkinter.CTkButton(
                self, width=width_name, height=height, border_spacing=0,
                text="", text_color="black",
                font=customtkinter.CTkFont(family="Outfit", size=18, weight="normal"),
                bg_color=bg_color, fg_color=bg_color,
                hover_color=bg_color,
                anchor="w",
            )
            self.button_name.place(x=width_icon, rely=0, anchor="nw")

            # balance
            self.button_balance = customtkinter.CTkButton(
                self, width=width_balance, height=height, border_spacing=0,
                text="", text_color="black",
                font=customtkinter.CTkFont(family="Outfit", size=18, weight="normal"),
                bg_color=bg_color, fg_color=bg_color,
                hover_color=bg_color,
                anchor="w",
            )
            self.button_balance.place(x=(width_icon+width_name), rely=0, anchor="nw")

            # balance2
            self.button_balance2 = customtkinter.CTkButton(
                self, width=width_balance2, height=height, border_spacing=0,
                text="", text_color="black",
                font=customtkinter.CTkFont(family="Outfit", size=18, weight="normal"),
                bg_color=bg_color, fg_color=bg_color,
                hover_color=bg_color,
                anchor="w",
            )
            self.button_balance2.place(x=(width_icon+width_name+width_balance), rely=0, anchor="nw")

        except Exception as e:
            logger.error(f"Init error : {e}", exc_info=True)

    def update_frame(self, row_id: int, name, balance, balance2, url):  # asset: Dict[str:Any],
        logger.debug(f"update_frame for asset name: {name}")

        # populate row with asset
        # fg_color = DEFAULT_BG_COLOR if row_id % 2 == 0 else BG_HOVER_BUTTON
        # text_color = TEXT_COLOR if row_id % 2 == 0 else BUTTON_TEXT_COLOR

        # todo update asset icon
        self.button_name.configure(text=name)
        self.button_balance.configure(text=balance)
        self.button_balance2.configure(text=balance2)
        self.button_name.configure(command=lambda: webbrowser.open(url, new=2))
