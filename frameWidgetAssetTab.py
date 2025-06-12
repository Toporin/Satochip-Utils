import customtkinter
import logging

from pycryptotools.coins import AssetType

from frameWidgetAssetTable import FrameWidgetAssetTable

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameWidgetAssetTab(customtkinter.CTkTabview):
    def __init__(self, master, width, height, **kwargs):
        super().__init__(master, width=width, height=height, **kwargs)

        logger.debug("init")

        try:
            # create tabs
            token_tab = self.add("Token")
            nft_tab = self.add("NFT")

            # set table dimension a little smaller
            table_width = width-10
            table_height = height - 10

            # set token as default
            self.set("Token")
            self.token_table = FrameWidgetAssetTable(
                master=token_tab,
                width=table_width,
                height=table_height,
                asset_type=AssetType.TOKEN
            )
            self.token_table.place(relx=0.0, rely=0.0, anchor="nw")

            # nft
            self.nft_table = FrameWidgetAssetTable(
                master=nft_tab,
                width=table_width,
                height=table_height,
                asset_type=AssetType.NFT
            )
            self.nft_table.place(relx=0.0, rely=0.0, anchor="nw")

        except Exception as e:
            logger.error(f"Init error : {e}", exc_info=True)

    def update_tab(self, asset_list):
        logger.debug(f"update_tab asset_list size: {len(asset_list)}")
        # todo: separate tokens and nfts based on type

        self.token_table.update_frame(asset_list)
        self.nft_table.update_frame(asset_list)




