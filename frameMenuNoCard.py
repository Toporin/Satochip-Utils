import webbrowser

import customtkinter
import logging
from PIL import Image, ImageTk

from constants import MAIN_MENU_COLOR, ICON_PATH

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameMenuNoCard(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameMenuNoCard init")
        try:
            self.configure(
                width=250, height=600,
                bg_color=MAIN_MENU_COLOR, fg_color=MAIN_MENU_COLOR,
                corner_radius=0, border_color="black", border_width=0
            )

            # Logo section
            image_frame = customtkinter.CTkFrame(
                self, bg_color=MAIN_MENU_COLOR, fg_color=MAIN_MENU_COLOR,
                width=284, height=126
            )
            image_frame.place(rely=0, relx=0.5, anchor="n")
            logo_image = Image.open("./pictures_db/logo.png")
            logo_photo = ImageTk.PhotoImage(logo_image)
            self.canvas = customtkinter.CTkCanvas(
                image_frame, width=284, height=127, bg=MAIN_MENU_COLOR,
                highlightthickness=0
            )
            self.canvas.pack(fill="both", expand=True)
            self.canvas.create_image(142, 63, image=logo_photo, anchor="center")
            self.canvas.image = logo_photo  # conserver une référence

            # create default widgets, use update method to update state

            # Menu items
            self.button_status = master.create_menu_button(
                self,
                "Insert Card",
                "insert_card.jpg",
                0.26, 0.05,
                command=lambda: None,
                state='normal'
            )

            # webshop
            self.button_webshop = master.create_menu_button(
                self,
                "Go to the Webshop",
                "webshop.png",
                0.95, 0.05,
                command=lambda: webbrowser.open("https://satochip.io/shop/", new=2),
                state='normal'
            )

            self.place(relx=0.0, rely=0.5, anchor="w")

        except Exception as e:
            logger.error(f"010 Unexpected error in _seedkeeper_lateral_menu: {e}", exc_info=True)
