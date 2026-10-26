import customtkinter
import logging

import constants
from constants import (DEFAULT_BG_COLOR, TYPE_MASTERSEED, TYPE_DIC,
                       TYPE_BIP39_MNEMONIC, TYPE_ELECTRUM_MNEMONIC, TYPE_PASSWORD, TYPE_DESCRIPTOR, TYPE_DATA)
from frameWidgetCanvasTable import FrameWidgetCanvasTable
from frameWidgetHeader import FrameWidgetHeader

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

TABLE_X = 33.5
TABLE_COLUMNS = [
    {'title': "Id", 'width': 50},
    {'title': "Type of secret", 'width': 200},
    {'title': "Label", 'width': 350},
]
TABLE_WIDTH = sum(column['width'] for column in TABLE_COLUMNS) + 2 * (len(TABLE_COLUMNS) - 1)


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

            # Secrets table
            self.table = FrameWidgetCanvasTable(
                self, TABLE_COLUMNS, height=375,
                on_row_click=lambda secret: self.master.show_seedkeeper_secret(secret)
            )
            self.table.place(x=TABLE_X, y=172)

            # all rows: dicts with 'data' (secret header), 'values' (cells), 'category' & 'label' (for filtering)
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
            label = str(secret.get('label', ""))
            self.secret_rows.append({
                'data': secret,
                'values': [str(secret['id']), get_secret_type_name(secret), label],
                'category': get_secret_category(secret),
                'label': label.lower(),
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
        self.table.empty_message = (
            "No secret matches the search." if self.secret_rows else "No secret stored on the card."
        )
        self.table.set_rows(visible_rows)
