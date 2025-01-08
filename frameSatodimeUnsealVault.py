from PIL import Image, ImageTk
import customtkinter
import logging

from constants import ICON_PATH
from frameWidgetHeader import FrameWidgetHeader
from frameWidgetLabel import FrameWidgetLabel
from frameWidgetSatodimeCard import FrameWidgetSatodimeCard
from utils import format_asset_balances

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameSatodimeUnsealVault(customtkinter.CTkFrame):

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
                "Unseal vault #",
                "unlock_icon_black.png",
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            # intro text
            self.intro_label = FrameWidgetLabel(
                master=self,
                text="You are about to unseal the following vault:"
            )
            self.intro_label.place(relx=0.05, rely=0.15, anchor="nw")

            # satocard: show info about the coin in the vault
            # todo: border
            self.vaultcard = FrameWidgetSatodimeCard(master=self)
            self.vaultcard.place(relx=0.05, rely=0.25, anchor="nw")

            # info labels
            self.info_label = FrameWidgetLabel(
                master=self,
                text="Unsealling the vault will reveal the corresponding private key.\nYou can then transfer the entire balance to another wallet \nusing the revealed private key."
            )
            self.info_label.configure(justify="left")
            self.info_label.place(relx=0.05, rely=0.5, anchor="nw")

            self.info2_label = FrameWidgetLabel(
                master=self,
                text="This action is irreversible."
            )
            self.info2_label.configure(text_color="red")
            self.info2_label.place(relx=0.05, rely=0.65, anchor="nw")


            # Create action buttons
            self.left_button = master.create_button(
                text="Cancel",
                command=lambda: self.master.show_satodime_overview(),  # will be updated in update_frame()
                frame=self
            )
            self.left_button.place(relx=0.75, rely=0.95, anchor="e")
            self.right_button = master.create_button(
                text="Unseal!",
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

        # update header
        self.header.button.configure(text=f"Unseal vault #{vault_nbr}")

        # fetch cached vault info
        status_int = self.master.controller.satodime_vaults_status[vault_nbr]
        vault_info = self.master.controller.satodime_vaults_info[vault_nbr]
        blockchain = vault_info.get('name', 'unknown blockchain')
        symbol = vault_info.get('symbol', 'unknown blockchain')
        address = vault_info.get('address', 'unknown address')

        # update coin icon
        # self.icon_path = f"{ICON_PATH}{symbol}{'.png'}"
        # self.image = Image.open(self.icon_path)
        # self.image = self.image.resize((24, 24), Image.LANCZOS)
        # self.photo_image = ImageTk.PhotoImage(self.image)
        # self.header.button.configure(image=self.photo_image)

        # update balance
        coin_info = self.master.controller.satodime_vaults_coin_info[vault_nbr]
        (balance_str, balance2_str) = format_asset_balances(coin_info)
        url = coin_info.get('address_explorer_url', 'no url available')

        logger.debug(f"update_frame update vaultcard for vault #{vault_nbr}")
        self.vaultcard.update_frame(
            status=status_int,
            blockchain=blockchain,
            symbol=symbol,
            address=address,
            url=url,
            balance=balance_str,
            balance2=balance2_str,
        )

        # update unseal action buttons with vault number
        self.right_button.configure(
            command=lambda index=vault_nbr: self.master.controller.satodime_unseal_vault(index),
        )

