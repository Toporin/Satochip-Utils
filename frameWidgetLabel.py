import customtkinter
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameWidgetLabel(customtkinter.CTkLabel):
    def __init__(self, master,  text, bg_fg_color: str = "whitesmoke"):
        super().__init__(master)
        try:
            logger.debug("FrameWidgetLabel init")

            # Créer le cadre de l'en-tête
            self.configure(
                text=text,
                text_color="black",
                bg_color=bg_fg_color,
                fg_color=bg_fg_color,
                font=customtkinter.CTkFont(family="Outfit", size=18, weight="normal")
            )

        except Exception as e:
            logger.error(f"An unexpected error occurred in init: {e}", exc_info=True)

