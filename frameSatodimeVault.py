import asyncio
import aiohttp
import customtkinter
import logging

from constants import (DEFAULT_BG_COLOR, BG_MAIN_MENU, BG_HOVER_BUTTON,
                       TEXT_COLOR, BUTTON_TEXT_COLOR, HIGHLIGHT_COLOR, TYPE_MASTERSEED, TYPE_DIC, STATUS_DIC)
from frameWidgetAssetTab import FrameWidgetAssetTab
from frameWidgetAssetTable import FrameWidgetAssetTable
from frameWidgetHeader import FrameWidgetHeader
from frameWidgetSatodimeCard import FrameWidgetSatodimeCard

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameSatodimeVault(customtkinter.CTkFrame):

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
                "Vault",
                "generate_popup.png",
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            # satocard: show info about the coin in the vault
            self.vaultcard = FrameWidgetSatodimeCard(master=self)
            self.vaultcard.place(relx=0.0, rely=0.15, anchor="nw")

            # tabs with token & nft assets info
            self.asset_tab = FrameWidgetAssetTab(master=self, width=750, height=300)
            self.asset_tab.place(relx=0.0, rely=0.5, anchor="nw")

            # DEBUG directly place token frame
            #self.token_table = FrameWidgetAssetTable(master=self, width=750, height=300)
            #self.token_table.place(relx=0.0, rely=0.5, anchor="nw")


            # place frame
            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            error_msg = f"FrameSatodimeVault init: Failed to create frame: {e}"
            logger.error(error_msg, exc_info=True)

    def update_frame(self, vault_nbr):
        logger.debug(f"update_frame start vault_nbr: {vault_nbr}")
        logger.debug(f"update_frame start satodime_vaults_info.size: {len(self.master.controller.satodime_vaults_info)}")

        # update header
        self.header.button.configure(text=f"Vault #{vault_nbr}")

        # update card
        status_int = self.master.controller.satodime_vaults_status[vault_nbr]
        status = STATUS_DIC.get(status_int, "unknown status")
        vault_info = self.master.controller.satodime_vaults_info[vault_nbr]
        blockchain = vault_info.get('name', 'unknown blockchain')
        address = vault_info.get('address', 'unknown address')

        coin_info = self.master.controller.satodime_vaults_coin_info[vault_nbr]
        url = coin_info.get('address_explorer_url', 'no url available')
        symbol = coin_info.get('symbol', '')
        balance_dec = coin_info.get('balance', None)
        logger.debug(f"balance_dec: {balance_dec} {symbol}")
        balance_str = f""
        balance2_str = f""
        if balance_dec is not None:
            balance_str = f"{balance_dec} {symbol}"
            # in second devise #todo: select devise...
            rate_dec = coin_info.get('exchange_rate', None)
            symbol2 = coin_info.get('currency', '')
            logger.debug(f"rate_dec: {rate_dec} {symbol2}")
            if rate_dec is not None:
                balance2_dec = balance_dec * rate_dec
                balance2_str = f"{balance2_dec} {symbol2}"
                logger.debug(f"balance2_str: {balance2_str}")

        logger.debug(f"update_frame update vaultcard for vault #{vault_nbr}")
        self.vaultcard.update_frame(
            status=status,
            blockchain=blockchain,
            address=address,
            url=url,
            balance=balance_str,
            balance2=balance2_str,
        )

        # update tabs
        asset_list = self.master.controller.satodime_vaults_asset_list[vault_nbr]
        self.asset_tab.update_tab(asset_list)
        # DEBUG update token table directly without tabs
        #self.token_table.update_frame(asset_list)


