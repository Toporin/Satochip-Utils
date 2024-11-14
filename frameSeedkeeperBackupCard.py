import customtkinter
import logging

from applicationMode import ApplicationMode
from frameWidgetHeader import FrameWidgetHeader
from utils import get_fingerprint_from_authentikey_bytes
from constants import BG_MAIN_MENU, BG_HOVER_BUTTON

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameSeedkeeperBackupCard(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameSeedkeeperBackupCard init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Creating header
            self.header = FrameWidgetHeader(
                "Backup your seedkeeper", "seed_popup.jpg",  # todo change icon
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            # labels
            self.label_step = master.create_label("step", frame=self)
            self.label_step.configure(font=master.make_text_bold())
            self.label_step.place(relx=0.05, rely=0.15, anchor="nw")

            self.label_description = master.create_label("description", frame=self)
            self.label_description.configure(justify="left")
            self.label_description.place(relx=0.05, rely=0.23, anchor="nw")

            self.label_instruction = master.create_label("instruction", frame=self)
            self.label_instruction.configure(justify="left")
            self.label_instruction.configure(font=master.make_text_bold())
            self.label_instruction.place(relx=0.05, rely=0.31, anchor="nw")

            # action buttons
            self.next_button = master.create_button("Start", command=None, frame=self)
            self.next_button.place(relx=0.95, rely=0.95, anchor="se")

            def on_cancel_button():
                master.appMode = ApplicationMode.Normal  # reset application mode
                self.reset_backup_state()  # reset state
                master.show_start_frame()

            self.cancel_button = master.create_button(
                "Cancel", command=lambda: on_cancel_button(), frame=self)
            self.cancel_button.place(relx=0.75, rely=0.95, anchor="se")

            # backup state # todo reset state on cancel/finish
            self.master_pin = None
            self.master_authentikey = None
            self.master_authentikey_id = None
            self.master_secret_headers = None

            self.backup_pin = None
            self.backup_authentikey = None
            self.backup_authentikey_id = None
            self.backup_secret_headers = None

            self.secret_headers_to_backup = []
            self.secrets_to_backup = []
            self.backup_logs = []
            self.is_backup_error = False

            # place frame
            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"Init error : {e}", exc_info=True)

    def backup_start(self):

        # configure frame
        self.label_step.configure(text="Start")
        self.label_description.configure(
            text="You are about to create a carbon copy of your current card (the 'master') "
                 "\nto another Seedkeeper (the 'backup') via an encrypted communication.")
        self.label_instruction.configure(text="Press the start button to continue.")

        # reset state
        self.reset_backup_state()
        self.master.secret_headers = None  # reset cached list of headers since multiple cards will be inserted/removed

        def on_next_button():
            self.master_pairing()

        self.next_button.configure(command=lambda: on_next_button())

    def master_pairing(self):

        # configure frame
        self.label_step.configure(text="Step 1/4 - pairing master card")
        self.label_description.configure(
            text="In this step, the application will recover from the master card"
                 "\nthe information needed to perform the backup.")
        self.label_instruction.configure(text="Ensure your master card is inserted then click 'next'.")
        self.label_instruction.configure(text_color=BG_MAIN_MENU)
        self.next_button.configure(text="Next")

        def on_next_button():
            # verify PIN
            self.master.update_verify_pin()
            # hack: recover master pin from cc
            self.master_pin = bytes(self.master.controller.cc.pin)
            logger.debug(f"self.master_pin: {self.master_pin}")

            # get authentikey # todo check with masterview
            self.master_authentikey = self.master.controller.cc.card_bip32_get_authentikey()
            logger.debug(f"self.master_authentikey: {self.master_authentikey}")
            logger.debug(f"self.master_authentikey bytes: {self.master_authentikey.get_public_key_bytes(compressed=False)}")
            logger.debug(
                f"self.master_authentikey hex: {self.master_authentikey.get_public_key_bytes(compressed=False).hex()}")
            logger.debug(
                f"self.master_authentikey.get_public_key_hex(): {self.master_authentikey.get_public_key_hex()}")
            logger.debug(
                f"self.master_authentikey.get_public_key_hex(compressed=False): {self.master_authentikey.get_public_key_hex(compressed=False)}")

            # get list of headers if needed
            # if self.master.secrets_data is None:
            # get list of secret headers
            self.master_secret_headers = self.master.controller.retrieve_secrets_stored_into_the_card()
            logger.debug(f"Fetched {len(self.master_secret_headers)} headers from card")
            # else:
            #     self.master_secrets_headers = self.master.secrets_data

            # proceed to next screen
            self.backup_pairing()

        self.next_button.configure(command=lambda: on_next_button())

    def backup_pairing(self):
        # configure frame
        self.label_step.configure(text="Step 2/4 - pairing backup card")
        self.label_description.configure(
            text="In this step, the application will recover from the backup card"
                 "\nthe information needed to perform the backup.")
        self.label_instruction.configure(text="Insert your backup card then click 'next' to proceed.")
        self.label_instruction.configure(text_color=BG_HOVER_BUTTON)
        self.next_button.configure(text="Next")

        def on_next_button():
            # verify PIN
            self.master.controller.PIN_dialog(f'Enter the PIN of your BACKUP card')
            # hack: recover master pin from cc
            self.backup_pin = bytes(self.master.controller.cc.pin)
            logger.debug(f"self.backup_pin: {self.backup_pin}")

            # get authentikey
            self.backup_authentikey = self.master.controller.cc.card_bip32_get_authentikey()
            logger.debug(f"self.backup_authentikey: {self.backup_authentikey}")
            logger.debug(f"self.backup_authentikey bytes: {self.backup_authentikey.get_public_key_bytes(compressed=False)}")
            logger.debug(
                f"self.backup_authentikey hex: {self.backup_authentikey.get_public_key_bytes(compressed=False).hex()}")
            logger.debug(
                f"self.backup_authentikey.get_public_key_hex(): {self.backup_authentikey.get_public_key_hex()}")
            logger.debug(
                f"self.backup_authentikey.get_public_key_hex(compressed=False): {self.backup_authentikey.get_public_key_hex(compressed=False)}")

            # check it is different from master
            if (self.backup_authentikey.get_public_key_bytes(compressed=False) ==
                    self.master_authentikey.get_public_key_bytes(compressed=False)):
                self.master.show(
                    'ERROR',
                    'This is your MASTER card.\nPlease insert your BACKUP card and try again!',
                    'Ok',
                    None,
                    "./pictures_db/change_pin_popup.jpg"
                )
                return

            # get list of headers from backup
            self.backup_secret_headers = self.master.controller.retrieve_secrets_stored_into_the_card()
            logger.debug(f"Fetched {len(self.backup_secret_headers)} headers from backup card")

            # find secrets that are on master but not yet on backup, based on fingerprint
            self.secret_headers_to_backup = []
            logger.debug(f"backup self.master_secret_headers: {self.master_secret_headers}")
            for header in self.master_secret_headers:
                # check if already in backup
                logger.debug(f"backup pairing header from master_secret_headers: {header}")
                secret_fingerprint = header['fingerprint']
                if not any(d['fingerprint'] == secret_fingerprint for d in self.backup_secret_headers):
                    # does not exist!
                    self.secret_headers_to_backup.append(header)
            logger.debug(f"Fetched {len(self.secret_headers_to_backup)} headers to backup")

            # check if master authentikey is already in backup or import it
            master_authentikey_fingerprint = get_fingerprint_from_authentikey_bytes(self.master_authentikey.get_public_key_bytes(compressed=False))
            authentikey_found = next((item for item in self.backup_secret_headers if item['fingerprint'] == master_authentikey_fingerprint), None)

            #if not any(d['fingerprint'] == master_authentikey_fingerprint for d in self.backup_secret_headers):
            if authentikey_found is None:
                # does not exist in backup=> import it
                self.master_authentikey_id, fingerprint = self.master.controller.import_pubkey(
                    label=f"master authentikey #{master_authentikey_fingerprint}",
                    pubkey_bytes=self.master_authentikey.get_public_key_bytes(compressed=False)
                )
                logger.debug(f"imported master authentikey to backup")
                logger.debug(f"imported master authentikey id: {self.master_authentikey_id}")
                logger.debug(f"imported master authentikey fingerprint: {fingerprint}")
            else:
                logger.debug(f"master authentikey already imported to backup")
                self.master_authentikey_id = authentikey_found['id']

            # proceed to next screen
            self.master_export_secrets()

        self.next_button.configure(command=lambda: on_next_button())

    def master_export_secrets(self):
        # configure frame
        self.label_step.configure(text="Step 3/4 - exporting encrypted secrets from master")
        self.label_description.configure(
            text="In this step, the application will export the secrets from the master card."
                 "\nThe secret are encrypted using a key known only from these 2 cards.")
        self.label_instruction.configure(text="Insert your master card then click 'next' to proceed.")
        self.label_instruction.configure(text_color=BG_MAIN_MENU)
        self.next_button.configure(text="Next")

        def on_next_button():
            try:
                # verify PIN with cached pin
                self.master.controller.cc.card_verify_PIN_simple(self.master_pin)

                # check authentikey match
                authentikey = self.master.controller.cc.card_bip32_get_authentikey()
                if (authentikey.get_public_key_bytes(compressed=False) !=
                        self.master_authentikey.get_public_key_bytes(compressed=False)):
                    self.master.show(
                        'ERROR',
                        'Wrong card!\nPlease insert your MASTER card and try again.',
                        'Ok',
                        None,
                        "./pictures_db/change_pin_popup.jpg"
                    )
                    return

                # check if backup authentikey is already in master, or import it
                backup_authentikey_fingerprint = get_fingerprint_from_authentikey_bytes(
                    self.backup_authentikey.get_public_key_bytes(compressed=False))
                authentikey_found = next((item for item in self.master_secret_headers if
                                          item['fingerprint'] == backup_authentikey_fingerprint), None)
                if authentikey_found is None:
                    # does not exist in master=> import it
                    self.backup_authentikey_id, fingerprint = self.master.controller.import_pubkey(
                        label=f"backup authentikey #{backup_authentikey_fingerprint}",
                        pubkey_bytes=self.backup_authentikey.get_public_key_bytes(compressed=False)
                    )
                    logger.debug(f"imported backup authentikey to master")
                    logger.debug(f"imported backup authentikey id: {self.backup_authentikey_id}")
                    logger.debug(f"imported backup authentikey fingerprint: {fingerprint}")
                else:
                    logger.debug(f"backup authentikey already imported to backup")
                    self.backup_authentikey_id = authentikey_found['id']

                # export encrypted secret using backup authentikey for pairing
                for header in self.secret_headers_to_backup:
                    try:
                        secret = self.master.controller.cc.seedkeeper_export_secret(
                            sid=header['id'],
                            sid_pubkey=self.backup_authentikey_id,
                        )
                        self.secrets_to_backup += [secret]
                        logger.debug(f"exported secret with label: {secret['label']} and id: {secret['id']}")
                        logger.debug(f"exported secret using self.backup_authentikey_id: {self.backup_authentikey_id}")
                        logger.debug(f"exported secret: {secret}")
                    except Exception as e:
                        logger.error(f"Error during secret export: {e}", exc_info=True)
                        self.is_backup_error = True
                        error_dic = {
                            'msg': 'str(e)',
                            'id': header['id'],
                            'label': header['label']
                        }
                        self.backup_logs += [error_dic]

                logger.debug(f"exported {len(self.secrets_to_backup)} secrets")

                # proceed to next screen
                self.backup_import_secrets()

            except Exception as e:
                logger.error(f"Init error : {e}", exc_info=True)
                self.master.show(
                    'ERROR',
                    str(e),
                    'Ok',
                    None,
                    "./pictures_db/change_pin_popup.jpg"
                )

        self.next_button.configure(command=lambda: on_next_button())

    def backup_import_secrets(self):
        # configure frame
        self.label_step.configure(text="Step 4/4 - import encrypted secrets to backup")
        self.label_description.configure(
            text="In this step, the application will import the secrets to the backup card."
                 "\nThe secrets are encrypted using a key known only from these 2 cards.")
        self.label_instruction.configure(text="Insert your backup card then click 'next' to proceed.")
        self.label_instruction.configure(text_color=BG_HOVER_BUTTON)
        self.next_button.configure(text="Next")

        def on_next_button():
            # verify backup PIN with cached pin
            self.master.controller.cc.card_verify_PIN_simple(self.backup_pin)

            # check authentikey match
            authentikey = self.master.controller.cc.card_bip32_get_authentikey()
            if (authentikey.get_public_key_bytes(compressed=False) !=
                    self.backup_authentikey.get_public_key_bytes(compressed=False)):
                self.master.show(
                    'ERROR',
                    'Wrong card!\nPlease insert your BACKUP card and try again.',
                    'Ok',
                    None,
                    "./pictures_db/change_pin_popup.jpg"
                )
                return

            # import encrypted secret using master authentikey for pairing
            for secret in self.secrets_to_backup:
                try:
                    logger.debug(f"secret to import: {secret}")
                    # Import the secret
                    sid, fingerprint = self.master.controller.cc.seedkeeper_import_secret(
                        secret,
                        sid_pubkey=self.master_authentikey_id
                    )
                    if fingerprint == secret['fingerprint']:
                        ok_dic = {
                            'msg': f"success",
                            'id': sid,
                            'label': secret['label']
                        }
                        self.backup_logs += [ok_dic]
                    else:
                        logger.error(f"fingerprint mismatch: {fingerprint} instead of {secret['fingerprint']}")
                        error_dic = {
                            'msg': f"fingerprint mismatch: {fingerprint} instead of {secret['fingerprint']}",
                            'id': sid,
                            'label': secret['label']
                        }
                        self.backup_logs += [error_dic]

                    logger.debug(f"imported secret to backup")
                    logger.debug(f"imported secret id: {sid}")
                    logger.debug(f"imported secret fingerprint: {fingerprint}")
                except Exception as e:
                    logger.error(f"Error during secret import: {e}", exc_info=True)
                    self.is_backup_error = True
                    error_dic = {
                        'msg': str(e),
                        'id': secret['id'],
                        'label': secret['label']
                    }
                    self.backup_logs += [error_dic]

            # reset state
            is_backup_error = self.is_backup_error
            backup_logs = self.backup_logs
            self.reset_backup_state()
            # switch app mode to normal
            self.master.appMode = ApplicationMode.Normal
            # proceed to result screen according to backup result
            self.master.show_backup_result(is_backup_error, backup_logs)

        self.next_button.configure(command=lambda: on_next_button())

    # def backup_success(self):
    #     # configure frame
    #     self.label_step.configure(text="Backup terminated successfully!")
    #     self.label_description.configure(
    #         text="Your secrets have been successfully saved on your backup card!"
    #              "\n TODO secrets have been saved."
    #     )
    #     self.next_button.configure(text="End")
    #     logger.debug(f"self.backup_logs: {self.backup_logs}")
    #
    #     def on_next_button():
    #         # switch app mode to normal
    #         self.master.appMode = ApplicationMode.Normal
    #         # back to start screen
    #         self.master.show_start_frame()
    #
    #     self.next_button.configure(command=lambda: on_next_button())
    #
    # def backup_failure(self):
    #     # configure frame
    #     self.label_step.configure(text="There were some issues during backup")
    #     self.label_description.configure(
    #         text="Some or all secrets may not have been saved on your backup card."
    #              "\nHere is a list of issues encountered:"
    #              "\nTODO"
    #     )
    #     self.next_button.configure(text="End")
    #     logger.debug(f"self.backup_logs: {self.backup_logs}")
    #
    #     def on_next_button():
    #         # switch app mode to normal
    #         self.master.appMode = ApplicationMode.Normal
    #         # back to start screen
    #         self.master.show_start_frame()
    #
    #     self.next_button.configure(command=lambda: on_next_button())

    def reset_backup_state(self):
        # backup state
        self.master_pin = None
        self.master_authentikey = None
        self.master_authentikey_id = None
        self.master_secret_headers = None

        self.backup_pin = None
        self.backup_authentikey = None
        self.backup_authentikey_id = None
        self.backup_secret_headers = None

        self.secret_headers_to_backup = []
        self.secrets_to_backup = []
        self.backup_logs = []
        self.is_backup_error = False
