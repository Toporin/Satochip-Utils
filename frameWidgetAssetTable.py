import customtkinter
import logging

from constants import (HIGHLIGHT_COLOR, BG_MAIN_MENU, DEFAULT_BG_COLOR,
                        BG_HOVER_BUTTON, TEXT_COLOR, BUTTON_TEXT_COLOR)
from frameWidgetAssetRow import FrameWidgetAssetRow
from frameWidgetScrollableFrame import FrameWidgetScrollableFrame

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameWidgetAssetTable(FrameWidgetScrollableFrame):
#class FrameWidgetAssetTable(customtkinter.CTkFrame):

    # def __init__(self, master, width, height):
    #     super().__init__(master, width, height)
    #
    #     logger.debug("init")
    #
    #     try:
    #
    #         # Creating new frame
    #         self.configure(
    #             width=750, height=300,
    #             bg_color="whitesmoke", fg_color="whitesmoke"
    #         )
    #
    #         # table header
    #         # currently none... todo?
    #
    #         # table content
    #         self.table_frame = FrameWidgetScrollableFrame(
    #             self, width=750, height=300
    #         )
    #         self.table_frame.place(relx=0.0, rely=0.0, anchor="nw")
    #         #self.log_rows = []
    #
    #     except Exception as e:
    #         logger.error(f"Init error : {e}", exc_info=True)

    def update_frame(self, asset_list):
        logger.debug(f"update_frame asset_list size: {len(asset_list)}")
        # todo clear list if needed?

        def _on_mouse_on_log(event, button):
            button.configure(fg_color=HIGHLIGHT_COLOR, cursor="hand2")

        def _on_mouse_out_log(event, button):
            button.configure(fg_color=DEFAULT_BG_COLOR)

        # populate table with assets
        for i, asset in enumerate(asset_list):

            #row_frame = FrameWidgetAssetRow(self.table_frame.inner_frame, width=700, height=28)
            row_frame = FrameWidgetAssetRow(self.inner_frame, width=self.width, height=28)

            name = asset.get('name', asset.get('contract', "(unknown)"))
            balance = "0.1 TOK"
            balance2 = "100 USD"
            url = "https://google.com"
            row_frame.update_frame(row_id=i, name=name, balance=balance, balance2=balance2, url=url)

            row_frame.bind("<Enter>", lambda event, btn=row_frame: _on_mouse_on_log(event, btn))
            row_frame.bind("<Leave>", lambda event, btn=row_frame: _on_mouse_out_log(event, btn))

            # add frame
            row_frame.pack(pady=2, fill="x")

            # todo add row to list (keep ref to destroy them on card removal)
            #self.log_rows += [row_frame]


