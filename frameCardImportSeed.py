import customtkinter
import logging

from constants import BUTTON_COLOR
from frameWidgetHeader import FrameWidgetHeader

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameCardImportSeed(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameCardImportSeed init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Creating header
            self.header = FrameWidgetHeader(
                "Import Seed",
                "seed_popup.jpg",
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            # setup paragraph
            self.text1 = master.create_label(
                "Set up your Satochip hardware wallet as a new device to get started.",
                frame=self
            )
            self.text1.place(relx=0.05, rely=0.17, anchor="w")

            self.text2 = master.create_label(
                "Import or generate a new mnemonic seedphrase and generate new",
                frame=self
            )
            self.text2.place(relx=0.05, rely=0.22, anchor="w")

            self.text3 = master.create_label(
                "private keys that will be stored within the chip memory.",
                frame=self
            )
            self.text3.place(relx=0.05, rely=0.27, anchor="w")

            self.radio_value = customtkinter.StringVar(value="")
            self.checkbox_passphrase_value = customtkinter.StringVar(value="off")
            self.radio_value_mnemonic = customtkinter.StringVar(value="")
            logger.debug(
                f"Settings radio_value: {self.radio_value}, checkbox_passphrase_value: {self.checkbox_passphrase_value}")

            def on_text_box_click(event):
                if self.text_box.get("1.0", "end-1c") == "Type your existing seedphrase here":
                    self.text_box.delete("1.0", "end")

            def update_radio_mnemonic_length():
                if self.radio_value_mnemonic.get() == "generate_12":
                    self.mnemonic_length = 12
                elif self.radio_value_mnemonic.get() == "generate_24":
                    self.mnemonic_length = 24

                mnemonic = master.controller.generate_random_seed(self.mnemonic_length)
                master.update_textbox(self.text_box, mnemonic)

            def update_radio_selection():
                if self.radio_value.get() == "import":
                    logger.debug("Import seed")
                    self.finish_button.place(relx=0.8, rely=0.9, anchor="w")
                    self.cancel_button.place(relx=0.6, rely=0.9, anchor="w")
                    self.radio_button_generate_seed.place_forget()
                    self.radio_button_import_seed.place_forget()
                    self.radio_button_generate_12_words.place_forget()
                    self.radio_button_generate_24_words.place_forget()
                    self.text_box.place_forget()
                    self.warning_label.place_forget()
                    self.radio_button_import_seed.place(relx=0.05, rely=0.35, anchor="w")
                    self.text_box.delete(1.0, "end")
                    self.text_box.configure(width=550, height=80)
                    self.text_box.insert(text="Type your existing seedphrase here", index=1.0)
                    self.text_box.bind("<FocusIn>", on_text_box_click)
                    self.text_box.place(relx=0.13, rely=0.45, anchor="w")
                    self.checkbox_passphrase.place(relx=0.13, rely=0.58, anchor="w")
                    update_checkbox_passphrase()
                    self.radio_button_generate_seed.place(relx=0.05, rely=0.75, anchor="w")

                elif self.radio_value.get() == "generate":
                    logger.debug("Generate seed")
                    self.cancel_button.place_forget()
                    self.finish_button.place(relx=0.8, rely=0.9, anchor="w")
                    self.cancel_button.place(relx=0.6, rely=0.9, anchor="w")
                    self.radio_button_import_seed.place_forget()
                    self.radio_button_generate_seed.place_forget()
                    self.checkbox_passphrase.place_forget()
                    self.text_box.delete(1.0, "end")
                    self.text_box.place_forget()
                    self.warning_label.place_forget()
                    self.radio_button_import_seed.place(relx=0.05, rely=0.35, anchor="w")
                    self.radio_button_generate_seed.place(relx=0.05, rely=0.41, anchor="w")
                    self.radio_button_generate_12_words.place(relx=0.17, rely=0.47, anchor="w")
                    self.radio_button_generate_24_words.place(relx=0.37, rely=0.47, anchor="w")
                    self.text_box.configure(width=550, height=96) #height=80
                    self.text_box.place(relx=0.16, rely=0.58, anchor="w")
                    self.warning_label.place(relx=0.36, rely=0.69, anchor="w") # rely=0.64
                    self.checkbox_passphrase.place(relx=0.17, rely=0.75, anchor="w")
                    update_checkbox_passphrase()

            def update_checkbox_passphrase():
                if self.radio_value.get() == "import":
                    if self.checkbox_passphrase_value.get() == "on":
                        logger.debug("Generate seed with passphrase")
                        self.passphrase_entry.place_forget()
                        self.passphrase_entry.place(relx=0.13, rely=0.65, anchor="w")
                        self.passphrase_entry.configure(placeholder_text="Type your passphrase here")
                    else:
                        self.passphrase_entry.place_forget()

                elif self.radio_value.get() == "generate":
                    if self.checkbox_passphrase_value.get() == "on":
                        logger.debug("Generate seed with passphrase")
                        self.passphrase_entry.place_forget()
                        self.passphrase_entry.place(relx=0.16, rely=0.82, anchor="w") #rely=0.76
                        self.passphrase_entry.configure(placeholder_text="Type your passphrase here")
                    else:
                        self.passphrase_entry.place_forget()

            # Setting up radio buttons and entry fields
            self.radio_button_import_seed = customtkinter.CTkRadioButton(
                self,
                text="I already have a seedphrase",
                variable=self.radio_value, value="import",
                font=customtkinter.CTkFont(family="Outfit", size=14, weight="normal"),
                bg_color="whitesmoke", fg_color="green", hover_color="green",
                command=update_radio_selection
            )
            self.radio_button_import_seed.place(relx=0.05, rely=0.35, anchor="w")

            self.radio_button_generate_seed = customtkinter.CTkRadioButton(
                self,
                text="I want to generate a new seedphrase",
                variable=self.radio_value, value="generate",
                font=customtkinter.CTkFont(family="Outfit", size=14, weight="normal"),
                bg_color="whitesmoke", fg_color="green",
                hover_color="green",
                command=update_radio_selection,
            )
            self.radio_button_generate_seed.place(relx=0.05, rely=0.42, anchor="w")

            self.radio_button_generate_12_words = customtkinter.CTkRadioButton(
                self,
                text="12 words",
                variable=self.radio_value_mnemonic,
                value="generate_12",
                font=customtkinter.CTkFont(family="Outfit", size=14, weight="normal"),
                bg_color="whitesmoke", fg_color="green",
                hover_color="green",
                command=update_radio_mnemonic_length
            )
            self.radio_button_generate_24_words = customtkinter.CTkRadioButton(
                self,
                text="24 words",
                variable=self.radio_value_mnemonic,
                value="generate_24",
                font=customtkinter.CTkFont(family="Outfit", size=14, weight="normal"),
                bg_color="whitesmoke", fg_color="green",
                hover_color="green",
                command=update_radio_mnemonic_length
            )

            self.checkbox_passphrase = customtkinter.CTkCheckBox(
                self,
                text="Use a passphrase (optional)",
                command=update_checkbox_passphrase,
                variable=self.checkbox_passphrase_value,
                onvalue="on",
                offvalue="off"
            )

            self.passphrase_entry = master.create_entry(frame=self)

            self.text_box = customtkinter.CTkTextbox(
                self, corner_radius=20,
                bg_color="whitesmoke", fg_color=BUTTON_COLOR,
                border_color=BUTTON_COLOR, border_width=1,
                width=557, height=83, border_spacing=0,
                text_color="grey", wrap="word",
                font=customtkinter.CTkFont(family="Outfit", size=13, weight="normal")
            )

            self.warning_label = customtkinter.CTkLabel(
                self,
                text="Your mnemonic is important, be sure to save it in a safe place!",
                text_color="red",
                font=customtkinter.CTkFont(family="Outfit", size=12, weight="normal")
            )

            self.cancel_button = master.create_button(
                "Back",
                command=lambda: master.show_start_frame(),
                frame=self
            )
            self.cancel_button.place(relx=0.8, rely=0.9, anchor="w")

            self.finish_button = master.create_button(  # will be placed after mnemonic is generated
                "Import",
                command=lambda: [
                    master.controller.import_seed(
                        self.text_box.get(1.0, "end-1c"),
                        self.passphrase_entry.get() if (self.checkbox_passphrase_value.get() == "on") else None,
                    ),
                ],
                frame=self
            )

            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"An unexpected error occurred in FrameCardImportSeed init: {e}", exc_info=True)