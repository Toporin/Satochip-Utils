import customtkinter
import logging

import constants
from constants import NDEF_PREDEFINED_LIST, NDEF_POLICY_DISABLED, NDEF_POLICY_STATIC, NDEF_POLICY_DYNAMIC
from frameWidgetHeader import FrameWidgetHeader
from utils import ndef_encode_url, ndef_encode_aar, ndef_parse_raw

logger = logging.getLogger(__name__)

# NDEF configuration options: (value, text)
NDEF_OPTION_DISABLE = "disable"
NDEF_OPTION_URL = "url"
NDEF_OPTION_APP = "app"
NDEF_OPTION_PREDEFINED = "predefined"
NDEF_OPTION_DYNAMIC = "dynamic"
NDEF_OPTION_RAW = "raw"
NDEF_OPTIONS = [
    (NDEF_OPTION_DISABLE, "Disable NDEF"),
    (NDEF_OPTION_URL, "Set URL"),
    (NDEF_OPTION_APP, "Set Android app"),
    (NDEF_OPTION_PREDEFINED, "Predefined list"),
    (NDEF_OPTION_DYNAMIC, "Dynamic NDEF"),
    (NDEF_OPTION_RAW, "RAW (advanced)"),
]

URL_PLACEHOLDER = "(enter URL here)"
APP_PLACEHOLDER = "(enter your Android Application Record name here, e.g. io.hexawallet.bitcoinkeeper)"
RAW_PLACEHOLDER = "(enter raw hex NDEF encoding here)"


