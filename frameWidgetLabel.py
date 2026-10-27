import customtkinter
import logging

import constants

logger = logging.getLogger(__name__)


class FrameWidgetLabel(customtkinter.CTkLabel):
    def __init__(self, master,  text, bg_fg_color: str = "whitesmoke"):
        super().__init__(master)

        # Créer le cadre de l'en-tête
        self.configure(
            text=text,
            text_color="black",
            bg_color=bg_fg_color,
            fg_color=bg_fg_color,
            font=customtkinter.CTkFont(family=constants.FONT_FAMILY, size=18, weight="normal")
        )
