import customtkinter
import logging

from frameWidgetCanvasTable import FrameWidgetCanvasTable
from frameWidgetHeader import FrameWidgetHeader

logger = logging.getLogger(__name__)


class FrameSeedkeeperCardLogs(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameSeedkeeperCardLogs init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Creating header
            self.header = FrameWidgetHeader(
                "Card logs", "logs_icon_black.png",
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            self.label_text = master.create_label(
                text="Here is a list of the last operations performed on your card:",
                frame=self
            )
            self.label_text.place(relx=0.05, rely=0.15, anchor="nw")

            # Logs table
            self.table = FrameWidgetCanvasTable(
                self,
                [
                    {'title': "Operation", 'width': 260},
                    {'title': "ID1", 'width': 70},
                    {'title': "ID2", 'width': 70},
                    {'title': "Result", 'width': 262},
                ],
                height=400, empty_message="No log available."
            )
            self.table.place(x=30, y=138)

            # place frame
            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"Init error : {e}", exc_info=True)

    def update_frame(self, logs):
        # populate table with logs
        self.table.set_rows([
            {'values': [log['Operation'], log['ID1'], log['ID2'], log['Result']]}
            for log in logs
        ])
        logger.debug(f"Table updated with {len(logs)} logs")
