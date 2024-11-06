import time

import customtkinter
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameCardFactoryReset(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameCardFactoryReset init")
        master.controller.cc.set_mode_factory_reset(True)

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Load background photo
            self.background_photo = master.create_background_photo("./pictures_db/reset_my_card.png")
            self.canvas = master.create_canvas(frame=self)
            self.canvas.place(relx=0.0, rely=0.5, anchor="w")
            self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")

            # Creating header
            self.header = master.create_an_header(
                f"Reset Your {master.controller.cc.card_type}",
                "reset_popup.jpg",
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            # setup paragraph
            self.text1 = master.create_label(
                f"Resetting your card to factory settings removes all private keys, saved ",
                frame=self
            )
            self.text1.place(relx=0.05, rely=0.17, anchor="w")

            self.text2 = master.create_label(
                "information, and settings (PIN code) from your device.",
                frame=self
            )
            self.text2.place(relx=0.05, rely=0.22, anchor="w")

            self.text3 = master.create_label(
                "Before your start: be sure to have a backup of its content; either the",
                frame=self
            )
            self.text3.place(relx=0.05, rely=0.32, anchor="w")

            self.text4 = master.create_label(
                f"seedphrase or any other passwords stored in it.",
                frame=self
            )
            self.text4.place(relx=0.05, rely=0.37, anchor="w")

            self.text5 = master.create_label(
                "The reset process is simple: click on “Reset”, follow the pop-up wizard and",
                frame=self
            )
            self.text5.place(relx=0.05, rely=0.47, anchor="w")

            self.text6 = master.create_label(
                "remove your card from the chip card reader, insert it again. And do that",
                frame=self
            )
            self.text6.place(relx=0.05, rely=0.52, anchor="w")

            self.text7 = master.create_label(
                "several times.",
                frame=self
            )
            self.text7.place(relx=0.05, rely=0.57, anchor="w")

            # Creating quit & start button
            def click_cancel_button():
                logger.info("Executing quit button action")
                master.controller.cc.set_mode_factory_reset(False)
                time.sleep(0.5)  # todo remove?
                master.show_start_frame()

            def click_start_button():
                master.show(
                    'IN PROGRESS',
                    f"Please follow the instruction bellow.",
                    "Remove card",
                    lambda: self.click_reset_button(),
                    "./pictures_db/reset_popup.jpg"
                )
                master.show_button.configure(state='disabled')

            self.cancel_button = master.create_button(
                'Cancel',
                lambda: click_cancel_button(),
                frame=self
            )
            self.cancel_button.place(relx=0.6, rely=0.9, anchor="w")

            self.reset_button = master.create_button(
                'Start',
                lambda: click_start_button(),
                frame=self
            )
            self.reset_button.place(relx=0.8, rely=0.9, anchor="w")

            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"An unexpected error occurred in FrameCardImportSeed init: {e}", exc_info=True)

    def click_reset_button(self): # todo implement reset factory v1 & v2
        try:
            logger.info("click_reset_button attempting to reset the card.")

            (response, sw1, sw2) = self.master.controller.cc.card_reset_factory_signal()
            logger.info(f"card_reset_factory response: {hex(256 * sw1 + sw2)}")
            if sw1 == 0xFF and sw2 == 0x00:
                logger.info("Factory reset successful. Disconnecting the card.")
                self.master.controller.cc.set_mode_factory_reset(False)
                self.master.controller.cc.card_disconnect()
                msg = 'The card has been reset to factory\nRemaining counter: 0'
                self.master.show('SUCCESS', msg, "Ok", lambda: self.master.restart_app(),
                          "./pictures_db/reset_popup.jpg")
                logger.info("Card has been reset to factory. Counter set to 0.")
            elif sw1 == 0xFF and sw2 == 0xFF:
                logger.info("Factory reset aborted. The card must be removed after each reset.")
                msg = 'RESET ABORTED!\n Remaining counter: MAX.'
                self.master.show('ABORTED', msg, "Ok",
                          lambda: [self.master.controller.cc.set_mode_factory_reset(False), self.master.show_start_frame()],
                          "./pictures_db/reset_popup.jpg")
                logger.info("Reset aborted. Counter set to MAX.")
            elif sw1 == 0xFF and sw2 > 0x00:
                logger.info(f"Factory reset in progress. Remaining counter: {sw2}")
                counter = str(sw2) + "/4"
                msg = f"Please follow the instruction bellow.\n{counter}"
                self.master.show('IN PROGRESS', msg, "Remove card", lambda: self.click_reset_button(),
                          "./pictures_db/reset_popup.jpg")
                self.master.show_button.configure(state='disabled')
                logger.info("Card needs to be removed and reinserted to continue.")
            elif sw1 == 0x6F and sw2 == 0x00:
                logger.info("Factory reset failed with error code 0x6F00.")
                counter = "Unknown error " + str(hex(256 * sw1 + sw2))
                msg = f"The factory reset failed\n{counter}"
                self.master.show('FAILED', msg, "Ok", None, "./pictures_db/reset_popup.jpg")
            elif sw1 == 0x6D and sw2 == 0x00:
                logger.info("Factory reset failed with error code 0x6D00.")
                counter = "Instruction not supported - error code: " + str(hex(256 * sw1 + sw2))
                msg = f"The factory reset failed\n{counter}"
                self.master.show('FAILED', msg, "Ok", None, "./pictures_db/reset_popup.jpg")

        except Exception as e:
            logger.error(f"An unexpected error occurred during the factory reset process: {e}", exc_info=True)
