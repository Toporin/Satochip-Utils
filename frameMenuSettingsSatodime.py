import webbrowser

import customtkinter
import logging
from PIL import Image, ImageTk

from constants import MAIN_MENU_COLOR, ICON_PATH
from utils import convert_name_to_photo_image

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameMenuSettingsSatodime(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameMenuSettingsSatodime init")
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
            self.rely = 0.26

            # edit label
            self.button_edit_label = master.create_menu_button(
                self,
                "Edit Label",
                "edit_label.png",
                self.rely, 0.05,
                command=lambda: master.show_edit_label_frame(),
                state='normal'
            )
            self.rely += 0.07

            # check authenticity
            self.button_check_auth = master.create_menu_button(
                self,
                "Check Authenticity",
                "check_authenticity.png",
                self.rely, 0.05,
                command=lambda: master.show_check_authenticity_frame(),
                state='normal'
            )
            self.rely += 0.07

            # about
            self.button_about = master.create_menu_button(
                self,
                "About",
                "about.jpg",
                self.rely, 0.05,  # 0.73, 0.05,
                command=lambda: master.show_about_frame(),
                state='normal'
            )
            self.rely += 0.07

            # back to start button
            self.button_back = master.create_menu_button(
                self,
                "Back",
                "back_icon.png",
                0.74, 0.05,
                command=lambda: master.show_start_frame(),
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
            logger.error(f"An error occurred in main_menu: {e}", exc_info=True)

    def update_frame(self):
        logger.debug("FrameMenuSetting update_frame() start")





