import webbrowser

import logging
from PIL import Image, ImageTk

from pycryptotools.coins import AssetType

from constants import ICON_PATH
from frameWidgetCanvasTable import FrameWidgetCanvasTable, SCROLLBAR_WIDTH
from utils import format_asset_balances

logger = logging.getLogger(__name__)


class FrameWidgetAssetTable(FrameWidgetCanvasTable):
    # Table of assets (token or NFT) of a Satodime vault; click on a row to open the asset in the explorer

    def __init__(self, master, width, height, asset_type: AssetType):
        table_width = width - SCROLLBAR_WIDTH
        super().__init__(
            master,
            [
                {'width': int(0.05 * table_width), 'anchor': "w"},  # icon
                {'width': int(0.4 * table_width), 'anchor': "w"},  # name
                {'width': int(0.3 * table_width), 'anchor': "w"},  # balance
                {'width': int(0.25 * table_width), 'anchor': "w"},  # balance2
            ],
            height=height, font_size=18, column_gap=0, striped=False,
            on_row_click=lambda url: webbrowser.open(url, new=2)
        )
        self.asset_type = asset_type

        # icon shown for each asset
        image = Image.open(f"{ICON_PATH}coin_icon.png").resize((24, 24), Image.LANCZOS)
        self.icon = ImageTk.PhotoImage(image)  # keep a reference of image

    def update_frame(self, asset_list):
        logger.debug(f"update_frame asset_list size: {len(asset_list)}")
        rows = []
        for asset in asset_list:
            asset_type = asset.get('type', AssetType.TOKEN)
            if asset_type != self.asset_type:
                continue
            name = asset.get('name', asset.get('contract', "(unknown)"))
            (balance, balance2) = format_asset_balances(asset)
            if asset_type == AssetType.TOKEN:
                url = asset.get('token_explorer_url', '')
            else:
                url = asset.get('nft_explorer_url', '')
            # todo update asset icon
            rows.append({'values': [self.icon, name, balance, balance2], 'data': url or None})
        self.set_rows(rows)
