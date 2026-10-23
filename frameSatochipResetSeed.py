import customtkinter
import logging

import constants
from frameWidgetHeader import FrameWidgetHeader

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameSatochipResetSeed(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameSatochipResetSeed init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Creating header
            self.header = FrameWidgetHeader(
                "Reset seed",
                "reset_icon_red.png",
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            # setup paragraph
            self.text1 = master.create_label(
                "Reset the seed of your Satochip card.",
                frame=self
            )
            self.text1.place(relx=0.05, rely=0.17, anchor="w")

            self.text2 = master.create_label(
                "This removes the seed and all derived private keys from the card.",
                frame=self
            )
            self.text2.place(relx=0.05, rely=0.22, anchor="w")

            self.text3 = master.create_label(
                "After the reset, you will be able to import or generate a new seed.",
                frame=self
            )
            self.text3.place(relx=0.05, rely=0.27, anchor="w")

            # warning
            self.text_warning1 = master.create_label("Warning!", frame=self)
            self.text_warning1.configure(font=master.make_text_bold(), text_color="red")
            self.text_warning1.place(relx=0.05, rely=0.36, anchor="w")
            self.text_warning2 = master.create_label(
                "Erasing the seed cannot be undone.",
                frame=self
            )
            self.text_warning2.configure(text_color="red")
            self.text_warning2.place(relx=0.05, rely=0.41, anchor="w")
            self.text_warning3 = master.create_label(
                "Make sure you have a backup of your seed before proceeding,",
                frame=self
            )
            self.text_warning3.configure(text_color="red")
            self.text_warning3.place(relx=0.05, rely=0.46, anchor="w")
            self.text_warning4 = master.create_label(
                "otherwise your funds may be lost.",
                frame=self
            )
            self.text_warning4.configure(text_color="red")
            self.text_warning4.place(relx=0.05, rely=0.51, anchor="w")

            # confirmation checkbox
            self.checkbox_confirmation_value = customtkinter.StringVar(value="off")

            def update_checkbox_confirmation():
                if self.checkbox_confirmation_value.get() == "on":
                    self.reset_button.configure(state="normal")
                else:
                    self.reset_button.configure(state="disabled")

            self.checkbox_confirmation = customtkinter.CTkCheckBox(
                self,
                text="I confirm that I have made a backup of the seed",
                text_color="red",
                font=customtkinter.CTkFont(family=constants.FONT_FAMILY, size=16, weight="bold"),
                command=update_checkbox_confirmation,
                variable=self.checkbox_confirmation_value,
                onvalue="on",
                offvalue="off"
            )
            self.checkbox_confirmation.place(relx=0.05, rely=0.60, anchor="w")

            # Creating cancel and reset buttons
            self.cancel_button = master.create_button(
                "Cancel",
                lambda: master.reset_seed_return_callback(),
                frame=self
            )
            self.cancel_button.place(relx=0.6, rely=0.9, anchor="w")

            self.reset_button = master.create_button(
                "Reset!",
                lambda: self.reset_seed(),
                frame=self
            )
            self.reset_button.configure(state="disabled")  # enabled by confirmation checkbox
            self.reset_button.place(relx=0.8, rely=0.9, anchor="w")

            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"An unexpected error occurred in FrameSatochipResetSeed init: {e}", exc_info=True)

    def update_frame(self):
        # reset confirmation state
        self.checkbox_confirmation_value.set(value="off")
        self.reset_button.configure(state="disabled")

    def reset_seed(self):
        self.master.update_verify_pin()
        self.master.controller.reset_seed(
            on_success=self.master.reset_seed_return_callback
        )
