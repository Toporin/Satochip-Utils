import time

import customtkinter
import logging
from PIL import Image, ImageTk

from constants import ICON_PATH

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameWidgetHeader(customtkinter.CTkFrame):
    def __init__(self, title_text: str = "", icon_name: str = None, frame=None):
        super().__init__(frame)
        try:
            logger.debug("FrameWidgetHeader init")

            # Créer le cadre de l'en-tête
            self.configure(
                width=750, height=40,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Creating header with title and icon
            self.title_text = f"{'   '}{title_text}"
            self.icon_path = f"{ICON_PATH}{icon_name}"

            # Charger et redimensionner l'image de l'icône
            self.image = Image.open(self.icon_path)
            self.image = self.image.resize((40, 40), Image.LANCZOS)
            self.photo_image = ImageTk.PhotoImage(self.image)

            # Créer le bouton avec l'image de l'icône
            self.button = customtkinter.CTkButton(
                self, text=self.title_text, image=self.photo_image,
                font=customtkinter.CTkFont(family="Outfit", size=25, weight="bold"),
                bg_color="whitesmoke", fg_color="whitesmoke", text_color="black",
                hover_color="whitesmoke", compound="left"
            )
            self.button.image = self.photo_image  # Garder une référence de l'image
            self.button.place(rely=0.5, relx=0, anchor="w")

        except Exception as e:
            logger.error(f"An unexpected error occurred in init: {e}", exc_info=True)

    def update_frame(self):
        pass
