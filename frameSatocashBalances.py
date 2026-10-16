from typing import SupportsIndex
import customtkinter
import logging

from constants import BG_MAIN_MENU, DEFAULT_BG_COLOR, BG_HOVER_BUTTON, TEXT_COLOR, BUTTON_TEXT_COLOR, HIGHLIGHT_COLOR
from frameWidgetHeader import FrameWidgetHeader

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameSatocashBalances(customtkinter.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameSatocashBalances init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Creating header
            self.header = FrameWidgetHeader(
                "Balances",
                "cashu.png", # TODO
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")


            # Creating balance table
            # currently only sat info
            # todo: support other units

            # Introduce table
            self.label_text = master.create_label(text="Balances in sat:", frame=self)
            self.label_text.place(relx=0.05, rely=0.15, anchor="nw")

            # Define headers
            self.headers = ["Mint", "Unspent balance", "Spent balance"]
            rely = 0.3
            absx = 33.5

            self.header_widths = [300, 150, 150]  # Define specific widths for each header
            for col, width in zip(self.headers, self.header_widths):
                self.header_button = customtkinter.CTkButton(
                    self, text=col,
                    font=customtkinter.CTkFont(size=14, family='Outfit', weight="bold"),
                    corner_radius=0, state='disabled', text_color='white',
                    fg_color=BG_MAIN_MENU, width=width
                )
                # self.header_button.pack(side="left", expand=True, fill="both")
                # self.header_button.place(relx=0.05, rely=rely, anchor="w")
                self.header_button.place(x=absx, rely=0.23, anchor="nw")
                absx = absx + width + 2

            self.table_frame = master._create_scrollable_frame(
                self, width=600, height=400, x=33.5, y=175
            )

            self.balance_rows = []

            # place frame
            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            error_msg = f"FrameSatocashBalances init: Failed to create frame: {e}"
            logger.error(error_msg, exc_info=True)

    def update_frame(self, mint_urls, amount_unspent_by_mints, amount_spent_by_mints):

        # clear rows
        if len(self.balance_rows)>0:
            for i, row in enumerate(self.balance_rows):
                self.balance_rows[i].destroy()
            self.balance_rows=[]

        # Create rows of labels with alternating colors
        for i, mint_url in enumerate(mint_urls):
            try:

                amount_unspent = amount_unspent_by_mints[i]
                amount_spent = amount_spent_by_mints[i]
                if amount_unspent>0 or amount_spent>0:

                    row_frame = customtkinter.CTkFrame(
                        self.table_frame, width=750,
                        bg_color=DEFAULT_BG_COLOR,
                        fg_color=DEFAULT_BG_COLOR
                    )
                    row_frame.pack(pady=2, fill="x")

                    fg_color = DEFAULT_BG_COLOR if i % 2 == 0 else BG_HOVER_BUTTON
                    text_color = TEXT_COLOR if i % 2 == 0 else BUTTON_TEXT_COLOR

                    values = [mint_url, amount_unspent, amount_spent]
                    for value, width in zip(values, self.header_widths):
                        cell_button = customtkinter.CTkButton(
                            row_frame, text=value,
                            text_color=text_color, fg_color=fg_color,
                            font=customtkinter.CTkFont(size=14, family='Outfit'),
                            hover_color=HIGHLIGHT_COLOR, corner_radius=0, width=width
                        )
                        cell_button.default_color = fg_color  # Store the default color
                        cell_button.pack(side='left', expand=True, fill="both")

                    # add row to list (keep ref to destroy them on card removal)
                    self.balance_rows += [row_frame]
                    logger.debug(f"Row created for mint: {mint_url}")

            except Exception as e:
                logger.error(f"Error creating row for mint {mint_url}: {str(e)}")
