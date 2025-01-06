import webbrowser

import customtkinter
import logging
from PIL import Image, ImageTk

from constants import MAIN_MENU_COLOR, ICON_PATH
from framePopup import FramePopup

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameMenuSatodime(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameMenuSatodime init")
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
            self.button_my_vaults = master.create_menu_button(
                self,
                "Overview",
                "secrets.png",
                0.26, 0.05,
                state="normal",
                command=lambda: master.show_satodime_overview(),
            )

            rely = 0.33
            self.button_vaults_array = []
            for vault_nbr in range(3): # TODO: currently max 3 vaults supported
                button_vault = self.master.create_menu_button(
                    self,
                    f"Vault #{vault_nbr}",
                    "secrets.png",
                    rely, 0.05,
                    state="normal",
                    command=lambda index=vault_nbr: self.master.show_satodime_vault(index),
                )
                self.button_vaults_array += [button_vault]
                rely += 0.07

            self.button_settings = master.create_menu_button(
                self, "Settings",
                "settings.png",
                0.74, 0.05,
                state="normal",
                command=lambda: [
                    master.show_about_frame(),
                    master.show_settings_satodime_menu(),
                ]
            )

            self.button_help = master.create_menu_button(
                self, "Online help", "help.png",
                0.88, 0.05,
                state='normal',
                command=lambda: webbrowser.open("https://satochip.io/setup-use-seedkeeper-on-desktop/", new=2)
            )

            self.button_webshop = master.create_menu_button(
                self,
                "Go to the webshop", "webshop.png",
                0.95, 0.05,
                state='normal',
                command=lambda: webbrowser.open("https://satochip.io/shop/", new=2)
            )

            self.place(relx=0.0, rely=0.5, anchor="w")

        except Exception as e:
            logger.error(f"010 Unexpected error in FrameMenuSatodime init(): {e}", exc_info=True)


    def update_frame(self):

        rely = 0.33
        for vault_nbr in range(3):  # TODO: currently max 3 vaults supported

            # show/hide vaults that are not supported by the card
            if vault_nbr < self.master.controller.satodime_nb_vaults:
                self.button_vaults_array[vault_nbr].place(relx=0.05, rely=rely, anchor="w")
            else:
                self.button_vaults_array[vault_nbr].place_forget()
            rely += 0.07


        # check satodime version
        # for v0.1-0.1, we need to take ownership to access vault info
        full_version = ((self.master.controller.card_status["protocol_major_version"] << 24) +
                        (self.master.controller.card_status["protocol_minor_version"] << 16) +
                        (self.master.controller.card_status["applet_major_version"] << 8) +
                        self.master.controller.card_status["applet_minor_version"])
        logger.info(f"Satodime card full_version: {full_version}")
        if full_version <= 0x00010001 and not self.master.controller.cc.setup_done:
            logger.warning(f"DEBUG DEBUG before POPUP ")
            FramePopup(
                self,
                "Take ownership?",
                "To display vaults info, the card ownership must be taken. \nDo you want to take the card ownership on this device?",
                "Yes",
                lambda: [
                    self.master.controller.satodime_take_card_ownership(),
                    self.master.update_status(isConnected=True),
                ],
                './pictures_db/secrets_popup.png',  # todo
                button2_txt="Cancel",
                cmd2=lambda: logger.info(f"take ownership action cancelled"),
            )
            logger.warning(f"DEBUG DEBUG after POPUP ")








