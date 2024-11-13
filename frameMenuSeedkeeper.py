import webbrowser

import customtkinter
import logging
from PIL import Image, ImageTk

from constants import MAIN_MENU_COLOR, ICON_PATH

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class FrameMenuSeedkeeper(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameMenuSeedkeeper init")
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
            self.button_my_secrets = master.create_button_for_main_menu_item(
                self,
                "My secrets",
                "secrets.png",
                0.26, 0.05,
                state="normal",
                command=lambda: master.show_view_my_secrets(),
            )

            self.button_generate = master.create_button_for_main_menu_item(
                self,
                "Generate",
                "generate.png",
                0.33, 0.05,
                state="normal",
                command=lambda: master.show_generate_secret()
            )

            self.button_import = master.create_button_for_main_menu_item(
                self,
                "Import",
                "import.png",
                0.40, 0.05,
                state="normal",
                command=lambda: master.show_import_secret()
            )

            self.button_backup = master.create_button_for_main_menu_item(
                self, "Backup card",
                "logs.png",
                0.47, 0.05,
                state="normal",
                command=lambda: master.show_backup_card()
            )

            self.button_logs = master.create_button_for_main_menu_item(
                self, "Logs",
                "logs.png",
                0.54, 0.05,
                state="normal",
                command=lambda: master.show_card_logs()
            )

            self.button_settings = master.create_button_for_main_menu_item(
                self, "Settings",
                "settings.png",
                0.74, 0.05,
                state="normal",
                command=lambda: master.show_about_frame()
            )

            self.button_help = master.create_button_for_main_menu_item(
                self, "Online help", "help.png",
                0.81, 0.05,
                state='normal',
                command=lambda: webbrowser.open("https://satochip.io/setup-use-seedkeeper-on-desktop/", new=2)
            )

            self.button_webshop = master.create_button_for_main_menu_item(
                self,
                "Go to the webshop", "webshop.png",
                0.95, 0.05,
                state='normal',
                command=lambda: webbrowser.open("https://satochip.io/shop/", new=2)
            )

            self.place(relx=0.0, rely=0.5, anchor="w")

        except Exception as e:
            logger.error(f"010 Unexpected error in _seedkeeper_lateral_menu: {e}", exc_info=True)
