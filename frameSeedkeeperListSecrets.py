import tkinter.font
import customtkinter
import logging

import constants
from constants import (DEFAULT_BG_COLOR, BG_MAIN_MENU, BG_HOVER_BUTTON,
                       TEXT_COLOR, BUTTON_TEXT_COLOR, HIGHLIGHT_COLOR, TYPE_MASTERSEED, TYPE_DIC,
                       TYPE_BIP39_MNEMONIC, TYPE_ELECTRUM_MNEMONIC, TYPE_PASSWORD, TYPE_DESCRIPTOR, TYPE_DATA)
from frameWidgetHeader import FrameWidgetHeader
from utils import bind_mousewheel_scrolling

logger = logging.getLogger(__name__)

# Filter options of the type dropdown, and the secret types they match ('All' matches every type)
FILTER_ALL = "All"
FILTER_TYPES = {
    "Mnemonic": {TYPE_BIP39_MNEMONIC, TYPE_ELECTRUM_MNEMONIC},  # + masterseed with mnemonic subtype
    "Password": {TYPE_PASSWORD, 0x91},  # password & master password
    "Descriptors": {TYPE_DESCRIPTOR},
    "Data": {TYPE_DATA},
}
# delay before filtering after a keystroke in the search field, to coalesce fast typing
SEARCH_DEBOUNCE_MS = 150

# table geometry (unscaled): column widths, gap between columns, row height and gap between rows
COLUMN_WIDTHS = [50, 200, 350]
COLUMN_GAP = 2
ROW_HEIGHT = 28
ROW_GAP = 4
TABLE_X = 33.5
TABLE_WIDTH = sum(COLUMN_WIDTHS) + COLUMN_GAP * (len(COLUMN_WIDTHS) - 1)


def get_secret_category(secret) -> str:
    # return the filter option matching the secret type (None if only matched by 'All')
    if secret['type'] == TYPE_MASTERSEED and secret.get('subtype') == 0x01:
        return "Mnemonic"
    for category, types in FILTER_TYPES.items():
        if secret['type'] in types:
            return category
    return None


def get_secret_type_name(secret) -> str:
    if secret['type'] == TYPE_MASTERSEED and secret.get('subtype') == 0x01:
        return "Mnemonic"
    return TYPE_DIC.get(secret['type'], "Unknown type")


