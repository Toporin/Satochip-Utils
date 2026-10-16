import customtkinter
import logging

from frameWidgetHeader import FrameWidgetHeader
from constants import BG_BUTTON
from utils import update_textbox

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameSatocashExportTokenv4(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameSatocashExportTokenv4 init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Creating header
            self.header = FrameWidgetHeader(
                f"Export token v4", "cashu.png",
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            # unit dropdown
            self.unit_label = master.create_label("Choose unit: ", frame=self)
            self.unit_label.place(relx=0.05, rely=0.2, anchor="w")

            self.unit_value, self.unit_menu = master.create_option_list(
                self,
                ["sat", "msat", "USD", "EUR"],
                width=200
            )
            self.unit_menu.place(relx=0.25, rely=0.2, anchor="w")

            # label
            self.amount_label = master.create_label("Amount:", frame=self)
            self.amount_label.place(relx=0.05, rely=0.3, anchor="nw")

            self.amount_entry = master.create_entry(frame=self)
            self.amount_entry.configure(width=200)
            self.amount_entry.configure(placeholder_text="Enter amount")
            self.amount_entry.place(relx=0.25, rely=0.3, anchor="nw")

            # token textbox
            self.token_label = master.create_label(f"Token v4:", frame=self)
            #self.token_label.place(relx=0.05, rely=0.30, anchor="nw")

            self.token_textbox = customtkinter.CTkTextbox(
                self, corner_radius=20, bg_color="whitesmoke", fg_color=BG_BUTTON,
                border_color=BG_BUTTON, border_width=1, width=500, height=300,
                text_color="grey",
                font=customtkinter.CTkFont(family="Outfit", size=13, weight="normal")
            )
            #self.token_textbox.place(relx=0.15, rely=0.36, anchor="nw")

            # action buttons
            # token import to card
            def _export_token_from_card():
                try:
                    logger.info(f"Exporting tokenv4 from card")

                    amount = int(self.amount_entry.get())
                    unit_str = self.unit_value.get()

                    # verify PIN
                    master.update_verify_pin()

                    # export
                    tokenv4_str, mint_url, unit, amount_exported, error_msg = master.controller.satocash_export_tokenv4(unit_str, amount)

                    # update token textbox
                    txt = tokenv4_str + "\n" + error_msg
                    self.token_label.place(relx=0.05, rely=0.4)
                    self.token_textbox.place(relx=0.15, rely=0.46, relheight=0.20, )
                    update_textbox(self.token_textbox, txt)

                    if error_msg == "" :
                        master.show(
                            "SUCCESS",
                            f"Token v4 exported successfully with {amount_exported} {unit_str} \nMint: {mint_url}",
                            "Ok",
                            None,
                            "./pictures_db/success_popup_green.png"
                        )
                    else:
                        master.show(
                            "ERROR",
                            f"Failed to export tokenv4",
                            "Ok", None,
                            "./pictures_db/error_popup_red.png"
                        )


                except Exception as ex:
                    logger.error(f"Failed to export tokenv4 from card: {ex}", exc_info=True)
                    master.show(
                        "ERROR",
                        f"Failed to export tokenv4: \n{ex}",
                        "Ok", None,
                        "./pictures_db/error_popup_red.png"
                    )

            self.save_button = master.create_button(
                "Export from card",
                command=_export_token_from_card,
                frame=self
            )
            self.save_button.place(relx=0.85, rely=0.95, anchor="center")

            # back button
            self.back_button = master.create_button(
                "Back",
                command=master.show_satocash_export_tokenv4,
                frame=self
            )
            self.back_button.place(relx=0.65, rely=0.95, anchor="center")

            # place frame
            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"Init error : {e}", exc_info=True)



