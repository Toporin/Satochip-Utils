from typing import SupportsIndex
import customtkinter
import logging
from pysatochip.JCconstants import STATE_UNINITIALIZED

from frameWidgetHeader import FrameWidgetHeader
from frameWidgetSatodimeCard import FrameWidgetSatodimeCard
from utils import format_asset_balances

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameSatodimeOverview(customtkinter.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameSatodimeVaults init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Creating header
            self.header = FrameWidgetHeader(
                "My vaults",
                "generate_popup.png",
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            # display vaults
            self.vaultcards = None

            # place frame
            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            error_msg = f"FrameSatodimeVaults init: Failed to create frame: {e}"
            logger.error(error_msg, exc_info=True)

    def update_frame(self):
        # populate vaults
        nb_vaults = self.master.controller.satodime_nb_vaults
        rely = 0.25
        if self.vaultcards is None:
            self.vaultcards = nb_vaults * [None]
        for vault_nbr in range(nb_vaults):
            self.update_frame_vault(vault_nbr)
            self.vaultcards[vault_nbr].place(relx=0.05, rely=rely, anchor="w")
            rely += 0.25

    def update_frame_vault(self, vault_nbr: SupportsIndex):
        if self.vaultcards[vault_nbr] is None:
            self.vaultcards[vault_nbr] = FrameWidgetSatodimeCard(self)

        # update info
        status_int = self.master.controller.satodime_vaults_status[vault_nbr]
        if status_int == STATE_UNINITIALIZED:
            blockchain = "not initialized"
            symbol = "UNKNOWN"  # todo
            address = ""
            url = ""
            balance_str = ""
            balance2_str = ""
        else:
            # update with cached vault info
            vault_info = self.master.controller.satodime_vaults_info[vault_nbr]
            blockchain = vault_info.get('name', 'unknown blockchain')
            symbol = vault_info.get('symbol', 'unknown blockchain')
            address = vault_info.get('address', 'unknown address')

            # update balance with cached coin info
            coin_info = self.master.controller.satodime_vaults_coin_info[vault_nbr]
            (balance_str, balance2_str) = format_asset_balances(coin_info)
            url = coin_info.get('address_explorer_url', 'no url available')

        # update vault card
        # logger.debug(f"update_frame update vaultcard for vault #{vault_nbr}")
        self.vaultcards[vault_nbr].update_frame(
            status=status_int,
            blockchain=blockchain,
            symbol=symbol,
            address=address,
            url=url,
            balance=balance_str,
            balance2=balance2_str,
        )
