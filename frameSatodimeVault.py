import asyncio
import aiohttp
import customtkinter
import logging

from constants import (DEFAULT_BG_COLOR, BG_MAIN_MENU, BG_HOVER_BUTTON,
                       TEXT_COLOR, BUTTON_TEXT_COLOR, HIGHLIGHT_COLOR, TYPE_MASTERSEED, TYPE_DIC)
from frameWidgetHeader import FrameWidgetHeader

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameSatodimeVault(customtkinter.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameSatodimeVault init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Creating header
            self.header = FrameWidgetHeader(
                "Vault",
                "generate_popup.png",
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            # todo display vaults
            # Create balance field
            rely = 0.15
            self.balance_label = master.create_label("Balance:", frame=self)
            self.balance_label.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.05
            self.balance_entry = master.create_label("", frame=self)
            self.balance_entry.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.1

            # Create address field

            self.address_label = master.create_label("Address:", frame=self)
            self.address_label.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.05
            self.address_entry = master.create_label("", frame=self)
            self.address_entry.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.1


            # place frame
            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            error_msg = f"FrameSatodimeVault init: Failed to create frame: {e}"
            logger.error(error_msg, exc_info=True)

    def update_frame(self, vault_nbr):
        logger.debug(f"update_frame start vault_nbr: {vault_nbr}")
        logger.debug(f"update_frame start satodime_vaults_info.size: {len(self.master.controller.satodime_vaults_info)}")

        vault_info = self.master.controller.satodime_vaults_info[vault_nbr]

        self.header.button.configure(text=f"Vault #{vault_nbr}")
        self.address_entry.configure(text=vault_info.get('address', 'unknown'))


        logger.debug("update_frame end")

