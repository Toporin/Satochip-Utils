import customtkinter
import logging

from frameWidgetCanvasTable import FrameWidgetCanvasTable
from frameWidgetHeader import FrameWidgetHeader

logger = logging.getLogger(__name__)


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

            # Balances table
            self.table = FrameWidgetCanvasTable(
                self,
                [
                    {'title': "Mint", 'width': 300},
                    {'title': "Unspent balance", 'width': 150},
                    {'title': "Spent balance", 'width': 150},
                ],
                height=400
            )
            self.table.place(x=33.5, y=138)

            # place frame
            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            error_msg = f"FrameSatocashBalances init: Failed to create frame: {e}"
            logger.error(error_msg, exc_info=True)

    def update_frame(self, mint_urls, amount_unspent_by_mints, amount_spent_by_mints):
        # populate table with mints having a non-zero balance
        rows = []
        for i, mint_url in enumerate(mint_urls):
            try:
                amount_unspent = amount_unspent_by_mints[i]
                amount_spent = amount_spent_by_mints[i]
                if amount_unspent > 0 or amount_spent > 0:
                    rows.append({'values': [mint_url, amount_unspent, amount_spent]})
            except Exception as e:
                logger.error(f"Error creating row for mint {mint_url}: {str(e)}")
        self.table.set_rows(rows)
        logger.debug(f"Table updated with {len(rows)} mints")
