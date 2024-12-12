import customtkinter
import logging

from constants import (HIGHLIGHT_COLOR, BG_MAIN_MENU, DEFAULT_BG_COLOR,
                        BG_HOVER_BUTTON, TEXT_COLOR, BUTTON_TEXT_COLOR)
from frameWidgetHeader import FrameWidgetHeader

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
                "Backup your seedkeeper", "seed_popup.jpg",
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

            # Table header
            self.headers = ['ID', 'label', 'Result']
            self.header_widths = [50, 325, 325]

            self.header_frame = customtkinter.CTkFrame(
                self, width=700, bg_color=DEFAULT_BG_COLOR,
                corner_radius=0, fg_color=DEFAULT_BG_COLOR
            )
            self.header_frame.place(relx=0.04, rely=0.30, relwidth=0.9, anchor="nw")

            for col, width in zip(self.headers, self.header_widths):
                header_button = customtkinter.CTkButton(
                    self.header_frame, text=col,
                    font=customtkinter.CTkFont(size=14, family='Outfit', weight="bold"),
                    corner_radius=0, state='disabled', text_color='white',
                    fg_color=BG_MAIN_MENU, width=width
                )
                header_button.pack(side="left", expand=True, fill="both")

            # table content
            self.table_frame = master._create_scrollable_frame(
                self, width=700, height=400, x=30, y=210
            )
            self.log_rows = []

            # place frame
            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"Init error : {e}", exc_info=True)

    def update_frame(self, is_backup_error, backup_logs):

        # clear existing logs if needed
        if len(self.log_rows) > 0:
            for i, row in enumerate(self.log_rows):
                self.log_rows[i].destroy()
            self.log_rows = []

        def _on_mouse_on_log(event, button):
            button.configure(fg_color=HIGHLIGHT_COLOR, cursor="hand2")

        def _on_mouse_out_log(event, button):
            button.configure(fg_color=button.default_color)

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
        for i, log in enumerate(backup_logs):
            row_frame = customtkinter.CTkFrame(
                self.table_frame, width=750,
                bg_color=DEFAULT_BG_COLOR, fg_color=DEFAULT_BG_COLOR
            )
            row_frame.pack(pady=2, fill="x")

            fg_color = DEFAULT_BG_COLOR if i % 2 == 0 else BG_HOVER_BUTTON
            text_color = TEXT_COLOR if i % 2 == 0 else BUTTON_TEXT_COLOR

            values = [log['id'], log['label'], log['msg']]
            for value, width in zip(values, self.header_widths):
                cell_button = customtkinter.CTkButton(
                    row_frame, text=value, text_color=text_color,
                    fg_color=fg_color,
                    font=customtkinter.CTkFont(size=14, family='Outfit'),
                    hover_color=HIGHLIGHT_COLOR, width=width, corner_radius=0
                )
                cell_button.default_color = fg_color
                cell_button.pack(side='left', expand=True, fill="both")
                cell_button.bind("<Enter>", lambda event, btn=cell_button: _on_mouse_on_log(event, btn))
                cell_button.bind("<Leave>", lambda event, btn=cell_button: _on_mouse_out_log(event, btn))

            # add row to list (keep ref to destroy them on card removal)
            self.log_rows += [row_frame]

            logger.debug(
                f"Row created for log: {log['id'], log['label'], log['msg']}")
