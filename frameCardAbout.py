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

            rely = 0.15

            # software information
            self.software_information = master.create_label("Software information", frame=self)
            self.software_information.configure(font=master.make_text_bold())
            self.software_information.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.05
            # software version
            self.app_version = master.create_label(f"Satochip-utils version: {VERSION}", frame=self)
            self.app_version.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.05
            self.pysatochip_version = master.create_label(f"Pysatochip version: {PYSATOCHIP_VERSION}", frame=self)
            self.pysatochip_version.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.08

            # card infos (using default values)
            self.card_information = master.create_label("Card information", frame=self)
            self.card_information.configure(font=master.make_text_bold())
            self.card_information.place(relx=0.05, rely=rely, anchor="nw")
            # verify PIN button
            self.unlock_button = master.create_button("Verify PIN", lambda: [self.unlock()], frame=self)
            self.unlock_button.configure(font=master.make_text_size_at(15))
            self.rely_button = rely
            rely += 0.05
            # card applet version
            self.applet_version = master.create_label(f"Applet version",  frame=self)
            self.applet_version.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.05
            # label
            self.card_label = master.create_label(f"Label: [PIN required]", frame=self)
            self.card_label.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.05
            # authenticity
            self.card_genuine = master.create_label(f"Genuine: [PIN required]", frame=self)
            self.card_genuine.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.05
            # status
            self.card_status = master.create_label("card status", frame=self)  # updated later
            self.card_status.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.05
            # NFC
            self.nfc = master.create_label(f"NFC status", frame=self)  # updated later
            self.nfc.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.08

            # TODO authentikey?

            #################
            # Card type specific info
            self.card_configuration = master.create_label("Specific configuration", frame=self)
            self.card_configuration.configure(font=master.make_text_bold())
            self.card_configuration.place(relx=0.05, rely=rely, anchor="nw")
            rely += 0.05
            self.rely = rely

            # SATOCHIP specific
            # card seeded
            self.satochip_seeded = master.create_label("Card seeded", frame=self)  # updated later
            # 2FA
            self.satochip_2FA = master.create_label("2FA status", frame=self)  # updated later

            # SEEDKEEPER specific
            # memory
            self.seedkeeper_memory = master.create_label("Memory available", frame=self)  # updated later
            # nb secrets
            self.seedkeeper_nb_secrets = master.create_label("Secret stored", frame=self)  # updated later

            # SATODIME specific
            # TODO

            self.update_frame()
            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"An unexpected error occurred in FrameCardAbout init: {e}", exc_info=True)

    def unlock(self):
        self.master.update_verify_pin()
        self.update_frame()

    def update_frame(self):
        logger.debug("FrameCardAbout update_frame start")
        if self.master.controller.cc.card_present:

            # get card data
            response, sw1, sw2, card_status = self.master.controller.cc.card_get_status()
            applet_full_version_string = f"{card_status['protocol_major_version']}.{card_status['protocol_minor_version']}-{card_status['applet_major_version']}.{card_status['applet_minor_version']}"
            protocol_version = card_status['protocol_version']

            # generic info no pin needed

            # applet version
            self.applet_version.configure(text=f"Applet version: {applet_full_version_string}")
            # nfc
            if self.master.controller.cc.nfc_policy == 0:
                self.nfc.configure(text=f"NFC: [enabled]")
            elif self.master.controller.cc.nfc_policy == 1:
                self.nfc.configure(text=f"NFC: [disabled]")
            else:
                self.nfc.configure(text=f"NFC: [blocked]")

            # requires PIN (or satodime)

            if self.master.controller.cc.card_type == "Satodime" or self.master.controller.cc.is_pin_set():
                if self.master.controller.cc.card_type != "Satodime":
                    self.master.controller.cc.card_verify_PIN_simple()

                self.unlock_button.place_forget()

                self.card_label.configure(text=f"Label: [{self.master.controller.get_card_label_infos()}]")

                is_authentic, txt_ca, txt_subca, txt_device, txt_error = self.master.controller.cc.card_verify_authenticity()
                self.card_genuine.configure(text=f"Genuine: [YES]" if is_authentic else "Genuine: [NO]")
            else:
                # pin needed from user
                self.card_label.configure(text=f"Label: [PIN required]")
                self.card_genuine.configure(text=f"Genuine: [PIN required]")
                self.unlock_button.place(relx=0.65, rely=self.rely_button, anchor="nw")

            # card status
            if self.master.controller.cc.card_type == "Satodime":
                self.card_status.configure(
                    text="Card setup" if self.master.controller.cc.setup_done else "Card not setup"
                )
            else:
                if self.master.controller.cc.setup_done:
                    self.card_status.configure(
                        text=f"Card setup, PIN counter: [{card_status['PIN0_remaining_tries']}] tries remaining",
                    )
                else:
                    self.card_status.configure(text="Card requires setup")

            # Satochip Specific
            if self.master.controller.cc.card_type == "Satochip":
                rely = self.rely
                self.seedkeeper_memory.place_forget()
                self.seedkeeper_nb_secrets.place_forget()
                self.card_configuration.configure(text="Satochip configuration")
                # seeded
                self.satochip_seeded.configure(
                    text=f"Card seeded" if self.master.controller.cc.is_seeded else f"Card not seeded"
                )
                self.satochip_seeded.place(relx=0.05, rely=rely, anchor="nw")
                rely += 0.05
                # 2FA
                self.satochip_2FA.configure(
                    text=f"2FA enabled" if self.master.controller.cc.needs_2FA else f"2FA disabled"
                )
                self.satochip_2FA.place(relx=0.05, rely=rely, anchor="nw")
                rely += 0.05

            # Seedkeeper Specific
            elif self.master.controller.cc.card_type == "SeedKeeper":
                self.satochip_seeded.place_forget()
                self.satochip_2FA.place_forget()
                self.card_configuration.configure(text="Seedkeeper configuration")
                # get seedkeeper status (seedkeeper v0.2+ and PIN required!)
                if protocol_version >= 2:
                    if self.master.controller.cc.is_pin_set():
                        self.master.controller.cc.card_verify_PIN_simple()
                        response, sw1, sw2, seedkeeper_status = self.master.controller.cc.seedkeeper_get_status()
                        logger.debug(f"seedkeeper_status: {seedkeeper_status}")
                        # memory
                        self.seedkeeper_memory.configure(
                            text=f"Memory available:  {seedkeeper_status.get('free_memory')}/{seedkeeper_status.get('total_memory')} bytes"
                        )
                        # nb secrets
                        self.seedkeeper_nb_secrets.configure(
                            text=f"Number of secrets: {seedkeeper_status.get('nb_secrets')}"
                        )
                    else:
                        # memory
                        self.seedkeeper_memory.configure(text="Memory available: [PIN required]")
                        # nb secrets
                        self.seedkeeper_nb_secrets.configure(text="Number of secrets: [PIN required]")

                    # place info fields
                    rely = self.rely
                    self.seedkeeper_memory.place(relx=0.05, rely=rely, anchor="nw")
                    rely += 0.05
                    self.seedkeeper_nb_secrets.place(relx=0.05, rely=rely, anchor="nw")
                    rely += 0.05
                else:
                    # no info available for seedkeeper v0.1
                    pass

            # Satodime Specific
            if self.master.controller.cc.card_type == "Satodime":
                # TODO
                pass
