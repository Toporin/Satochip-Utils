import webbrowser

import customtkinter
import logging
from PIL import Image, ImageTk

from constants import MAIN_MENU_COLOR, ICON_PATH

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class FrameMenuSettings(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameMenuSettings init")
        try:
            self.state = "normal" if master.controller.cc.card_present else "disabled"

            self.configure(
                width=250, height=600,
                bg_color=MAIN_MENU_COLOR, fg_color=MAIN_MENU_COLOR,
                corner_radius=0, border_color="black", border_width=0
            )
            # menu_frame = customtkinter.CTkFrame(
            #     self.main_frame, width=250, height=600,
            #     bg_color=MAIN_MENU_COLOR, fg_color=MAIN_MENU_COLOR,
            #     corner_radius=0, border_color="black", border_width=0
            # )

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
            logger.debug("Logo section setup complete")

            # create default widgets, use update method to update state

            # setup/seed/insert/done button
            self.button_status = master.create_button_for_main_menu_item(
                self,
                "Insert Card",
                "insert_card.jpg",
                0.26, 0.05,
                command=lambda: None,
                state='normal'
            )
            # change PIN button
            self.button_change_pin = master.create_button_for_main_menu_item(
                self,
                "Change Pin",
                "change_pin_locked.jpg",
                0.33, 0.05,
                command=lambda: master.show_change_pin_frame(),
                state='disabled'
            )
            # edit label
            self.button_edit_label = master.create_button_for_main_menu_item(
                self,
                "Edit Label",
                "edit_label_locked.jpg",
                0.40, 0.05,
                command=lambda: master.show_edit_label_frame(),
                state='disabled'
            )
            # check authenticity
            self.button_check_auth = master.create_button_for_main_menu_item(
                self,
                "Check Authenticity",
                "check_authenticity_locked.jpg",
                0.47, 0.05,
                command=lambda: master.show_check_authenticity_frame(),
                state='disabled'
            )
            # factory reset
            self.button_factory_reset = master.create_button_for_main_menu_item(
                self,
                "Reset my Card",
                "reset.png",
                0.54, 0.05,
                command=lambda: master.show_factory_reset_frame(),
                state='disabled'
            )
            # about
            self.button_about = master.create_button_for_main_menu_item(
                self,
                "About",
                "about_locked.jpg",
                0.73, 0.05,
                command=lambda: master.show_about_frame(),
                state='disabled'
            )
            # webshop
            self.button_webshop = master.create_button_for_main_menu_item(
                self,
                "Go to the Webshop",
                "webshop.png",
                0.95, 0.05,
                command=lambda: webbrowser.open("https://satochip.io/shop/", new=2),
                state='normal'
            )

            ########
            # if master.controller.cc.card_present:
            #     if not master.controller.cc.setup_done:
            #         logger.info("Setup not done, enabling 'Setup My Card' button")
            #         self.create_button_for_main_menu_item(
            #             menu_frame,
            #             "Setup my card",
            #             "setup_my_card.png",
            #             0.26, 0.05,
            #             #command=lambda: self.setup_my_card_pin(),
            #             command=lambda: self.show_setup_card_frame(),
            #             state='normal'
            #         )
            #     else:
            #         if self.controller.cc.card_type == "Satochip" and not self.controller.cc.is_seeded:
            #         #if self.controller.cc.card_type == "Satochip": #DEBUG: should check is_seeded flag!!
            #             logger.info("Card not seeded, enabling 'Setup Seed' button")
            #             self.create_button_for_main_menu_item(
            #                 menu_frame,
            #                 "Setup Seed",
            #                 "seed.png",
            #                 0.26, 0.05,
            #                 command=lambda: self.show_seed_import_frame(), state='normal'
            #             )
            #         else:
            #             logger.info("Setup completed, disabling 'Setup Done' button")
            #             self.create_button_for_main_menu_item(
            #                 menu_frame,
            #                 "Setup Done" if self.controller.cc.card_present else 'Insert Card',
            #                 "setup_done.jpg" if self.controller.cc.card_present else "insert_card.jpg",
            #                 0.26, 0.05,
            #                 command=lambda: None, state='disabled'
            #             )
            # else:
            #     logger.info("Card not present, setting 'Setup My Card' button state")
            #     self.create_button_for_main_menu_item(
            #         menu_frame,
            #         "Insert a Card",
            #         "insert_card.jpg",
            #         0.26, 0.05,
            #         command=lambda: None, state='normal'
            #     )
            #
            # if self.controller.cc.card_type != "Satodime" and self.controller.cc.setup_done:
            #     logger.debug("Enabling 'Change Pin' button")
            #     self.create_button_for_main_menu_item(
            #         menu_frame,
            #         "Change Pin",
            #         "change_pin.png",
            #         0.33, 0.05,
            #         command=lambda: self.show_change_pin_frame(),
            #         state='normal'
            #     )
            # else:
            #     logger.info(f"Card type is {self.controller.cc.card_type} | Disabling 'Change Pin' button")
            #     self.create_button_for_main_menu_item(
            #         menu_frame,
            #         "Change Pin",
            #         "change_pin_locked.jpg",
            #         0.33, 0.05,
            #         command=lambda: self.show_change_pin_frame(),
            #         state='disabled'
            #     )
            #
            # if self.controller.cc.setup_done:
            #     self.create_button_for_main_menu_item(
            #         menu_frame,
            #         "Edit Label",
            #         "edit_label.png",
            #         0.40, 0.05,
            #         command=lambda: [self.show_edit_label_frame()], state='normal'
            #     )
            # else:
            #     self.create_button_for_main_menu_item(
            #         menu_frame,
            #         "Edit Label",
            #         "edit_label_locked.jpg",
            #         0.40, 0.05,
            #         command=lambda: self.edit_label(), state='disabled'
            #     )
            #
            # if self.controller.cc.setup_done:
            #     self.create_button_for_main_menu_item(
            #         menu_frame,
            #         "Check Authenticity",
            #         "auth.png",
            #         0.47, 0.05,
            #         command=lambda: self.show_check_authenticity_frame(), state='normal'
            #     )
            # else:
            #     self.create_button_for_main_menu_item(
            #         menu_frame,
            #         "Check Authenticity",
            #         "check_authenticity_locked.jpg",
            #         0.47, 0.05,
            #         command=lambda: self.check_authenticity(), state='disabled'
            #     )
            # if self.controller.cc.card_present:
            #     if self.controller.cc.card_type != "Satodime":
            #         self.create_button_for_main_menu_item(
            #             menu_frame,
            #             "Reset my Card",
            #             "reset.png",
            #             0.54, 0.05,
            #             command=lambda: self.show_factory_reset_frame(), state='normal'
            #         )
            #     else:
            #         # TODO: remove button?
            #         self.create_button_for_main_menu_item(
            #             menu_frame,
            #             "Reset my Card",
            #             "reset_locked.jpg",
            #             0.54, 0.05,
            #             command=lambda: None, state='disabled'
            #         )
            #
            #     self.create_button_for_main_menu_item(
            #         menu_frame,
            #         "About",
            #         "about.jpg",
            #         0.73, 0.05,
            #         command=lambda: self.show_about_frame(),
            #         state='normal'
            #     )
            # else:
            #     self.create_button_for_main_menu_item(
            #         menu_frame,
            #         "Reset my Card",
            #         "reset_locked.jpg",
            #         0.54, 0.05,
            #         command=lambda: None, state='disabled'
            #     )
            #     self.create_button_for_main_menu_item(
            #         menu_frame,
            #         "About",
            #         "about_locked.jpg",
            #         0.73, 0.05,
            #         command=lambda: self.show_about_frame(),
            #         state='disabled'
            #     )
            #
            # self.create_button_for_main_menu_item(
            #     menu_frame,
            #     "Go to the Webshop",
            #     "webshop.png",
            #     0.95, 0.05,
            #     command=lambda: webbrowser.open("https://satochip.io/shop/", new=2), state='normal'
            # )

            self.place(relx=0.0, rely=0.5, anchor="w")

            logger.info("Main menu setup complete")

        except Exception as e:
            logger.error(f"An error occurred in main_menu: {e}", exc_info=True)


    def update(self, require_redraw: bool = True):
        logger.debug("FrameMenuSetting update() start")
        logger.debug(f"FrameMenuSetting update() card_present: {self.master.controller.cc.card_present}")
        logger.debug(f"FrameMenuSetting update() card_type: {self.master.controller.cc.card_type}")
        logger.debug(f"FrameMenuSetting update() setup_done: {self.master.controller.cc.setup_done}")
        logger.debug(f"FrameMenuSetting update() is_seeded: {self.master.controller.cc.is_seeded}")

        if self.master.controller.cc.card_present:
            if self.master.controller.cc.card_type == "Satochip":
                self.button_factory_reset.configure(state="normal")
                if self.master.controller.cc.setup_done:
                    self.button_change_pin.configure(state="normal")
                    self.button_edit_label.configure(state="normal")
                    self.button_check_auth.configure(state="normal")
                    self.button_about.configure(state="normal")
                    if self.master.controller.cc.is_seeded:
                        photo_image = self.master.convert_icon_name_to_photo_image("setup_done.jpg")
                        self.button_status.configure(
                            require_redraw,
                            text="Setup Done", image=photo_image,
                            command=lambda: None,
                            state='normal'
                        )

                    else: # import seed
                        photo_image = self.master.convert_icon_name_to_photo_image("seed.png")
                        self.button_status.configure(
                            require_redraw,
                            text="Setup Seed", image=photo_image,
                            command=lambda: self.master.show_seed_import_frame(),
                            state='normal'
                        )
                else: # setup card
                    photo_image = self.master.convert_icon_name_to_photo_image("setup_my_card.png")
                    self.button_status.configure(
                        require_redraw,
                        text="Setup my card", image="setup_my_card.png",
                        command=lambda: self.master.show_setup_card_frame(),
                        state='normal'
                    )
                    self.button_change_pin.configure(state="disabled")
                    self.button_edit_label.configure(state="disabled")
                    self.button_check_auth.configure(state="disabled")
                    self.button_about.configure(state="disabled")

            if self.master.controller.cc.card_type == "Seedkeeper":
                self.button_factory_reset.configure(state="normal")
                if self.master.controller.cc.setup_done:
                    self.button_change_pin.configure(state="normal")
                    self.button_edit_label.configure(state="normal")
                    self.button_check_auth.configure(state="normal")
                    self.button_about.configure(state="normal")
                else:  # setup card
                    photo_image = self.master.convert_icon_name_to_photo_image("setup_my_card.png")
                    self.button_status.configure(
                        require_redraw,
                        text="Setup my card", image=photo_image,
                        command=lambda: self.master.show_setup_card_frame(),
                        state='normal'
                    )
                    self.button_change_pin.configure(state="disabled")
                    self.button_edit_label.configure(state="disabled")
                    self.button_check_auth.configure(state="disabled")
                    self.button_about.configure(state="disabled")

            if self.master.controller.cc.card_type == "Satodime":
                if self.master.controller.cc.setup_done:
                    photo_image = self.master.convert_icon_name_to_photo_image("setup_done.jpg")
                    self.button_status.configure(
                        require_redraw,
                        text="Setup Done", image=photo_image,
                        command=lambda: None,
                        state="normal"
                    )
                    self.button_edit_label.configure(state="normal")
                    self.button_check_auth.configure(state="normal")
                    self.button_about.configure(state="normal")
                else: # todo check
                    photo_image = self.master.convert_icon_name_to_photo_image("setup_my_card.png")
                    self.button_status.configure(
                        require_redraw,
                        text="Setup my card", image=photo_image,
                        command=lambda: self.master.show_setup_card_frame(),
                        state="normal"
                    )
                    self.button_edit_label.configure(state="disabled")
                    self.button_check_auth.configure(state="disabled")
                    self.button_about.configure(state="disabled")

        else: # no card
            photo_image = self.master.convert_icon_name_to_photo_image("insert_card.jpg")
            self.button_status.configure(text="Insert card", image=photo_image, command=lambda: None)
            self.button_change_pin.configure(state="disabled")
            self.button_edit_label.configure(state="disabled")
            self.button_check_auth.configure(state="disabled")
            self.button_about.configure(state="disabled")
            self.button_factory_reset.configure(state="disabled")







