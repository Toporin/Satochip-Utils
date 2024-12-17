import customtkinter
import logging

from pycryptotools.coins import AssetType

from constants import HIGHLIGHT_COLOR, DEFAULT_BG_COLOR
from frameWidgetAssetRow import FrameWidgetAssetRow
from frameWidgetScrollableFrame import FrameWidgetScrollableFrame
from utils import format_asset_balances

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameWidgetAssetTable(FrameWidgetScrollableFrame):

    def __init__(self, master, width, height, asset_type: AssetType):
        super().__init__(master, width, height)
        self.asset_type = asset_type

    def update_frame(self, asset_list):
        logger.debug(f"update_frame asset_list size: {len(asset_list)}")
        # todo clear list if needed?

        def _on_mouse_on_log(event, button):
            button.configure(fg_color=HIGHLIGHT_COLOR, cursor="hand2")

        def _on_mouse_out_log(event, button):
            button.configure(fg_color=DEFAULT_BG_COLOR)

        # populate table with assets
        for i, asset in enumerate(asset_list):

            asset_type = asset.get('type', AssetType.TOKEN)
            if asset_type == self.asset_type:
                row_frame = FrameWidgetAssetRow(self.inner_frame, width=self.width, height=28)

                name = asset.get('name', asset.get('contract', "(unknown)"))
                (balance, balance2) = format_asset_balances(asset)
                if asset_type == AssetType.TOKEN:
                    url = asset.get('token_explorer_url', '')
                else:
                    url = asset.get('nft_explorer_url', '')
                row_frame.update_frame(row_id=i, name=name, balance=balance, balance2=balance2, url=url)

                row_frame.bind("<Enter>", lambda event, btn=row_frame: _on_mouse_on_log(event, btn))
                row_frame.bind("<Leave>", lambda event, btn=row_frame: _on_mouse_out_log(event, btn))

                # add frame
                row_frame.pack(pady=2, fill="x")

                # todo add row to list (keep ref to destroy them on card removal)
                #self.log_rows += [row_frame]
