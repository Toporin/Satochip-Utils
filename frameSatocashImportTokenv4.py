import customtkinter
import logging

from frameWidgetHeader import FrameWidgetHeader
from constants import BG_BUTTON
from utils import update_textbox

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameSatocashImportTokenv4(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameSatocashImportTokenv4 init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Creating header
            self.header = FrameWidgetHeader(
                f"Import tokenv4", "cashu.png",
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            # secret textbox
            self.token_label = master.create_label(f"Token v4:", frame=self)
            self.token_label.place(relx=0.05, rely=0.30, anchor="nw")

            self.token_textbox = customtkinter.CTkTextbox(
                self, corner_radius=20, bg_color="whitesmoke", fg_color=BG_BUTTON,
                border_color=BG_BUTTON, border_width=1, width=500, height=200,
                text_color="grey",
                font=customtkinter.CTkFont(family="Outfit", size=13, weight="normal")
            )
            self.token_textbox.place(relx=0.15, rely=0.36, anchor="nw")

            # action buttons
            # token import to card
            def _save_secret_to_card():
                try:
                    logger.info(f"Saving tokenv4 to card")

                    tokenv4 = self.token_textbox.get("1.0", "end").strip()

                    if tokenv4:

                        # verify PIN
                        master.update_verify_pin()

                        # import
                        mint_url, unit_str, amount_total = master.controller.satocash_import_tokenv4(tokenv4)

                        master.show(
                            "SUCCESS",
                            f"Token v4 imported successfully with {amount_total} {unit_str} \nMint: {mint_url}",
                            "Ok",
                            None,
                            "./pictures_db/success_popup_green.png"
                        )
                    else:
                        raise ValueError("No tokenv4 provided")

                except Exception as ex:
                    logger.error(f"Failed to save tokenv4 to card: {ex}", exc_info=True)
                    master.show(
                        "ERROR",
                        f"Failed to import tokenv4: \n{ex}",
                        "Ok", None,
                        "./pictures_db/error_popup_red.png"
                    )

            self.save_button = master.create_button(
                "Import to card",
                command=_save_secret_to_card,
                frame=self
            )
            self.save_button.place(relx=0.85, rely=0.95, anchor="center")

            # back button
            self.back_button = master.create_button(
                "Back",
                command=master.show_satocash_import_tokenv4,
                frame=self
            )
            self.back_button.place(relx=0.65, rely=0.95, anchor="center")

            # place frame
            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"Init error : {e}", exc_info=True)

    def update_frame(self):
        update_textbox(self.token_textbox, "")
