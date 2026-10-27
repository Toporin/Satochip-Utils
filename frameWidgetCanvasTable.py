import tkinter
import tkinter.font
import customtkinter
import logging
from PIL import ImageTk

import constants
from constants import (DEFAULT_BG_COLOR, BG_MAIN_MENU, BG_HOVER_BUTTON,
                       TEXT_COLOR, BUTTON_TEXT_COLOR, HIGHLIGHT_COLOR)
from utils import bind_mousewheel_scrolling

logger = logging.getLogger(__name__)

SCROLLBAR_WIDTH = 20
HEADER_HEIGHT = 28
HEADER_TABLE_GAP = 5


class FrameWidgetCanvasTable(customtkinter.CTkFrame):
    """
        Scrollable table with optional header buttons, drawn as items on a single canvas.

        Creating/mapping one (customtkinter) widget per cell is slow (seconds for a few hundred rows on
        some systems), while canvas items are cheap: the table is fully redrawn on each set_rows() call.

        columns: list of dicts with keys
            - 'title': header text (headers are shown if at least one column has a title)
            - 'width': column width (unscaled)
            - 'anchor': 'center' (default) or 'w' (left aligned)
        set_rows(rows): rows is a list of dicts with keys
            - 'values': one value per column, either text or an image (tkinter or PIL PhotoImage)
            - 'data': (optional) passed to on_row_click when the row is clicked
    """
    def __init__(
            self, master, columns, height,
            font_size=14, row_height=28, row_gap=4, column_gap=2,
            striped=True, on_row_click=None, empty_message=""
    ):
        super().__init__(master)

        self.columns = columns
        self.striped = striped
        self.on_row_click = on_row_click
        self.empty_message = empty_message

        show_headers = any(column.get('title') for column in columns)
        table_width = sum(column['width'] for column in columns) + column_gap * (len(columns) - 1)
        body_y = HEADER_HEIGHT + HEADER_TABLE_GAP if show_headers else 0
        self.configure(
            width=table_width + SCROLLBAR_WIDTH, height=body_y + height, corner_radius=0,
            fg_color=DEFAULT_BG_COLOR, bg_color=DEFAULT_BG_COLOR
        )

        # headers
        if show_headers:
            header_font = customtkinter.CTkFont(size=14, family=constants.FONT_FAMILY, weight="bold")
            x = 0
            for column in columns:
                header_button = customtkinter.CTkButton(
                    self, text=column.get('title', ""), font=header_font,
                    corner_radius=0, state='disabled', text_color='white',
                    fg_color=BG_MAIN_MENU, width=column['width'], height=HEADER_HEIGHT
                )
                header_button.place(x=x, y=0, anchor="nw")
                x += column['width'] + column_gap

        # table body: canvas + scrollbar (the body frame applies customtkinter scaling to its size & position)
        self.body = customtkinter.CTkFrame(
            self, width=table_width + SCROLLBAR_WIDTH, height=height, corner_radius=0,
            fg_color=DEFAULT_BG_COLOR, bg_color=DEFAULT_BG_COLOR
        )
        self.body.place(x=0, y=body_y)
        self.body.pack_propagate(False)
        self.canvas = customtkinter.CTkCanvas(self.body, bg=DEFAULT_BG_COLOR, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar = customtkinter.CTkScrollbar(
            self.body, orientation="vertical", command=self.canvas.yview,
            fg_color=DEFAULT_BG_COLOR, button_color=BG_HOVER_BUTTON, button_hover_color=BG_HOVER_BUTTON
        )
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        bind_mousewheel_scrolling(self.body, self.canvas)

        # row interactions: the row under the pointer is computed from the pointer position
        self.canvas.bind("<Motion>", self._on_mouse_motion)
        self.canvas.bind("<Leave>", lambda _: self._set_hovered_row(None))
        self.canvas.bind("<Button-1>", self._on_click)
        self._hovered_row = None

        # scaled geometry & font for canvas drawing (canvas items are not scaled by customtkinter)
        scaling = customtkinter.ScalingTracker.get_widget_scaling(self.body)
        self._column_widths = [round(column['width'] * scaling) for column in columns]
        self._column_gap = round(column_gap * scaling)
        self._row_height = round(row_height * scaling)
        self._row_pitch = self._row_height + round(row_gap * scaling)
        self._table_width = sum(self._column_widths) + self._column_gap * (len(columns) - 1)
        self._text_padding = round(8 * scaling)
        self.font = tkinter.font.Font(family=constants.FONT_FAMILY, size=-round(font_size * scaling))
        # measuring text is slow (a few ms per call on some systems): bound & cache measures
        self._wide_char_width = self.font.measure("W")
        self._digit_width = self.font.measure("0")
        self._fit_text_cache = {}

        self.rows = []
        self._draw_rows()

    def set_rows(self, rows):
        # replace table content
        self.rows = rows
        self._draw_rows()

    def _get_row_colors(self, index):
        # (background, text) colors, alternating if striped
        if not self.striped or index % 2 == 0:
            return DEFAULT_BG_COLOR, TEXT_COLOR
        return BG_HOVER_BUTTON, BUTTON_TEXT_COLOR

    def _draw_rows(self):
        canvas = self.canvas
        canvas.delete("all")
        self._hovered_row = None
        canvas.configure(cursor="")

        for index, row in enumerate(self.rows):
            fg_color, text_color = self._get_row_colors(index)
            y0 = index * self._row_pitch + (self._row_pitch - self._row_height) // 2
            y1 = y0 + self._row_height
            y_middle = (y0 + y1) / 2
            x0 = 0
            for value, column, width in zip(row['values'], self.columns, self._column_widths):
                canvas.create_rectangle(x0, y0, x0 + width, y1, fill=fg_color, outline="", tags=f"bg{index}")
                left_aligned = column.get('anchor') == "w"
                x_text = x0 + self._text_padding if left_aligned else x0 + width / 2
                anchor = "w" if left_aligned else "center"
                if isinstance(value, (tkinter.PhotoImage, ImageTk.PhotoImage)):
                    canvas.create_image(x_text, y_middle, image=value, anchor=anchor)
                elif value is not None:
                    text = self._fit_text(str(value), width - 2 * self._text_padding)
                    canvas.create_text(x_text, y_middle, text=text, fill=text_color, font=self.font, anchor=anchor)
                x0 += width + self._column_gap

        if not self.rows and self.empty_message:
            canvas.create_text(
                self._table_width / 2, 3 * self._row_height,
                text=self.empty_message, fill=TEXT_COLOR, font=self.font
            )

        canvas.configure(scrollregion=(0, 0, self._table_width, len(self.rows) * self._row_pitch))
        # go back to the top of the list, as the previous position may be out of range
        canvas.yview_moveto(0)

    def _fit_text(self, text: str, max_width: int) -> str:
        # shorten text with an ellipsis so that it fits in max_width pixels
        char_width = self._digit_width if text.isdigit() else self._wide_char_width
        if len(text) * char_width <= max_width:
            return text  # short text fits for sure, no need to measure it
        key = (text, max_width)
        if key not in self._fit_text_cache:
            self._fit_text_cache[key] = self._shorten_text(text, max_width)
        return self._fit_text_cache[key]

    def _shorten_text(self, text: str, max_width: int) -> str:
        if self.font.measure(text) <= max_width:
            return text
        low, high = 0, len(text)
        while low < high:
            middle = (low + high + 1) // 2
            if self.font.measure(text[:middle] + "…") <= max_width:
                low = middle
            else:
                high = middle - 1
        return text[:low] + "…"

    def _get_row_index_at(self, x, y):
        # index of the row at canvas widget coordinates (x, y), or None
        canvas_y = self.canvas.canvasy(y)
        if x < 0 or x > self._table_width or canvas_y < 0:
            return None
        index = int(canvas_y // self._row_pitch)
        return index if index < len(self.rows) else None

    def _is_clickable(self, index):
        return self.on_row_click is not None and self.rows[index].get('data') is not None

    def _set_hovered_row(self, index):
        # highlight the row under the pointer
        if index == self._hovered_row:
            return
        if self._hovered_row is not None:
            self.canvas.itemconfigure(f"bg{self._hovered_row}", fill=self._get_row_colors(self._hovered_row)[0])
        if index is not None:
            self.canvas.itemconfigure(f"bg{index}", fill=HIGHLIGHT_COLOR)
        self.canvas.configure(cursor="hand2" if index is not None and self._is_clickable(index) else "")
        self._hovered_row = index

    def _on_mouse_motion(self, event):
        self._set_hovered_row(self._get_row_index_at(event.x, event.y))

    def _on_click(self, event):
        index = self._get_row_index_at(event.x, event.y)
        if index is not None and self._is_clickable(index):
            self.on_row_click(self.rows[index]['data'])
