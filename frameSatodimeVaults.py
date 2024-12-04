import customtkinter
import logging

from constants import (DEFAULT_BG_COLOR, BG_MAIN_MENU, BG_HOVER_BUTTON,
                       TEXT_COLOR, BUTTON_TEXT_COLOR, HIGHLIGHT_COLOR, TYPE_MASTERSEED, TYPE_DIC)
from frameWidgetHeader import FrameWidgetHeader

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameSatodimeVaults(customtkinter.CTkFrame):

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

            # todo display vaults

            # place frame
            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            error_msg = f"FrameSatodimeVaults init: Failed to create frame: {e}"
            logger.error(error_msg, exc_info=True)


    def update_frame(self):
        pass