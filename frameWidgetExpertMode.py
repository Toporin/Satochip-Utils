import customtkinter
import logging

from constants import BG_BUTTON
from frameWidgetLabel import FrameWidgetLabel

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameWidgetExpertMode(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=400,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            self.rely = 0.0

            # network label
            self.network_label = FrameWidgetLabel(
                master=self,
                text=f"Select network: ",
            )
            self.network_label.place(relx=0.15, rely=self.rely, anchor="nw")

            # network selector
            self.radio_value_network = customtkinter.StringVar(value="mainnet")

            def update_radio_network():
                pass

            self.radio_button_mainnet = customtkinter.CTkRadioButton(
                self,
                text="MainNet",
                variable=self.radio_value_network,
                value="mainnet",
                font=customtkinter.CTkFont(family="Outfit", size=18, weight="normal"),
                bg_color="whitesmoke", fg_color="green",
                hover_color="green",
                command=update_radio_network
            )
            self.radio_button_mainnet.place(relx=0.35, rely=self.rely, anchor="nw")

            self.radio_button_testnet = customtkinter.CTkRadioButton(
                self,
                text="TestNet",
                variable=self.radio_value_network,
                value="testnet",
                font=customtkinter.CTkFont(family="Outfit", size=18, weight="normal"),
                bg_color="whitesmoke", fg_color="green",
                hover_color="green",
                command=update_radio_network
            )
            self.radio_button_testnet.place(relx=0.5, rely=self.rely, anchor="nw")

            self.rely += 0.1

            # entropy label
            self.entropy_label = FrameWidgetLabel(
                master=self,
                text=f"Provide entropy (included during random keypair generation):"
            )
            self.entropy_label.place(relx=0.15, rely=self.rely, anchor="nw")
            self.rely += 0.08
            # entropy textbox
            self.entropy_textbox = customtkinter.CTkTextbox(
                self, corner_radius=20, bg_color="whitesmoke", fg_color=BG_BUTTON,
                border_color=BG_BUTTON, border_width=1, width=500, height=90,
                text_color="grey",
                font=customtkinter.CTkFont(family="Outfit", size=13, weight="normal")
            )
            self.entropy_textbox.place(relx=0.15, rely=self.rely, anchor="nw")

        except Exception as e:
            logger.error(f"Init error : {e}", exc_info=True)

    def update_frame(self):
        logger.debug(f"update_frame")
        pass
