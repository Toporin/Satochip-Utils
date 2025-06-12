import customtkinter
import logging

from constants import (HIGHLIGHT_COLOR, BG_MAIN_MENU, DEFAULT_BG_COLOR,
                        BG_HOVER_BUTTON, TEXT_COLOR, BUTTON_TEXT_COLOR)
from frameWidgetHeader import FrameWidgetHeader

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameWidgetScrollableFrame(customtkinter.CTkFrame):
    def __init__(self, master, width, height):
        super().__init__(master)

        logger.debug("FrameWidgetScrollableFrame init")

        try:
            self.width = width
            self.height = height

            # Creating new frame
            self.configure(
                width=width, height=height,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )
            self.pack_propagate(False)  # Prevent the frame from shrinking to fit its contents

            # Create a canvas with specific dimensions
            self.canvas = customtkinter.CTkCanvas(self, bg=DEFAULT_BG_COLOR, highlightthickness=0)
            self.canvas.pack(side="left", fill="both", expand=True)

            # Add a scrollbar to the canvas
            self.scrollbar = customtkinter.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview)
            self.scrollbar.pack(side="right", fill="y")

            # Configure scrollbar colors
            self.scrollbar.configure(
                fg_color=DEFAULT_BG_COLOR,
                button_color=BG_HOVER_BUTTON,
                button_hover_color=BG_HOVER_BUTTON
            )

            # Configure the canvas
            self.canvas.configure(yscrollcommand=self.scrollbar.set)

            # Create a frame inside the canvas
            self.inner_frame = customtkinter.CTkFrame(self.canvas, fg_color=DEFAULT_BG_COLOR)

            # Add that frame to a window in the canvas
            self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

            def _configure_inner_frame(event):
                # Update the scrollregion to encompass the inner frame
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))

                # Resize the inner frame to fit the canvas width
                self.canvas.itemconfig(self.canvas_window, width=self.canvas.winfo_width())

            self.inner_frame.bind("<Configure>", _configure_inner_frame)

            def _configure_canvas(event):
                # Resize the inner frame to fit the canvas width
                self.canvas.itemconfig(self.canvas_window, width=event.width)

            self.canvas.bind("<Configure>", _configure_canvas)

            def _on_mousewheel(event):
                # Check if there's actually something to scroll
                if self.canvas.bbox("all")[3] <= self.canvas.winfo_height():
                    return  # No scrolling needed, so do nothing

                if event.delta > 0:
                    self.canvas.yview_scroll(-1, "units")
                elif event.delta < 0:
                    self.canvas.yview_scroll(1, "units")

            # Bind mouse wheel to the canvas
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        except Exception as e:
            logger.error(f"Init error : {e}", exc_info=True)