class FrameCardConfigureNdef(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameCardConfigureNdef init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Creating header
            self.header = FrameWidgetHeader(
                "Configure NDEF",
                "icon_nfc.png",
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            # setup paragraph
            self.text1 = master.create_label(
                f"Configure the NDEF message of your {master.controller.cc.card_type}.",
                frame=self
            )
            self.text1.place(relx=0.05, rely=0.17, anchor="w")

            self.text2 = master.create_label(
                "When the card is tapped on a smartphone, the NDEF message can",
                frame=self
            )
            self.text2.place(relx=0.05, rely=0.22, anchor="w")

            self.text3 = master.create_label(
                "open a website or launch an app.",
                frame=self
            )
            self.text3.place(relx=0.05, rely=0.27, anchor="w")

            # NDEF option selection
            self.option_label = master.create_label("NDEF configuration:", frame=self)
            self.option_label.configure(font=master.make_text_bold())
            self.option_label.place(relx=0.05, rely=0.35, anchor="w")

            self.option_radio_value = customtkinter.StringVar(value=NDEF_OPTION_DISABLE)
            self.option_radio_buttons = {}
            for value, text in NDEF_OPTIONS:
                self.option_radio_buttons[value] = self._create_radio_button(
                    text, self.option_radio_value, value, self.update_option_selection
                )
            # radio buttons are placed in update_frame() as available options depend on the card

            # option specific widgets (placed in update_option_selection())
            self.option_text = master.create_label("", frame=self)

            self.url_label = master.create_label("URL:", frame=self)
            self.url_entry = master.create_entry(frame=self)
            self.url_entry.configure(placeholder_text=URL_PLACEHOLDER)

            self.app_label = master.create_label("App:", frame=self)
            self.app_entry = master.create_entry(frame=self)
            self.app_entry.configure(placeholder_text=APP_PLACEHOLDER)

            self.raw_label = master.create_label("Raw NDEF:", frame=self)
            self.raw_entry = master.create_entry(frame=self)
            self.raw_entry.configure(placeholder_text=RAW_PLACEHOLDER)

            self.predefined_radio_value = customtkinter.StringVar(value="0")
            self.predefined_radio_buttons = []
            for index, (name, ndef_type, ndef_value) in enumerate(NDEF_PREDEFINED_LIST):
                self.predefined_radio_buttons.append(
                    self._create_radio_button(name, self.predefined_radio_value, str(index))
                )

            # Creating cancel and apply buttons
            self.cancel_button = master.create_button(
                "Cancel",
                lambda: master.configure_ndef_return_callback(),
                frame=self
            )
            self.cancel_button.place(relx=0.6, rely=0.9, anchor="w")

            self.apply_button = master.create_button(
                "Apply",
                lambda: self.apply_ndef(),
                frame=self
            )
            self.apply_button.place(relx=0.8, rely=0.9, anchor="w")

            self.update_frame()
            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"An unexpected error occurred in FrameCardConfigureNdef init: {e}", exc_info=True)

    def _create_radio_button(self, text, variable, value, command=None):
        return customtkinter.CTkRadioButton(
            self,
            text=text,
            variable=variable,
            value=value,
            font=customtkinter.CTkFont(family=constants.FONT_FAMILY, size=14, weight="normal"),
            bg_color="whitesmoke", fg_color="green", hover_color="green",
            command=command
        )

    def update_frame(self):
        # refresh card-specific text and clear any previous input
        card_type = self.master.controller.cc.card_type
        self.text1.configure(text=f"Configure the NDEF message of your {card_type}.")
        for entry, placeholder in ((self.url_entry, URL_PLACEHOLDER),
                                   (self.app_entry, APP_PLACEHOLDER),
                                   (self.raw_entry, RAW_PLACEHOLDER)):
            entry.delete(0, "end")
            entry.configure(placeholder_text=placeholder)
        self.predefined_radio_value.set("0")

        # place option radio buttons on 2 rows of 3 (dynamic NDEF is only available for Satodime)
        options = [value for value, text in NDEF_OPTIONS
                   if value != NDEF_OPTION_DYNAMIC or card_type == "Satodime"]
        for radio_button in self.option_radio_buttons.values():
            radio_button.place_forget()
        for index, value in enumerate(options):
            self.option_radio_buttons[value].place(
                relx=0.05 + 0.28 * (index % 3), rely=0.41 + 0.06 * (index // 3), anchor="w"
            )
        self.option_radio_value.set(NDEF_OPTION_DISABLE)
        self.update_option_selection()

    def update_option_selection(self):
        option = self.option_radio_value.get()
        logger.debug(f"NDEF option selected: {option}")

        # remove option specific widgets
        for widget in [self.option_text, self.url_label, self.url_entry, self.app_label, self.app_entry,
                       self.raw_label, self.raw_entry] + self.predefined_radio_buttons:
            widget.place_forget()

        rely = 0.58
        if option == NDEF_OPTION_DISABLE:
            self.option_text.configure(text="NDEF will be disabled once you click on 'Apply'.")
            self.option_text.place(relx=0.05, rely=rely, anchor="w")
        elif option == NDEF_OPTION_URL:
            self.url_label.place(relx=0.05, rely=rely, anchor="w")
            self.url_entry.place(relx=0.05, rely=rely + 0.06, anchor="w")
        elif option == NDEF_OPTION_APP:
            self.app_label.place(relx=0.05, rely=rely, anchor="w")
            self.app_entry.place(relx=0.05, rely=rely + 0.06, anchor="w")
        elif option == NDEF_OPTION_PREDEFINED:
            for index, radio_button in enumerate(self.predefined_radio_buttons):
                radio_button.place(relx=0.05 + 0.35 * (index // 4), rely=rely + 0.06 * (index % 4), anchor="w")
        elif option == NDEF_OPTION_DYNAMIC:
            self.option_text.configure(
                text="NDEF will be generated dynamically based on the Satodime vaults status."
            )
            self.option_text.place(relx=0.05, rely=rely, anchor="w")
        elif option == NDEF_OPTION_RAW:
            self.raw_label.place(relx=0.05, rely=rely, anchor="w")
            self.raw_entry.place(relx=0.05, rely=rely + 0.06, anchor="w")

    def apply_ndef(self):
        option = self.option_radio_value.get()
        ndef_policy = NDEF_POLICY_STATIC
        ndef_bytes = b""
        try:
            if option == NDEF_OPTION_DISABLE:
                ndef_policy = NDEF_POLICY_DISABLED
            elif option == NDEF_OPTION_DYNAMIC:
                ndef_policy = NDEF_POLICY_DYNAMIC
            elif option == NDEF_OPTION_URL:
                ndef_bytes = ndef_encode_url(self.url_entry.get())
            elif option == NDEF_OPTION_APP:
                ndef_bytes = ndef_encode_aar(self.app_entry.get())
            elif option == NDEF_OPTION_RAW:
                ndef_bytes = ndef_parse_raw(self.raw_entry.get())
            elif option == NDEF_OPTION_PREDEFINED:
                name, ndef_type, ndef_value = NDEF_PREDEFINED_LIST[int(self.predefined_radio_value.get())]
                if ndef_type == "aar":
                    ndef_bytes = ndef_encode_aar(ndef_value)
                else:
                    ndef_bytes = ndef_encode_url(ndef_value)
        except Exception as e:
            logger.warning(f"Invalid NDEF value: {e}")
            self.master.show("ERROR", f"Invalid NDEF value: {e}", "Ok", None,
                             "./pictures_db/error_popup_red.png")
            return

        self.master.update_verify_pin()
        self.master.controller.set_card_ndef(
            ndef_bytes, ndef_policy,
            on_success=self.master.configure_ndef_return_callback
        )
