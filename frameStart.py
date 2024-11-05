import customtkinter
import logging

from constants import MAIN_MENU_COLOR

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameStart(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameStart init")

        try:
            self.configure(width=750, height=600)

            # Loading default background photo
            self.background_photo = master.create_background_photo("./pictures_db/insert_card.png")
            self.canvas = master.create_canvas(width=750, height=600, frame=self)
            self.canvas.place(relx=0.0, rely=0.5, anchor="w")
            self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")

            # Creating header
            self.header = master.create_an_header("Welcome", "home_popup.jpg", frame=self)
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            # Setting up labels
            self.label1 = master.create_label(
                "Please insert your card into your smart card",
                frame=self
            )
            self.label1.place(relx=0.05, rely=0.27, anchor="w")

            self.label2 = master.create_label(
                "reader, and select the action you wish to perform.",
                frame=self
            )
            self.label2.place(relx=0.05, rely=0.32, anchor="w")

            # if master.controller.cc.card_type == "SeedKeeper":
            #     master.show_seedkeeper_menu()
            # else:
            #     master.show_settings_menu()

            self.update()
            self.place(relx=1, rely=0.5, anchor="e")


        except Exception as e:
            message = f"An unexpected error occurred in create_start_frame: {e}"
            logger.error(message, exc_info=True)

    def update(self):
        logger.debug("FrameStart update() start")
        if self.master.controller.cc.card_present:
            logger.info(f"card type: {self.master.controller.cc.card_type}")
            self.label1.configure(text=f"Your {self.master.controller.cc.card_type} is connected.")
            self.label2.configure(text="Select on the menu the action you wish to perform.")
            if self.master.controller.cc.card_type == "Satochip":
                self.background_photo = self.master.create_background_photo("./pictures_db/card_satochip.png")
                self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")
                # update menu
                #self.master.show_settings_menu()
            elif self.master.controller.cc.card_type == "SeedKeeper":
                self.background_photo = self.master.create_background_photo("./pictures_db/card_seedkeeper.png")
                self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")
                # update menu
                #self.master.show_seedkeeper_menu()
            elif self.master.controller.cc.card_type == "Satodime":
                self.background_photo = self.master.create_background_photo("./pictures_db/card_satodime.png")
                self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")
                # update menu
                #self.master.show_settings_menu()
        else:
            self.label1.configure(text="Please insert your card into your smart card")
            self.label2.configure(text="reader, and select the action you wish to perform.")
            self.background_photo = self.master.create_background_photo("./pictures_db/insert_card.png")
            self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")