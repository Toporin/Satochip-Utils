import customtkinter
import logging
from pysatochip.version import PYSATOCHIP_VERSION

from frameWidgetHeader import FrameWidgetHeader
from version import VERSION

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameCardAbout(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameStart init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # background image
            self.background_photo = master.create_background_photo("./pictures_db/about_background.png")
            self.canvas = master.create_canvas(frame=self)
            self.canvas.place(relx=0.0, rely=0.5, anchor="w")
            self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")

            # title
            self.header = FrameWidgetHeader(
                "About", "about_popup.jpg",
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            # card infos
            # using default values,
            self.card_information = master.create_label("Card information", frame=self)
            self.card_information.place(relx=0.05, rely=0.25, anchor="w")
            self.card_information.configure(font=master.make_text_bold())

            self.applet_version = master.create_label(
                f"Applet version: [UNKNOWN]",  # to update later
                frame=self
            )
            self.applet_version.place(relx=0.05, rely=0.33)

            self.card_label_named = master.create_label(
                f"Label: [UNKNOWN]",
                frame=self
            )
            self.card_label_named.place(relx=0.05, rely=0.28)

            self.card_genuine = master.create_label(
                f"Genuine: [UNKNOWN]",
                frame=self
            )
            self.card_genuine.place(relx=0.05, rely=0.38)

            self.watch_all = master.create_label("card status [UNKNOWN]", frame=self)  # updated later
            self.watch_all.place(relx=0.05, rely=0.17)

            self.unlock_button = master.create_button("Verify PIN", lambda: [self.unlock()], frame=self)
            self.unlock_button.configure(font=master.make_text_size_at(15))
            self.unlock_button.place(relx=0.66, rely=0.17)
            # self.unlock_button.place_forget()

            # card configuration
            self.card_configuration = master.create_label("Card configuration", frame=self)
            self.card_configuration.place(relx=0.05, rely=0.48, anchor="w")
            self.card_configuration.configure(font=master.make_text_bold())

            self.pin_information = master.create_label("PIN status", frame=self)  # updated later
            self.pin_information.place(relx=0.05, rely=0.52)

            self.two_FA = master.create_label("2FA status", frame=self)  # updated later
            self.two_FA.place(relx=0.05, rely=0.58)

            # card connectivity # todo remove as part of card info?
            self.card_connectivity = master.create_label("Card connectivity", frame=self)
            self.card_connectivity.place(relx=0.05, rely=0.68, anchor="w")
            self.card_connectivity.configure(font=master.make_text_bold())

            self.nfc = master.create_label(f"NFC status: [UNKNOWN]", frame=self)  # updated later
            self.nfc.place(relx=0.05, rely=0.715)
            # self.button_nfc = self.create_button("Disable NFC")
            # self.button_nfc.place(relx=0.5, rely=0.71)

            # software information
            self.software_information = master.create_label("Software information", frame=self)
            self.software_information.place(relx=0.05, rely=0.81, anchor="w")
            self.software_information.configure(font=master.make_text_bold())

            self.app_version = master.create_label(f"Satochip-utils version: {VERSION}", frame=self)
            self.app_version.place(relx=0.05, rely=0.83)
            self.pysatochip_version = master.create_label(f"Pysatochip version: {PYSATOCHIP_VERSION}", frame=self)
            self.pysatochip_version.place(relx=0.05, rely=0.88)

            # self.back_button = master.create_button(
            #     'Back',
            #     lambda: master.show_start_frame(),
            #     frame=self
            # )
            # self.back_button.place(relx=0.8, rely=0.9, anchor="w")

            self.update_frame()
            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"An unexpected error occurred in FrameCardAbout init: {e}", exc_info=True)

    def unlock(self):
        self.master.update_verify_pin()
        self.update_frame()

    def update_frame(self):

        if self.master.controller.cc.card_present:
            logger.info("FrameCardAbout update_frame() card detected")
            # get card data
            response, sw1, sw2, card_status = self.master.controller.cc.card_get_status()
            applet_full_version_string = f"{card_status['protocol_major_version']}.{card_status['protocol_minor_version']}-{card_status['applet_major_version']}.{card_status['applet_minor_version']}"

            # generic info no pin needed
            self.applet_version.configure(text=f"Applet version: {applet_full_version_string}")

            if self.master.controller.cc.nfc_policy == 0:
                self.nfc.configure(text=f"NFC enabled")
            elif self.master.controller.cc.nfc_policy == 1:
                self.nfc.configure(text=f"NFC disabled")
            else:
                self.nfc.configure(text=f"NFC blocked")

            # requires PIN (or satodime)
            if self.master.controller.cc.card_type == "Satodime" or self.master.controller.cc.is_pin_set():
                if self.master.controller.cc.card_type != "Satodime":
                    self.master.controller.cc.card_verify_PIN_simple()

                self.watch_all.configure(text="")
                self.unlock_button.place_forget()

                self.card_label_named.configure(text=f"Label: [{self.master.controller.get_card_label_infos()}]")

                is_authentic, txt_ca, txt_subca, txt_device, txt_error = self.master.controller.cc.card_verify_authenticity()
                self.card_genuine.configure(text=f"Genuine: YES" if is_authentic else "Genuine: NO")
            else:
                self.watch_all.configure(text="PIN required to look at complete information")
                self.unlock_button.place()

            # pin status
            if self.master.controller.cc.card_type == "Satodime":
                self.pin_information.configure(text="No PIN required")
            else:
                if self.master.controller.cc.setup_done:
                    self.pin_information.configure(
                        text=f"PIN counter: [{card_status['PIN0_remaining_tries']}] tries remaining",
                    )
                else:
                    self.pin_information.configure(text="Card requires setup")

            # for a next implementation of 2FA functionality you have the code below
            if self.master.controller.cc.card_type == "Satochip":
                self.two_FA.configure(text=f"2FA enabled" if self.master.controller.cc.needs_2FA else f"2FA disabled")
                # if self.controller.cc.needs_2FA:
                #     self.button_2FA = self.create_button("Disable 2FA", None)
                # else:
                #     self.button_2FA = self.create_button("Enable 2FA")
                # self.button_2FA.configure(font=self.make_text_size_at(15), state='disabled')
                # self.button_2FA.place(relx=0.5, rely=0.58)
