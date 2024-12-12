import customtkinter
import logging
from PIL import Image, ImageTk
import webbrowser
import pyperclip

from constants import ICON_PATH
from frameWidgetLabel import FrameWidgetLabel

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameWidgetSatodimeCard(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        try:
            logger.debug("FrameWidgetSatodimeCard init")

            # Créer le cadre de l'en-tête
            self.configure(
                width=750, height=100,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # y-offset
            rely = 0

            # Status field
            # self.status_label = FrameWidgetLabel(master=self, text="Status:")
            # self.status_label.place(relx=0.05, rely=rely, anchor="nw")
            # self.status_value = FrameWidgetLabel(master=self, text="")
            # self.status_value.place(relx=0.25, rely=rely, anchor="nw")
            # rely += 0.25

            # Blockchain field
            self.blockchain_label = FrameWidgetLabel(master=self, text="Blockchain:")
            self.blockchain_label.place(relx=0.05, rely=rely, anchor="nw")
            self.blockchain_value = FrameWidgetLabel(master=self, text="")
            self.blockchain_value.place(relx=0.25, rely=rely, anchor="nw")
            rely += 0.30

            # Address field
            self.address_label = FrameWidgetLabel(master=self, text="Address:")
            self.address_label.place(relx=0.05, rely=rely, anchor="nw")
            self.address_value = FrameWidgetLabel(master=self, text="")
            self.address_value.place(relx=0.25, rely=rely, anchor="nw")

            # button for copy
            # load icon image
            bg_color = "whitesmoke"
            self.icon_path = f"{ICON_PATH}{'copy_icon.png'}"
            self.image = Image.open(self.icon_path)
            self.image = self.image.resize((24, 24), Image.LANCZOS)
            self.photo_image = ImageTk.PhotoImage(self.image)
            # create button
            self.button_copy = customtkinter.CTkButton(
                self, width=28, height=28, text="",
                border_spacing=0,
                image=self.photo_image,
                bg_color=bg_color, fg_color=bg_color,
                hover_color=bg_color,
            )
            self.button_copy.image = self.photo_image  # keep a reference of image
            self.button_copy.place(relx=0.15, rely=rely, anchor="nw")

            # button for explorer
            # load icon image
            self.icon_path2 = f"{ICON_PATH}{'open_in_browser.png'}"
            self.image = Image.open(self.icon_path2)
            self.image = self.image.resize((24, 24), Image.LANCZOS)
            self.photo_image2 = ImageTk.PhotoImage(self.image)
            # create button
            self.button_explore = customtkinter.CTkButton(
                self, width=28, height=28, text="",
                border_spacing=0,
                image=self.photo_image2,
                bg_color=bg_color, fg_color=bg_color,
                hover_color=bg_color,
            )
            self.button_explore.image = self.photo_image2  # keep a reference of image
            self.button_explore.place(relx=0.18, rely=rely, anchor="nw")

            rely += 0.30

            # Balances field
            self.balance_label = FrameWidgetLabel(master=self, text="Balance:")
            self.balance_label.place(relx=0.05, rely=rely, anchor="nw")
            self.balance_value = FrameWidgetLabel(master=self, text="")
            self.balance_value.place(relx=0.25, rely=rely, anchor="nw")
            self.balance_value2 = FrameWidgetLabel(master=self, text="")
            self.balance_value2.configure(font=customtkinter.CTkFont(family="Outfit", size=16, weight="normal"))
            self.balance_value2.place(relx=0.5, rely=rely, anchor="nw")

        except Exception as e:
            logger.error(f"An unexpected error occurred in init: {e}", exc_info=True)

    def update_frame(
            self,
            status: str,
            blockchain: str,
            address: str,
            url: str,
            balance: str,
            balance2: str
    ):
        logger.debug("FrameWidgetSatodimeCard update_frame")
        # self.status_value.configure(text=status)
        self.blockchain_value.configure(text=blockchain)
        self.address_value.configure(text=address)
        self.button_explore.configure(command=lambda: webbrowser.open(url, new=2))
        self.button_copy.configure(command=lambda: pyperclip.copy(address))
        self.balance_value.configure(text=balance)
        self.balance_value2.configure(text=balance2)