class FrameSeedkeeperListSecrets(customtkinter.CTkFrame):
    """
         This class manages to:
             - Show a list of all secrets stored on the card.
             - Filter the list by secret type and label (search field).
             - Select and display details about each secret from the list.

         The table is drawn as items on a single canvas instead of one widget per cell:
         creating/mapping (customtkinter) widgets is slow, while canvas items are cheap,
         so the list can be redrawn instantly on each filter change, whatever the number of secrets.
    """
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameSeedkeeperListSecrets init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Creating header
            self.header = FrameWidgetHeader(
                "My secrets",
                "password_icon.png",
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            # Introduce table
            self.label_text = master.create_label(text="Click on a secret to manage it:", frame=self)
            self.label_text.place(relx=0.05, rely=0.15, anchor="nw")

            # Search & filter row, centered above the table
            self.search_frame = customtkinter.CTkFrame(self, fg_color=DEFAULT_BG_COLOR, bg_color=DEFAULT_BG_COLOR)
            self.search_frame.place(x=TABLE_X + TABLE_WIDTH / 2, y=126, anchor="n")
            self.search_label = master.create_label("Search:", frame=self.search_frame)
            self.search_label.pack(side="left", padx=(0, 10))
            self.search_var = customtkinter.StringVar(value="")
            self.search_entry = customtkinter.CTkEntry(
                self.search_frame, width=280, height=32, corner_radius=10,
                fg_color=constants.BUTTON_COLOR, border_color=constants.BUTTON_COLOR, text_color='grey',
                textvariable=self.search_var
            )
            self.search_entry.pack(side="left", padx=(0, 10))
            self.type_var, self.type_menu = master.create_option_list(
                self.search_frame, [FILTER_ALL] + list(FILTER_TYPES), width=150
            )
            self.type_menu.configure(command=lambda _: self.apply_filter())
            self.type_menu.pack(side="left")
            self._search_after_id = None
            self.search_var.trace_add("write", lambda *_: self._schedule_filter())

            # Create header labels
            absx = TABLE_X
            for col, width in zip(["Id", "Type of secret", "Label"], COLUMN_WIDTHS):
                header_button = customtkinter.CTkButton(
                    self, text=col,
                    font=customtkinter.CTkFont(size=14, family=constants.FONT_FAMILY, weight="bold"),
                    corner_radius=0, state='disabled', text_color='white',
                    fg_color=BG_MAIN_MENU, width=width
                )
                header_button.place(x=absx, y=172, anchor="nw")
                absx = absx + width + COLUMN_GAP

            # Table: canvas + scrollbar (the container applies customtkinter scaling to its size & position)
            self.table_container = customtkinter.CTkFrame(
                self, width=TABLE_WIDTH + 20, height=375, corner_radius=0,
                fg_color=DEFAULT_BG_COLOR, bg_color=DEFAULT_BG_COLOR
            )
            self.table_container.place(x=TABLE_X, y=205)
            self.table_container.pack_propagate(False)
            self.table_canvas = customtkinter.CTkCanvas(
                self.table_container, bg=DEFAULT_BG_COLOR, highlightthickness=0
            )
            self.table_canvas.pack(side="left", fill="both", expand=True)
            self.table_scrollbar = customtkinter.CTkScrollbar(
                self.table_container, orientation="vertical", command=self.table_canvas.yview,
                fg_color=DEFAULT_BG_COLOR, button_color=BG_HOVER_BUTTON, button_hover_color=BG_HOVER_BUTTON
            )
            self.table_scrollbar.pack(side="right", fill="y")
            self.table_canvas.configure(yscrollcommand=self.table_scrollbar.set)
            bind_mousewheel_scrolling(self.table_container, self.table_canvas)

            # row interactions: the row under the pointer is computed from the pointer position
            self.table_canvas.bind("<Motion>", self._on_mouse_motion)
            self.table_canvas.bind("<Leave>", lambda _: self._set_hovered_row(None))
            self.table_canvas.bind("<Button-1>", self._on_click)
            self._hovered_row = None

            # scaled geometry & font for canvas drawing (canvas items are not scaled by customtkinter)
            scaling = customtkinter.ScalingTracker.get_widget_scaling(self.table_container)
            self._column_widths = [round(w * scaling) for w in COLUMN_WIDTHS]
            self._column_gap = round(COLUMN_GAP * scaling)
            self._row_height = round(ROW_HEIGHT * scaling)
            self._row_pitch = self._row_height + round(ROW_GAP * scaling)
            self._table_width = sum(self._column_widths) + self._column_gap * (len(self._column_widths) - 1)
            self._text_padding = round(8 * scaling)
            self.row_font = tkinter.font.Font(family=constants.FONT_FAMILY, size=-round(14 * scaling))
            # measuring text is slow (a few ms per call on some systems): bound & cache measures
            self._wide_char_width = self.row_font.measure("W")
            self._fit_text_cache = {}

            # all rows: dicts with 'secret', 'category', 'label' (lowercase, for search) & 'values' (cell texts)
            self.secret_rows = []
            # rows currently displayed (filtered), in display order
            self.visible_rows = []

            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            error_msg = f"FrameSeedkeeperListSecrets init: Failed to create secrets frame: {e}"
            logger.error(error_msg, exc_info=True)

    def update_frame(self, secret_headers):
        self.secret_rows = []
        for secret in secret_headers:
            values = [str(secret['id']), get_secret_type_name(secret), str(secret.get('label', ""))]
            self.secret_rows.append({
                'secret': secret,
                'category': get_secret_category(secret),
                'label': values[2].lower(),
                # cell texts: type & label shortened with an ellipsis to fit their column (ids always fit)
                'values': [values[0]] + [self._fit_text(value, width - 2 * self._text_padding)
                                         for value, width in zip(values[1:], self._column_widths[1:])],
            })
        logger.debug(f"Rows created for {len(self.secret_rows)} secrets")

        self.apply_filter(force=True)

        # update status flag
        # todo detect changes in secret_headers to update list when needed
        self.master.seedkeeper_secret_headers_need_update = False

    def _schedule_filter(self):
        # debounce: filter once the user pauses typing
        if self._search_after_id is not None:
            self.after_cancel(self._search_after_id)
        self._search_after_id = self.after(SEARCH_DEBOUNCE_MS, self.apply_filter)

    def apply_filter(self, force=False):
        # show only rows matching the selected type and containing the search text in their label
        self._search_after_id = None
        search_text = self.search_var.get().strip().lower()
        category = self.type_var.get()
        visible_rows = [
            row for row in self.secret_rows
            if (category == FILTER_ALL or row['category'] == category) and search_text in row['label']
        ]
        if not force and visible_rows == self.visible_rows:
            return  # nothing changed, avoid useless redraw
        self.visible_rows = visible_rows
        self._draw_rows()

    def _get_row_colors(self, index):
        # alternating colors: (background, text)
        if index % 2 == 0:
            return DEFAULT_BG_COLOR, TEXT_COLOR
        return BG_HOVER_BUTTON, BUTTON_TEXT_COLOR

    def _draw_rows(self):
        canvas = self.table_canvas
        canvas.delete("all")
        self._hovered_row = None
        canvas.configure(cursor="")

        for index, row in enumerate(self.visible_rows):
            fg_color, text_color = self._get_row_colors(index)
            y0 = index * self._row_pitch + (self._row_pitch - self._row_height) // 2
            y1 = y0 + self._row_height
            x0 = 0
            for value, width in zip(row['values'], self._column_widths):
                canvas.create_rectangle(x0, y0, x0 + width, y1, fill=fg_color, outline="", tags=f"bg{index}")
                canvas.create_text(
                    x0 + width / 2, (y0 + y1) / 2, text=value, fill=text_color, font=self.row_font
                )
                x0 += width + self._column_gap

        if not self.visible_rows:
            message = "No secret matches the search." if self.secret_rows else "No secret stored on the card."
            canvas.create_text(
                self._table_width / 2, 3 * self._row_height, text=message, fill=TEXT_COLOR, font=self.row_font
            )

        canvas.configure(scrollregion=(0, 0, self._table_width, len(self.visible_rows) * self._row_pitch))
        # go back to the top of the list, as the previous position may be out of range
        canvas.yview_moveto(0)

    def _fit_text(self, text: str, max_width: int) -> str:
        # shorten text with an ellipsis so that it fits in max_width pixels
        if len(text) * self._wide_char_width <= max_width:
            return text  # short text fits for sure, no need to measure it
        key = (text, max_width)
        if key not in self._fit_text_cache:
            self._fit_text_cache[key] = self._shorten_text(text, max_width)
        return self._fit_text_cache[key]

    def _shorten_text(self, text: str, max_width: int) -> str:
        if self.row_font.measure(text) <= max_width:
            return text
        low, high = 0, len(text)
        while low < high:
            middle = (low + high + 1) // 2
            if self.row_font.measure(text[:middle] + "…") <= max_width:
                low = middle
            else:
                high = middle - 1
        return text[:low] + "…"

    def _get_row_index_at(self, x, y):
        # index of the visible row at widget coordinates (x, y), or None
        canvas_y = self.table_canvas.canvasy(y)
        if x < 0 or x > self._table_width or canvas_y < 0:
            return None
        index = int(canvas_y // self._row_pitch)
        return index if index < len(self.visible_rows) else None

    def _set_hovered_row(self, index):
        # highlight the row under the pointer
        if index == self._hovered_row:
            return
        if self._hovered_row is not None:
            self.table_canvas.itemconfigure(f"bg{self._hovered_row}", fill=self._get_row_colors(self._hovered_row)[0])
        if index is not None:
            self.table_canvas.itemconfigure(f"bg{index}", fill=HIGHLIGHT_COLOR)
        self.table_canvas.configure(cursor="hand2" if index is not None else "")
        self._hovered_row = index

    def _on_mouse_motion(self, event):
        self._set_hovered_row(self._get_row_index_at(event.x, event.y))

    def _on_click(self, event):
        index = self._get_row_index_at(event.x, event.y)
        if index is not None:
            self.master.show_seedkeeper_secret(self.visible_rows[index]['secret'])
