from os import urandom
import customtkinter
import logging

from pysatochip.CardConnector import IdentityBlockedError, WrongPinError, PinBlockedError, CardResetToFactoryError

from applicationMode import ApplicationMode
from frameWidgetHeader import FrameWidgetHeader

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameCardFactoryReset(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameCardFactoryReset init")

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
            self.header = FrameWidgetHeader(
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
                "The reset process is simple: click on 'Start', follow the pop-up wizard and",
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

            # Cancel button

            def click_cancel_button():
                logger.info("Executing quit button action")
                master.controller.cc.set_mode_factory_reset(False)
                master.appMode = ApplicationMode.Normal
                master.show_start_frame()

            self.cancel_button = master.create_button(
                'Cancel',
                lambda: click_cancel_button(),
                frame=self
            )
            self.cancel_button.place(relx=0.6, rely=0.9, anchor="w")

            # Reset button

            def factory_reset_unsupported():
                master.appMode = ApplicationMode.Normal
                master.show(
                    'FAIL',
                    f"Factory reset not supported for this card",
                    "ok",
                    lambda: master.show_start_frame(),
                    "./pictures_db/reset_popup.jpg"
                )
                master.show_button.configure(state='normal')

            def click_start_button():
                # get card type and version
                if master.controller.cc.card_present:

                    # reset cached list of headers since card state will change
                    self.master.secret_headers = None

                    # get card version
                    response, sw1, sw2, card_status = self.master.controller.cc.card_get_status()
                    applet_version = card_status['protocol_major_version']*256 + card_status['protocol_minor_version']

                    if master.controller.cc.card_type == "SeedKeeper":
                        if applet_version < 2:
                            master.appMode = ApplicationMode.FactoryResetV1
                            master.controller.cc.set_mode_factory_reset(True)
                        else:
                            master.appMode = ApplicationMode.FactoryResetV2
                    elif master.controller.cc.card_type == "Satochip":
                        if applet_version >= 12:
                            master.appMode = ApplicationMode.FactoryResetV1
                            master.controller.cc.set_mode_factory_reset(True)
                        else:
                            factory_reset_unsupported()
                    else:
                        factory_reset_unsupported()

                    master.show(
                        'IN PROGRESS',
                        f"Please follow the instruction below.",
                        "Remove card",
                        lambda: self.click_reset_button(),
                        "./pictures_db/reset_popup.jpg"
                    )
                    master.show_button.configure(state='disabled')

                else: # no card present
                    master.show(
                        'IN PROGRESS',
                        f"No card found.\nInsert card and start again.",
                        "Ok",
                        lambda: None,
                        "./pictures_db/reset_popup.jpg"
                    )
                    master.show_button.configure(state='normal')

            self.reset_button = master.create_button(
                'Start',
                lambda: click_start_button(),
                frame=self
            )
            self.reset_button.place(relx=0.8, rely=0.9, anchor="w")

            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"An unexpected error occurred in FrameCardImportSeed init: {e}", exc_info=True)

    def click_reset_button(self):
        if self.master.appMode == ApplicationMode.FactoryResetV1:
            try:
                logger.info("click_reset_button attempting to reset the card (V1)")

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
                    msg = f"Please follow the instruction below.\n{counter} steps left."
                    self.master.show('IN PROGRESS', msg, "Remove card", lambda: self.click_reset_button(),
                              "./pictures_db/reset_popup.jpg")
                    self.master.show_button.configure(state='disabled')
                    logger.info("Card needs to be removed and reinserted to continue.")
                elif sw1 == 0x6F and sw2 == 0x00:
                    logger.info("Factory reset failed with error code 0x6F00.")
                    counter = "Unknown error 0x6F00"
                    msg = f"The factory reset failed\n{counter}"
                    self.master.show('FAILED', msg, "Ok", None, "./pictures_db/reset_popup.jpg")
                elif sw1 == 0x6D and sw2 == 0x00:
                    logger.info("Factory reset failed with error code 0x6D00.")
                    counter = "Instruction not supported (error code 0x6D00)"
                    msg = f"The factory reset failed\n{counter}"
                    self.master.show('FAILED', msg, "Ok", None, "./pictures_db/reset_popup.jpg")

            except Exception as e:
                logger.error(f"An unexpected error occurred during the factory reset process: {e}", exc_info=True)

        elif self.master.appMode == ApplicationMode.FactoryResetV2:
            try:
                logger.info("click_reset_button attempting to reset the card (v2)")

                pin = urandom(6) # random pin
                try:
                    (response, sw1, sw2) = self.master.controller.cc.card_verify_PIN_simple(pin)
                    if sw1 == 0x90 and sw2 == 0x00:
                        logger.debug("correct PIN entered, factory reset is aborted")
                except PinBlockedError as ex:
                    # PIN blocked, PUK next
                    logger.debug("PIN code is blocked!")
                except WrongPinError as ex:
                    pin_remaining = ex.pin_left
                    logger.info(f"Factory reset in progress. Remaining counter: {pin_remaining}")
                    if pin_remaining > 0:
                        # if pin_remaining == 0, no need to show this popup
                        self.master.show(
                            'IN PROGRESS',
                            f"Please follow the instruction below.\n{pin_remaining} steps left.",
                            "Remove card",
                            lambda: self.click_reset_button(),
                            "./pictures_db/reset_popup.jpg"
                        )
                        self.master.show_button.configure(state='disabled')
                except Exception as ex:
                    logger.debug(f"exception: {str(ex)}")
                    import traceback
                    print(traceback.format_exc())

                response, sw1, sw2, card_status = self.master.controller.cc.card_get_status()
                if card_status["PIN0_remaining_tries"] == 0:
                    # at this point, pin is blocked, now block the puk
                    while True:
                        puk = urandom(16)  # random puk
                        puk_list = list(puk)
                        try:
                            (response, sw1, sw2) = self.master.controller.cc.card_unblock_PIN(0, puk_list)
                        except WrongPinError as ex:
                            logger.debug(f"Wrong PUK! {ex.pin_left} tries remaining!")
                        except PinBlockedError as ex:
                            logger.debug(f"PUK blocked!")
                        except CardResetToFactoryError as ex:
                            # Card reset to factory
                            logger.debug(f"CARD RESET TO FACTORY!")
                            self.master.controller.cc.setup_done = False  # force update cc state
                            self.master.appMode = ApplicationMode.Normal
                            self.master.show(
                                'SUCCESS',
                                "The card has been reset to factory!",
                                "Ok",
                                lambda: self.master.show_start_frame(),  # self.master.restart_app(),
                                "./pictures_db/reset_popup.jpg"
                            )
                            break
                        except Exception as ex:
                            logger.debug(f"Unexpected error: {str(ex)}")

            except Exception as e:
                logger.error(f"unexpected error during factory reset: {e}", exc_info=True)

        else:
            logger.info(f"unsupported application mode {self.master.appMode}")
