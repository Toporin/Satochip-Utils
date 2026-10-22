import customtkinter
import logging

import constants
from frameWidgetHeader import FrameWidgetHeader

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameCardSwitchNfc(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameCardSwitchNfc init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Creating header
            self.header = FrameWidgetHeader(
                "Enable/disable NFC",
                "icon_nfc.png",
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            # setup paragraph
            self.text1 = master.create_label(
                f"Activate or deactivate the NFC interface of your {master.controller.cc.card_type}.",
                frame=self
            )
            self.text1.place(relx=0.05, rely=0.17, anchor="w")

            self.text2 = master.create_label(
                "When NFC is disabled, the card only communicates through the contact interface.",
                frame=self
            )
            self.text2.place(relx=0.05, rely=0.22, anchor="w")

            # NFC state selection
            self.text3 = master.create_label("NFC state:", frame=self)
            self.text3.configure(font=master.make_text_bold())
            self.text3.place(relx=0.05, rely=0.32, anchor="w")

            self.nfc_radio_value = customtkinter.StringVar(value="0")

            self.radio_nfc_enabled = customtkinter.CTkRadioButton(
                self,
                text="NFC enabled",
                variable=self.nfc_radio_value,
                value="0",
                font=customtkinter.CTkFont(family=constants.FONT_FAMILY, size=14, weight="normal"),
                bg_color="whitesmoke", fg_color="green", hover_color="green",
                command=self.update_radio_selection
            )
            self.radio_nfc_enabled.place(relx=0.05, rely=0.38, anchor="w")

            self.radio_nfc_disabled = customtkinter.CTkRadioButton(
                self,
                text="NFC disabled",
                variable=self.nfc_radio_value,
                value="1",
                font=customtkinter.CTkFont(family=constants.FONT_FAMILY, size=14, weight="normal"),
                bg_color="whitesmoke", fg_color="green", hover_color="green",
                command=self.update_radio_selection
            )
            self.radio_nfc_disabled.place(relx=0.33, rely=0.38, anchor="w")

            self.radio_nfc_blocked = customtkinter.CTkRadioButton(
                self,
                text="NFC blocked",
                variable=self.nfc_radio_value,
                value="2",
                font=customtkinter.CTkFont(family=constants.FONT_FAMILY, size=14, weight="normal"),
                bg_color="whitesmoke", fg_color="green", hover_color="green",
                command=self.update_radio_selection
            )
            self.radio_nfc_blocked.place(relx=0.61, rely=0.38, anchor="w")

            # warning shown when NFC blocked is selected
            self.text_warning1 = master.create_label("", frame=self)
            self.text_warning1.configure(font=master.make_text_bold(), text_color="red")
            self.text_warning1.place(relx=0.05, rely=0.47, anchor="w")
            self.text_warning2 = master.create_label("", frame=self)
            self.text_warning2.configure(text_color="red")
            self.text_warning2.place(relx=0.05, rely=0.52, anchor="w")

            # Creating cancel and apply buttons
            self.cancel_button = master.create_button(
                "Cancel",
                lambda: master.switch_nfc_return_callback(),
                frame=self
            )
            self.cancel_button.place(relx=0.6, rely=0.9, anchor="w")

            self.apply_button = master.create_button(
                "Apply",
                lambda: self.apply_nfc_policy(),
                frame=self
            )
            self.apply_button.place(relx=0.8, rely=0.9, anchor="w")

            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"An unexpected error occurred in FrameCardSwitchNfc init: {e}", exc_info=True)

    def update_frame(self):
        # refresh card-specific text and select the current NFC state
        self.text1.configure(
            text=f"Activate or deactivate the NFC interface of your {self.master.controller.cc.card_type}."
        )
        nfc_policy = self.master.controller.cc.nfc_policy
        if nfc_policy is None:
            nfc_policy = 0  # NFC_ENABLED by default
        self.nfc_radio_value.set(str(nfc_policy))
        self.update_radio_selection()

    def update_radio_selection(self):
        logger.info(f"NFC state selected: {self.nfc_radio_value.get()}")
        if self.nfc_radio_value.get() == "2":
            self.text_warning1.configure(text="Warning!")
            self.text_warning2.configure(
                text="When NFC is blocked, it can only be enabled again through a factory reset."
            )
        else:
            self.text_warning1.configure(text="")
            self.text_warning2.configure(text="")

    def apply_nfc_policy(self):
        self.master.update_verify_pin()
        self.master.controller.set_nfc_policy(
            int(self.nfc_radio_value.get()),
            on_success=self.master.switch_nfc_return_callback
        )
