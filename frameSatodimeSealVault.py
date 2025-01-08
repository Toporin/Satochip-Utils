from os import urandom

import customtkinter
import logging

from constants import (BG_BUTTON, BG_HOVER_BUTTON, BG_MAIN_MENU, COIN_DICT)
from frameWidgetExpertMode import FrameWidgetExpertMode
from frameWidgetHeader import FrameWidgetHeader
from frameWidgetLabel import FrameWidgetLabel

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameSatodimeSealVault(customtkinter.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        logger.debug("init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Creating header
            self.header = FrameWidgetHeader(
                "Seal vault #",
                "generate_popup.png",
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            self.rely = 0.15

            # intro text
            self.intro_label = FrameWidgetLabel(
                master=self,
                text="This vault is uninitialized. \nYou can generate a new random keypair and seal the vault."
            )
            self.intro_label.configure(justify="left")
            self.intro_label.place(relx=0.05, rely=self.rely, anchor="nw")
            self.rely += 0.1

            # blockchain label
            self.blockchain_label = FrameWidgetLabel(
                master=self,
                text="Select the blockchain for this vault:"
            )
            self.blockchain_label.place(relx=0.05, rely=self.rely, anchor="nw")
            self.rely += 0.07

            # select blockchain
            self.blockchain_list = list(COIN_DICT.keys()) # COIN_LIST
            self.blockchain_variable = customtkinter.StringVar(value=self.blockchain_list[0])
            self.blockchain_option_menu = customtkinter.CTkOptionMenu(
                master=self,
                variable=self.blockchain_variable,
                values=self.blockchain_list,
                width=600,
                fg_color=BG_BUTTON,  # Utilisez la même couleur que pour les entrées
                button_color=BG_BUTTON,  # Couleur du bouton déroulant
                button_hover_color=BG_HOVER_BUTTON,  # Couleur au survol du bouton
                dropdown_fg_color=BG_MAIN_MENU,  # Couleur de fond du menu déroulant
                dropdown_hover_color=BG_HOVER_BUTTON,  # Couleur au survol des options
                dropdown_text_color="white",  # Couleur du texte des options
                text_color="grey",  # Couleur du texte sélectionné
                font=customtkinter.CTkFont(family="Outfit", size=13, weight="normal"),
                dropdown_font=customtkinter.CTkFont(family="Outfit", size=13, weight="normal"),
                corner_radius=10,  # Même rayon de coin que les entrées
            )
            self.blockchain_option_menu.place(relx=0.05, rely=self.rely, anchor="nw")
            self.rely += 0.1

            # expert mode label
            self.expert_label = FrameWidgetLabel(
                master=self,
                text="The Expert Mode lets you select the network and provide your own entropy:"
            )
            self.expert_label.place(relx=0.05, rely=self.rely, anchor="nw")
            self.rely += 0.07

            # checkbox_expert_mode
            self.checkbox_expert_mode_value = customtkinter.StringVar(value="off")

            def update_checkbox_expert_mode():
                if self.checkbox_expert_mode_value.get() == "on":
                    self.expert_mode_widget.place(relx=0.0, rely=0.56, anchor="nw")
                else:
                    self.expert_mode_widget.place_forget()

            self.checkbox_expert_mode = customtkinter.CTkCheckBox(
                self,
                text="Use Expert Mode (optional)",
                command=update_checkbox_expert_mode,
                variable=self.checkbox_expert_mode_value,
                onvalue="on",
                offvalue="off"
            )
            self.checkbox_expert_mode.place(relx=0.05, rely=self.rely, anchor="nw")
            self.rely += 0.1

            # expert mode widget
            self.expert_mode_widget = FrameWidgetExpertMode(master=self)

            # Create action button
            self.right_button = master.create_button(
                text="Create and seal",
                command=None,  # will be updated in update
                frame=self
            )
            self.right_button.place(relx=0.95, rely=0.95, anchor="e")

            # place frame
            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            error_msg = f"init: Failed to create frame: {e}"
            logger.error(error_msg, exc_info=True)

    def update_frame(self, vault_nbr):
        logger.debug(f"update_frame start vault_nbr: {vault_nbr}")

        # update header
        self.header.button.configure(text=f"Seal vault #{vault_nbr}")

        def seal_vault():
            # update seal action buttons with vault number and expert mode parameters
            if self.checkbox_expert_mode_value.get() == "on":
                entropy_str = self.expert_mode_widget.entropy_textbox.get(1.0, "end-1c")
                entropy_bytes = entropy_str.encode('utf-8')
                is_testnet = (self.expert_mode_widget.radio_value_network.get() == "testnet")
            else:
                entropy_bytes = urandom(32)  # bytes([])
                is_testnet = False
            blockchain = self.blockchain_variable.get()

            self.master.controller.satodime_seal_vault(vault_nbr, blockchain, is_testnet, entropy_bytes)

        # update button command
        self.right_button.configure(
            command=lambda: seal_vault(),
        )

