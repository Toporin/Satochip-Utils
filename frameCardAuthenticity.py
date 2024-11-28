import customtkinter
import logging
from PIL import Image, ImageTk

from constants import MAIN_MENU_COLOR, BUTTON_COLOR
from frameWidgetHeader import FrameWidgetHeader

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameCardAuthenticity(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameStart init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            self.header = FrameWidgetHeader(
                "Check authenticity",
                "check_authenticity_popup.jpg",
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            self.certificate_radio_value = customtkinter.StringVar(value="device_certificate")

            #
            self.text1 = master.create_label(
                f"Check whether or not you have a genuine Satochip card.",
                frame=self
            )
            self.text1.place(relx=0.05, rely=0.17, anchor="w")

            self.text2 = master.create_label(
                f"Status:",
                frame=self
            )
            self.text2.configure(font=master.make_text_bold())
            self.text2.place(relx=0.05, rely=0.27, anchor="w")

            # widget with default values, willbe updated later
            icon_image = Image.open("./pictures_db/not_genuine_card.jpg")
            icon = customtkinter.CTkImage(light_image=icon_image, size=(30, 30))
            self.icon_label = customtkinter.CTkLabel(
                self, image=icon,
                text=f"Your card is not authentic. ",
                compound='right', bg_color="whitesmoke", fg_color="whitesmoke",
                font=customtkinter.CTkFont(family="Outfit", size=18, weight="normal"),
            )
            self.icon_label.place(relx=0.2, rely=0.267, anchor="w")
            # text if not authentic
            self.text_warning1 = master.create_label("", frame=self)
            self.text_warning1.configure(font=master.make_text_bold())
            self.text_warning1.place(relx=0.05, rely=0.7, anchor="w")
            self.text_warning2 = master.create_label("",frame=self)
            self.text_warning2.place(relx=0.05, rely=0.75, anchor="w")
            self.text_warning3 = master.create_label("", frame=self)
            self.text_warning3.place(relx=0.05, rely=0.8, anchor="w")
            self.text_warning4 = master.create_label("", frame=self)
            self.text_warning4.place(relx=0.05, rely=0.85, anchor="w")

            # Setting up radio buttons
            self.root_ca_certificate = customtkinter.CTkRadioButton(
                self,
                text="Root CA certificate",
                variable=self.certificate_radio_value,
                value="root_ca_certificate",
                font=customtkinter.CTkFont(family="Outfit", size=14, weight="normal"),
                bg_color="whitesmoke", fg_color="green", hover_color="green",
                command=self.update_radio_selection
            )
            self.root_ca_certificate.place(relx=0.05, rely=0.35, anchor="w")

            self.sub_ca_certificate = customtkinter.CTkRadioButton(
                self,
                text="Sub CA certificate",
                variable=self.certificate_radio_value,
                value="sub_ca_certificate",
                font=customtkinter.CTkFont(family="Outfit", size=14, weight="normal"),
                bg_color="whitesmoke", fg_color="green", hover_color="green",
                command=self.update_radio_selection
            )
            self.sub_ca_certificate.place(relx=0.33, rely=0.35, anchor="w")

            self.device_certificate = customtkinter.CTkRadioButton(
                self,
                text="Device certificate",
                variable=self.certificate_radio_value,
                value="device_certificate",
                font=customtkinter.CTkFont(family="Outfit", size=14, weight="normal"),
                bg_color="whitesmoke", fg_color="green", hover_color="green",
                command=self.update_radio_selection
            )
            self.device_certificate.place(relx=0.61, rely=0.35, anchor="w")

            # Setting up text box
            self.text_box = customtkinter.CTkTextbox(
                self, corner_radius=10,
                bg_color='whitesmoke', fg_color=BUTTON_COLOR, border_color=BUTTON_COLOR,
                border_width=0, width=581, text_color="grey",
                height= 150,
                font=customtkinter.CTkFont(family="Outfit", size=13, weight="normal")
            )

            self.cancel_button = master.create_button(
                "Back", lambda: master.show_start_frame(), frame=self)
            self.cancel_button.place(relx=0.8, rely=0.9, anchor="w")

            # update frame with card data then show
            self.txt_ca = self.txt_subca = self.txt_device = self.txt_error = ""
            self.update_frame()
            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"An unexpected error occurred in check_authenticity: {e}", exc_info=True)

    def update_radio_selection(self):
        logger.info(f"Button clicked: {self.certificate_radio_value.get()}")
        if self.certificate_radio_value.get() == 'root_ca_certificate':
            self.master.update_textbox(self.text_box, self.txt_ca)
            self.text_box.place(relx=0.05, rely=0.4, anchor="nw")
        if self.certificate_radio_value.get() == 'sub_ca_certificate':
            self.master.update_textbox(self.text_box, self.txt_subca)
            self.text_box.place(relx=0.05, rely=0.4, anchor="nw")
        if self.certificate_radio_value.get() == 'device_certificate':
            self.master.update_textbox(self.text_box, self.txt_device)
            self.text_box.place(relx=0.05, rely=0.4, anchor="nw")

    def update_frame(self):

        if self.master.controller.cc.card_present:
            logger.info("FrameCardAuthenticity update_frame() Card detected: checking authenticity")
            is_authentic, self.txt_ca, self.txt_subca, self.txt_device, self.txt_error = self.master.controller.cc.card_verify_authenticity()
            if self.txt_error != "":
                self.txt_device = self.txt_error + "\n------------------\n" + self.txt_device

            if is_authentic:
                icon_image = Image.open("./pictures_db/genuine_card.jpg")
                icon = customtkinter.CTkImage(light_image=icon_image, size=(30, 30))
                self.icon_label.configure(
                    require_redraw=True,
                    image=icon,
                    text=f"Your card is authentic. ",
                )
                self.text_box.configure(require_redraw=True, height= 228)
            else:
                icon_image = Image.open("./pictures_db/not_genuine_card.jpg")
                icon = customtkinter.CTkImage(light_image=icon_image, size=(30, 30))
                self.icon_label.configure(
                    require_redraw=True,
                    image=icon,
                    text="Your card is not authentic. ",
                )
                self.text_box.configure(require_redraw=True, height=150)
                self.text_warning1.configure(text="Warning!")
                self.text_warning2.configure(text="We could not authenticate the issuer of this card.")
                self.text_warning3.configure(text="If you did not load the card applet by yourself, be extremely careful!")
                self.text_warning4.configure(text="Contact support@satochip.io to report any suspicious device.")

            # update text_box content
            self.update_radio_selection()
