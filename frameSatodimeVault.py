from PIL import Image, ImageTk
import customtkinter
import logging

from pysatochip.JCconstants import STATE_SEALED, STATE_UNSEALED

from constants import (STATUS_DIC, ICON_PATH, STATUS_COLOR_DIC)
from frameWidgetAssetTab import FrameWidgetAssetTab
from frameWidgetHeader import FrameWidgetHeader
from frameWidgetPrivkeyTab import FrameWidgetPrivkeyTab
from frameWidgetSatodimeCard import FrameWidgetSatodimeCard
from utils import format_asset_balances

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
            self.show_asset_tab = True
            self.asset_list = []
            self.asset_tab = FrameWidgetAssetTab(master=self, width=750, height=300)
            self.asset_tab.place(relx=0.0, rely=0.35, anchor="nw")

            # tabs with privkey info (will be placed on button action)
            self.privkey_tab = FrameWidgetPrivkeyTab(master=self, width=750, height=300)

            # Create action buttons (will be updated later)
            self.left_button = master.create_button(
                text="",
                command=lambda: None,  # will be updated in update_frame()
                frame=self
            )
            self.left_button.place(relx=0.75, rely=0.95, anchor="e")
            self.right_button = master.create_button(
                text="",
                command=None,  # will be updated in update
                frame=self
            )
            self.right_button.place(relx=0.95, rely=0.95, anchor="e")

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

        # fetch cached vault info
        status_int = self.master.controller.satodime_vaults_status[vault_nbr]
        vault_info = self.master.controller.satodime_vaults_info[vault_nbr]
        blockchain = vault_info.get('name', 'unknown blockchain')
        symbol = vault_info.get('symbol', 'unknown blockchain')
        address = vault_info.get('address', 'unknown address')

        # update coin icon
        self.icon_path = f"{ICON_PATH}{symbol}{'.png'}"
        self.image = Image.open(self.icon_path)
        self.image = self.image.resize((24, 24), Image.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(self.image)
        self.header.button.configure(image=self.photo_image)

        # update balance
        coin_info = self.master.controller.satodime_vaults_coin_info[vault_nbr]
        (balance_str, balance2_str) = format_asset_balances(coin_info)
        url = coin_info.get('address_explorer_url', 'no url available')

        # update vault card
        #logger.debug(f"update_frame update vaultcard for vault #{vault_nbr}")
        self.vaultcard.update_frame(
            status=status_int,
            blockchain=blockchain,
            address=address,
            url=url,
            balance=balance_str,
            balance2=balance2_str,
        )

        # update frame based on status (buttons action + vaultcard status)
        self.update_frame_by_status(vault_nbr, status_int)

        # update tabs
        self.asset_list = self.master.controller.satodime_vaults_asset_list[vault_nbr]
        if len(self.asset_list) > 0:
            self.asset_tab.update_tab(self.asset_list)
        else:
            self.asset_tab.place_forget()

    def update_frame_by_status(self, vault_nbr, status: int):
        logger.debug(f"update_frame_by_status start vault_nbr: {vault_nbr}")
        # update vaultcard status
        status_str = STATUS_DIC.get(status, 'unknown')
        status_color = STATUS_COLOR_DIC.get(status, 'black')
        self.vaultcard.status_value.configure(
            text=status_str,
            text_color=status_color,
        )

        # update action buttons
        if status == STATE_SEALED:
            # buy crypto
            vault_info = self.master.controller.satodime_vaults_info[vault_nbr]
            symbol = vault_info.get('symbol', 'unknown blockchain')
            address = vault_info.get('address', 'unknown address')
            self.left_button.configure(
                text=f"Buy {symbol}",
                command=lambda: None #todo
            )
            # unseal
            self.right_button.configure(
                text="Unseal",
                command=lambda index=vault_nbr: self.master.show_satodime_unseal_vault(index)
            )
        elif status == STATE_UNSEALED:
            # update private info tab
            vault_info = self.master.controller.satodime_vaults_info[vault_nbr]
            privkey_bytes = vault_info.get('privkey_bytes', None)
            entropy_bytes = vault_info.get('entropy_bytes', None)
            wif = vault_info.get('wif', None)
            if privkey_bytes is None or entropy_bytes is None or wif is None:
                # recover from card
                (privkey_bytes, entropy_bytes, wif) = self.master.controller.satodime_export_privkey(vault_nbr)
            self.privkey_tab.update_tab(privkey_bytes, entropy_bytes, wif)

            # show/hide privkey
            def switch_tabs():
                if self.show_asset_tab:
                    self.show_asset_tab = False
                    self.asset_tab.place_forget()
                    self.privkey_tab.place(relx=0.0, rely=0.35, anchor="nw")
                    self.left_button.configure(text="Show asset list")
                else:
                    self.show_asset_tab = True
                    if len(self.asset_list) > 0:
                        self.asset_tab.place(relx=0.0, rely=0.35, anchor="nw")
                    self.privkey_tab.place_forget()
                    self.left_button.configure(text="Show private key")

            self.left_button.configure(
                text=f"Show private key",
                command=lambda: switch_tabs()
            )
            # warning: reset!
            self.right_button.configure(
                text="Reset",
                command=lambda index=vault_nbr: self.master.show_satodime_reset_vault(index)
            )


