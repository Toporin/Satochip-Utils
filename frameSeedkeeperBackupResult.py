import customtkinter
import logging

from frameWidgetCanvasTable import FrameWidgetCanvasTable
from frameWidgetHeader import FrameWidgetHeader

logger = logging.getLogger(__name__)

class FrameSeedkeeperBackupResult(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameSeedkeeperBackupResult init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Creating header
            self.header = FrameWidgetHeader(
                "Backup your seedkeeper", "backup_card_icon.png",
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            # labels
            # labels
            self.label_step = master.create_label("backup result", frame=self)
            self.label_step.configure(font=master.make_text_bold())
            self.label_step.place(relx=0.05, rely=0.15, anchor="nw")

            self.label_description = master.create_label("details", frame=self)
            self.label_description.configure(justify="left")
            self.label_description.place(relx=0.05, rely=0.21, anchor="nw")

            # Backup logs table
            self.table = FrameWidgetCanvasTable(
                self,
                [
                    {'title': "ID", 'width': 50},
                    {'title': "label", 'width': 309},
                    {'title': "Result", 'width': 309},
                ],
                height=360
            )
            self.table.place(x=30, y=180)

            # place frame
            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"Init error : {e}", exc_info=True)

    def update_frame(self, is_backup_error, backup_logs):

        # update label
        if is_backup_error:
            self.label_step.configure(text="There were some issues during backup")
            self.label_description.configure(
                text="Some or all secrets may not have been saved on your backup card."
                     "\nHere is a list of issues encountered:")
        else:
            self.label_step.configure(text="Backup terminated successfully!")
            self.label_description.configure(
                text="Your secrets have been successfully saved on your backup card!"
                     f"\n{len(backup_logs)} secrets have been saved."
            )

        # populate table with logs
        self.table.set_rows([
            {'values': [log['id'], log['label'], log['msg']]}
            for log in backup_logs
        ])
        logger.debug(f"Table updated with {len(backup_logs)} backup logs")
