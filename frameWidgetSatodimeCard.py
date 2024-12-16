import customtkinter
import logging
from PIL import Image, ImageTk
import webbrowser
import pyperclip

from constants import ICON_PATH, STATUS_DIC, STATUS_COLOR_DIC
from framePopup import FramePopup
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
                width=750, height=120,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Status field
            self.status_label = FrameWidgetLabel(master=self, text="Status:")
            self.status_label.grid(row=0, column=0, padx=5, pady=0, sticky="w")
            self.status_value = FrameWidgetLabel(master=self, text="")
            self.status_value.grid(row=0, column=1, padx=5, pady=0, sticky="w")

            # Blockchain field
            self.blockchain_label = FrameWidgetLabel(master=self, text="Blockchain:")
            self.blockchain_label.grid(row=1, column=0, padx=5, pady=0, sticky="w")
            self.blockchain_value = FrameWidgetLabel(master=self, text="")
            self.blockchain_value.grid(row=1, column=1, padx=5, pady=00, sticky="w")

            # Address field
            self.address_label = FrameWidgetLabel(master=self, text="Address:")
            self.address_label.grid(row=2, column=0, padx=5, pady=0, sticky="w")

            # frame with address and buttons
            self.address_frame = customtkinter.CTkFrame(self)
            self.address_frame.configure(bg_color="white", fg_color="white")
            self.address_frame.grid(row=2, column=1, padx=0, pady=0, sticky="w", columnspan=2)

            self.address_value = FrameWidgetLabel(master=self.address_frame, text="")
            self.address_value.grid(row=0, column=1, padx=5, pady=0, sticky="w")

            # button for copy
            # load icon image
            bg_color = "whitesmoke"
            self.icon_path = f"{ICON_PATH}{'copy_icon.png'}"
            self.image = Image.open(self.icon_path)
            self.image = self.image.resize((24, 24), Image.LANCZOS)
            self.photo_image = ImageTk.PhotoImage(self.image)
            # create button
            self.button_copy = customtkinter.CTkButton(
                self.address_frame, width=28, height=28, text="",
                border_spacing=0,
                image=self.photo_image,
                bg_color=bg_color, fg_color=bg_color,
                hover_color=bg_color,
            )
            self.button_copy.image = self.photo_image  # keep a reference of image
            self.button_copy.grid(row=0, column=2, padx=0, pady=0)

            # button for explorer
            # load icon image
            self.icon_path2 = f"{ICON_PATH}{'open_in_browser.png'}"
            self.image = Image.open(self.icon_path2)
            self.image = self.image.resize((24, 24), Image.LANCZOS)
            self.photo_image2 = ImageTk.PhotoImage(self.image)
            # create button
            self.button_explore = customtkinter.CTkButton(
                self.address_frame, width=28, height=28, text="",
                border_spacing=0,
                image=self.photo_image2,
                bg_color=bg_color, fg_color=bg_color,
                hover_color=bg_color,
            )
            self.button_explore.image = self.photo_image2  # keep a reference of image
            self.button_explore.grid(row=0, column=3, padx=0, pady=0)

            # button for qr code
            # load icon image
            self.icon_path3 = f"{ICON_PATH}{'qr_code_icon.png'}"
            self.image = Image.open(self.icon_path3)
            self.image = self.image.resize((24, 24), Image.LANCZOS)
            self.photo_image3 = ImageTk.PhotoImage(self.image)
            # create button
            self.button_qrcode = customtkinter.CTkButton(
                self.address_frame, width=28, height=28, text="",
                border_spacing=0,
                image=self.photo_image3,
                bg_color=bg_color, fg_color=bg_color,
                hover_color=bg_color,
            )
            self.button_qrcode.image = self.photo_image3  # keep a reference of image
            self.button_qrcode.grid(row=0, column=4, padx=0, pady=0)

            # Balances field
            self.balance_label = FrameWidgetLabel(master=self, text="Balance:")
            self.balance_label.grid(row=3, column=0, padx=5, pady=0, sticky="w")
            self.balance_value = FrameWidgetLabel(master=self, text="")
            self.balance_value.grid(row=3, column=1, padx=5, pady=0, sticky="w")
            self.balance_value2 = FrameWidgetLabel(master=self, text="")
            self.balance_value2.configure(font=customtkinter.CTkFont(family="Outfit", size=16, weight="normal"))
            self.balance_value2.grid(row=3, column=2, padx=5, pady=0, sticky="w")

        except Exception as e:
            logger.error(f"An unexpected error occurred in init: {e}", exc_info=True)

    def update_frame(
            self,
            status: int,
            blockchain: str,
            address: str,
            url: str,
            balance: str,
            balance2: str
    ):
        logger.debug("FrameWidgetSatodimeCard update_frame")
        status_str = STATUS_DIC.get(status, 'unknown')
        status_color = STATUS_COLOR_DIC.get(status, 'black')
        self.status_value.configure(text=status_str, text_color=status_color)
        self.blockchain_value.configure(text=blockchain)
        self.address_value.configure(text=address)
        self.button_explore.configure(command=lambda: webbrowser.open(url, new=2))
        self.button_copy.configure(command=lambda: pyperclip.copy(address))
        self.balance_value.configure(text=balance)
        self.balance_value2.configure(text=balance2)

        # show address in qr code popup
        self.button_qrcode.configure(
            command=lambda:
            FramePopup(
                self,
                address,
                address,
                "Ok",
                lambda :None,
                './pictures_db/secrets_popup.png',
                qr_msg=address,
            )
        )