import binascii
import hashlib
import json
import logging
from os import urandom
from typing import Dict, Any, Optional
from mnemonic import Mnemonic
from pysatochip.CardConnector import (CardConnector, UninitializedSeedError, UnexpectedSW12Error, PinBlockedError)

from constants import INS_DIC, RES_DIC, TYPE_PASSWORD, TYPE_MASTERSEED, TYPE_DATA, TYPE_DESCRIPTOR, TYPE_PUBKEY, \
    TYPE_BIP39_MNEMONIC, TYPE_ELECTRUM_MNEMONIC, TYPE_2FA_SECRET, TYPE_DIC

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Controller:

    def __init__(self, view, loglevel=logging.DEBUG):
        logger.setLevel(loglevel)
        self.view = view
        self.view.controller = self

        try:
            self.cc = CardConnector(self, loglevel=loglevel)
            logger.info("CardConnector initialized successfully.")
        except Exception as ex:
            logger.error(f"Failed to initialize CardConnector {ex}", exc_info=True)
            raise

        # card infos
        self.card_status = None
        self.satodime_status = None  # todo

    def get_card_status(self):
        if self.cc.card_present:
            logger.info("In get_card_status")
            try:
                response, sw1, sw2, self.card_status = self.cc.card_get_status()
                logger.debug(f"Card satus: {self.card_status}")
            except Exception as e:
                logger.error(f"Failed to retrieve card status: {e}")
                self.card_status = None
        else:
            self.card_status = None
        return self.card_status

    def request(self, request_type, *args):
        logger.info(str(request_type))

        method_to_call = getattr(self.view, request_type)
        reply = method_to_call(*args)
        return reply

    # def disconnect_the_card(self):
    #     self.cc.card_disconnect()

    def setup_card_pin(self, pin, pin_confirm):
        if pin:
            if 4 <= len(pin) <= 16:
                if pin == pin_confirm:
                    logger.info("Setup my card PIN: PINs match and are valid.")
                    self.card_setup_native_pin(pin)
                else:
                    logger.warning("Setup my card PIN: PINs do not match.")
                    self.view.show('ERROR', "Pin and pin confirm do not match!", 'Ok',
                                   None, "./pictures_db/change_pin_popup.jpg")
            else:
                logger.warning("Setup my card PIN: wrong PIN size.")
                self.view.show("ERROR",
                               "Pin must contain between 4 and 16 characters",
                               'Ok', None,
                               "./pictures_db/change_pin_popup.jpg")
        else:
            self.view.show("ERROR", "You have to set up a PIN to continue.", 'Ok',
                           None, "./pictures_db/change_pin_popup.jpg")

    def change_card_pin(self, current_pin, new_pin, new_pin_confirm):
        try:
            if self.cc.card_present and self.cc.card_type != "Satodime":

                if len(new_pin) < 4:
                    logger.warning("New PIN is too short.")
                    self.view.show("ERROR",
                                   "Pin must contain at least 4 characters", 'Ok',
                                   None, "./pictures_db/change_pin_popup.jpg")

                if new_pin != new_pin_confirm:
                    logger.warning("New PINs do not match.")
                    self.view.show("WARNING",
                                   "The PIN values do not match! Please type PIN again!",
                                   "Ok", None,
                                   "./pictures_db/change_pin_popup.jpg")
                else:
                    current_pin = list(current_pin.encode('utf8'))
                    new_pin = list(new_pin.encode('utf8'))
                    (response, sw1, sw2) = self.cc.card_change_PIN(0, current_pin, new_pin)
                    if sw1 == 0x90 and sw2 == 0x00:
                        logger.info("PIN changed successfully.")
                        msg = "PIN changed successfully!"
                        self.view.show("SUCCESS", msg, 'Ok',
                                       None, "./pictures_db/change_pin_popup.jpg")
                        self.view.show_start_frame()
                    else:
                        logger.error(f"Failed to change PIN with error code: {hex(sw1)}{hex(sw2)}")
                        msg = f"Failed to change PIN with error code: {hex(sw1)}{hex(sw2)}"
                        self.view.show("ERROR", f"{msg}\n Probably too long", 'Ok',
                                       None, "./pictures_db/change_pin_popup.jpg")
        except Exception as e:
            logger.error(f"Error changing PIN: {e}")
            self.view.show("ERROR", "Failed to change PIN.", "Ok",
                           None, "./pictures_db/change_pin_popup.jpg")

    def import_seed(self, mnemonic, passphrase=None):
        """Import a seed (and optional passphrase) into a Satochip"""
        try:
            MNEMONIC = Mnemonic(language="english")
            if MNEMONIC.check(mnemonic):  # check that seed is valid
                logger.info("Imported seed is valid.")
                if passphrase is not None:
                    if passphrase in ["", " ", "Type your passphrase here"]:  # todo?
                        logger.error("Passphrase is blank or empy")
                        self.view.show('WARNING',
                                       'Wrong passphrase: incorrect or blank',
                                       'Ok', None,
                                       "./pictures_db/seed_popup.jpg")
                    else:
                        seed = Mnemonic.to_seed(mnemonic, passphrase)
                        self.card_setup_native_seed(seed)
                else:
                    seed = Mnemonic.to_seed(mnemonic)
                    self.card_setup_native_seed(seed)
            else:
                logger.warning("Imported seed is invalid!")
                self.view.show('WARNING',
                               "Warning!\nInvalid BIP39 seedphrase, please retry.",
                               'Ok', None,
                               "./pictures_db/seed_popup.jpg")

        except Exception as e:
            logger.error(f"Error while importing seed: {e}")
            self.view.show("ERROR", "Failed to import seed.", "Ok", None,
                           "./pictures_db/seed_popup.jpg")

    def edit_label(self, label):
        try:
            logger.info(f"New label to set: {label}")

            if len(label.encode('utf8')) > 64:
                raise ValueError("Label should be max 64 bytes")

            (response, sw1, sw2) = self.cc.card_set_label(label)
            if sw1 == 0x90 and sw2 == 0x00:
                logger.info(f"New label set successfully: {label}")
                self.view.show("SUCCESS",
                               f"New label set successfully",
                               "Ok", self.view.show_start_frame(),
                               "./pictures_db/edit_label_popup.jpg")
            else:
                logger.warning("Failed to set new label.")
                self.view.show("ERROR", f"Failed to set label (code {hex(sw1*256+sw2)})", "oK",
                               None, "./pictures_db/edit_label_popup.jpg")

        except Exception as e:
            logger.error(f"Failed to edit label: {e}")
            self.view.show("ERROR", f"Failed to edit label: {e}", "Ok", None,
                           "./pictures_db/edit_label_popup.jpg")

    def get_card_label_infos(self):
        """Get label info"""
        if self.cc.card_present:
            response, sw1, sw2, label = self.cc.card_get_label()
            if label is None:
                logger.info("Label is None")
                return None
            if label == "":
                logger.info("Label is Blank")
                return ""
            else:
                logger.info(f"Label found: {label}")
                return label
        else:
            logger.info("In get_card_label_infos: No card present")
            return None

    # for PIN
    def PIN_dialog(self, msg):
        logger.info("Entering PIN_dialog method")

        def back_to_start_frame():
            self.view.show_start_frame()
            self.view.update_status()

        while True:
            try:
                logger.debug("Requesting PIN")
                pin = self.view.get_pin(msg)
                logger.debug(f"PIN received: pin={'***' if pin else None}")

                # check pin
                if not pin:
                    logger.info("PIN request cancelled or window closed")
                    #raise ValueError("Device cannot be unlocked without PIN code!")
                    self.view.show(
                        'ERROR', "Device cannot be unlocked without PIN code!", 'Ok',
                        lambda: None,
                        "./pictures_db/change_pin_popup.jpg"
                    )
                    return
                elif len(pin) < 4:
                    logger.warning("PIN length is less than 4 characters")
                    raise ValueError("PIN must have at least 4 characters.")
                elif len(pin) > 16:
                    logger.warning("PIN length is more than 16 characters")
                    raise ValueError("PIN must have maximum 16 characters.")

                # verify pin (can throw PinBlockedError or WrongPinError)
                pin = pin.encode('utf8')
                self.cc.card_verify_PIN_simple(pin)
                return

            except PinBlockedError as e:
                logger.error(f"Critical error: Pin blocked: {e}")
                self.view.show(
                    'ERROR',
                    "Too many wrong PIN! \nYour card has been blocked.",
                    'Ok', lambda: back_to_start_frame(),
                    "./pictures_db/change_pin_popup.jpg"
                )
                return

            except Exception as e:
                logger.info(f"Exception from PIN dialog: {e}")
                self.view.show(
                    'ERROR', str(e), 'Ok',
                    lambda: None,
                    "./pictures_db/change_pin_popup.jpg"
                )

    # only for satochip and seedkeeper
    def card_setup_native_pin(self, pin):
        try:
            logger.info("In card_setup_native_pin")
            logger.info("Setting up card pin and applet references")

            pin_0 = list(pin.encode('utf8'))
            pin_tries_0 = 0x05
            ublk_tries_0 = 0x01
            ublk_0 = list(urandom(16))  # PUK code
            pin_tries_1 = 0x01
            ublk_tries_1 = 0x01
            pin_1 = list(urandom(16))  # Second pin
            ublk_1 = list(urandom(16))
            secmemsize = 32  # Number of slots reserved in memory cache
            memsize = 0x0000  # RFU
            create_object_ACL = 0x01  # RFU
            create_key_ACL = 0x01  # RFU
            create_pin_ACL = 0x01  # RFU

            logger.info("Sending setup native pin command to card")
            (response, sw1, sw2) = self.cc.card_setup(pin_tries_0, ublk_tries_0, pin_0, ublk_0,
                                                      pin_tries_1, ublk_tries_1, pin_1, ublk_1,
                                                      secmemsize, memsize,
                                                      create_object_ACL, create_key_ACL, create_pin_ACL)
            logger.info(f"Response from card: {response}, sw1: {hex(sw1)}, sw2: {hex(sw2)}")

            if sw1 != 0x90 or sw2 != 0x00:
                logger.warning(f"Unable to set up applet! sw12={hex(sw1)} {hex(sw2)}")
                self.view.show('ERROR', f"Unable to set up applet! sw12={hex(sw1)} {hex(sw2)}")
                return False
            else:
                logger.info("Applet setup successfully")
                self.view.update_status()
                self.view.show_start_frame()
                self.view.show_menu_frame()
                self.view.show(
                    'SUCCESS', 'Your card is now setup!', 'Ok',
                    lambda: None,
                    "./pictures_db/home_popup.jpg"
                )
        except Exception as e:
            logger.error(f"An error occurred in card_setup_native_pin: {e}", exc_info=True)

    # only for satochip
    def card_setup_native_seed(self, seed):
        # verify pin
        self.view.update_verify_pin()
        # get authentikey
        try:
            authentikey = self.cc.card_bip32_get_authentikey()
        except UninitializedSeedError:
            # seed dialog...
            authentikey = self.cc.card_bip32_import_seed(seed)
            logger.info(f"authentikey: {authentikey}")
            if authentikey:
                self.view.show('SUCCESS',
                               'Your card is now seeded!',
                               'Ok',
                               lambda: None,
                               "./pictures_db/seed_popup.jpg")
                self.view.update_status()
                self.view.show_start_frame()
                self.view.show_menu_frame()

                hex_authentikey = authentikey.get_public_key_hex()
                logger.info(f"Authentikey={hex_authentikey}")
            else:
                self.view.show('ERROR', 'Error when importing seed to Satochip!', 'Ok', None,
                               "./pictures_db/seed_popup.jpg")

    ####################################################################################################################
    """MY SECRETS MANAGEMENT"""
    ####################################################################################################################

    def get_card_logs(self):
        logger.debug('In get_card_logs start')

        # get raw logs from card
        logs, nbtotal_logs, nbavail_logs = self.cc.seedkeeper_print_logs()

        nblogs = nbtotal_logs if nbtotal_logs < nbavail_logs else nbavail_logs
        logs = logs[0:nblogs]
        json_logs = []
        # convert raw logs to readable data
        for log in logs:
            ins = log[0]
            id1 = log[1]
            id2 = log[2]
            result = log[3]
            if ins == 0xA1:  # encrypted or plain import? depends on value of id2
                ins = 0xA1A if (id2 == 0xFFFF) else 0xA1B
            elif ins == 0xA2:
                ins = 0xA2A if (id2 == 0xFFFF) else 0xA2B
            ins = INS_DIC.get(ins, hex(log[0]))

            id1 = '' if id1 == 0xFFFF else str(id1)
            id2 = '' if id2 == 0xFFFF else str(id2)

            if (result & 0x63C0) == 0x63C0:  # last nible contains number of pin remaining
                remaining_tries = (result & 0x000F)
                result = f'PIN failed - {remaining_tries} tries remaining'
            else:
                result = RES_DIC.get(log[3], hex(log[3]))

            json_logs.append({
                "Operation": ins,
                "ID1": id1,
                "ID2": id2,
                "Result": result
            })

        # Convert to JSON string
        json_string = json.dumps(json_logs)
        logger.debug(f"JSON formatted logs: {json_string}")

        logger.debug(json_logs)
        logger.debug(nbtotal_logs)
        logger.debug(nbavail_logs)

        return nbtotal_logs, nbavail_logs, json_logs

    def seedkeeper_reset_secret(self, sid):
        logger.debug(f"delete secret with id: {sid}")
        try:

            # for v1, secret deletion is not supported
            if self.card_status.get('protocol_version') < 2:
                raise ValueError("Secret deletion is not supported on Seedkeeper v0.1!")

            # no need to verify PIN, it has already been done previously
            response, sw1, sw2, dic = self.cc.seedkeeper_reset_secret(sid)
            if sw1 == 0x90 and sw2 == 0x00:
                # remove secret from secret_headers
                if self.view.secret_headers is not None:
                    self.view.secret_headers = [d for d in self.view.secret_headers if d.get('id') != sid]
                    self.view.seedkeeper_secret_headers_need_update = True

                self.view.show(
                    "SUCCESS",
                    f"Secret deleted successfully\nID: {sid}",
                    "Ok",
                    self.view.show_seedkeeper_list_secrets(),
                    "./pictures_db/generate_popup.png"  # todo change icon
                )
            elif sw1 == 0x9C and sw2 == 0x08:
                self.view.show(
                    "ERROR",
                    f"Secret not found (code 0x9C08)",
                    "Ok",
                    self.view.show_seedkeeper_list_secrets(),
                    "./pictures_db/generate_popup.png"  # todo change icon
                )
            else:
                raise UnexpectedSW12Error(
                    f"Unexpected error during object deletion (error code {hex(256 * sw1 + sw2)})")
        except Exception as ex:
            logger.error(f"failed to delete secret with sid {sid}: {str(ex)}")
            self.view.show(
                "ERROR",
                f"Failed to delete secret with sid {sid}.\n{str(ex)}",
                "Ok",
                self.view.show_seedkeeper_list_secrets(),
                "./pictures_db/generate_popup.png"  # todo change icon
            )

    ####################################################################################################################
    """ DECODING SECRETS """
    ####################################################################################################################

    # generic method
    def decode_secret(self, secret: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug(f"Secret type: {TYPE_DIC.get(secret['type'], 'Unknown type')} and subtype: {secret['subtype']}")
        if secret['type'] == TYPE_PASSWORD:
            return self.decode_password(secret)
        elif secret['type'] == TYPE_MASTERSEED:
            if secret['subtype'] == 0x00:
                return self.decode_masterseed(secret)
            else:
                return self.decode_masterseed_mnemonic(secret)
        elif secret['type'] == TYPE_BIP39_MNEMONIC:
            return self.decode_mnemonic(secret)
        elif secret['type'] == TYPE_ELECTRUM_MNEMONIC:
            return self.decode_mnemonic(secret)
        elif secret['type'] == TYPE_DESCRIPTOR:
            return self.decode_descriptor(secret)
        elif secret['type'] == TYPE_DATA:
            return self.decode_data(secret)
        elif secret['type'] == TYPE_2FA_SECRET:
            return self.decode_2fa(secret)
        elif secret['type'] == TYPE_PUBKEY:
            return self.decode_pubkey(secret)
        else:
            return self.decode_default(secret)

    def decode_password(self, secret_dict: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Decoding password secret")
        result = secret_dict
        try:
            # Initialiser les champs
            result['password'] = ''
            result['login'] = ''
            result['url'] = ''

            # raw secret field
            # [password_size(1b) | password_bytes | login_size(1b) | login_bytes | url_size(1b) | url_bytes ]
            secret_bytes = binascii.unhexlify(secret_dict['secret'])
            offset = 0
            password_size = secret_bytes[offset]
            offset += 1
            password_bytes = secret_bytes[offset:offset + password_size]
            result['password_bytes'] = password_bytes
            try:
                result['password'] = result['secret_decoded'] = password_bytes.decode('utf-8')
            except Exception as e:
                logger.error(f"Error during password decoding: {str(e)}")
                result['password'] = result['secret_decoded'] = f"error during utf8 decoding: {password_bytes.hex()}"
            offset += password_size

            # login
            if offset < len(secret_bytes):
                login_size = secret_bytes[offset]
                offset += 1
                if login_size > 0 and (offset + login_size) <= len(secret_bytes):
                    login_bytes = secret_bytes[offset:offset + login_size]
                    result['login'] = login_bytes.decode('utf-8')
                    offset += login_size

            # url
            if offset < len(secret_bytes):
                url_size = secret_bytes[offset]
                offset += 1
                if url_size > 0 and (offset + url_size) <= len(secret_bytes):
                    url_bytes = secret_bytes[offset:offset + url_size]
                    result['url'] = url_bytes.decode('utf-8')
                else:
                    result['url'] = ""
                offset += url_size
            else:
                result['url'] = ""

            return result

        except Exception as e:
            error_msg = f"Error decoding password secret: {str(e)}"
            logger.error(error_msg)
            return result

    def decode_mnemonic(self, secret_dict: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Decoding mnemonic secret")
        result = secret_dict
        try:
            # Initialiser les champs
            secret_bytes = binascii.unhexlify(secret_dict['secret'])
            offset = 0
            mnemonic_size = secret_bytes[offset]
            offset += 1
            mnemonic_bytes = secret_bytes[offset:offset + mnemonic_size]
            result['mnemonic'] = result['secret_decoded'] = mnemonic_bytes.decode('utf-8')
            offset += mnemonic_size
            passphrase_size = secret_bytes[offset] if offset < len(secret_bytes) else 0
            offset += 1
            if passphrase_size > 0 and (offset + passphrase_size) <= len(secret_bytes):
                passphrase_bytes = secret_bytes[offset:offset + passphrase_size]
                result['passphrase'] = passphrase_bytes.decode('utf-8')
            else:
                result['passphrase'] = ""

            return result
        except Exception as e:
            error_msg = f"Error decoding password secret: {str(e)}"
            logger.error(error_msg)
            return result

    def decode_masterseed_mnemonic(self, secret_dict: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Decoding masterseed mnemonic secret")
        result = secret_dict
        try:
            # Initialiser les champs
            secret_bytes = binascii.unhexlify(secret_dict['secret'])
            offset = 0
            masterseed_size = secret_bytes[offset]
            offset += 1
            masterseed_bytes = secret_bytes[offset:offset + masterseed_size]
            result['masterseed_bytes'] = masterseed_bytes
            result['masterseed'] = result['secret_decoded'] = masterseed_bytes.hex()
            offset += masterseed_size

            # wordlist selector
            result['wordlist_selector'] = secret_bytes[offset]
            offset += 1

            # entropy
            entropy_size = secret_bytes[offset]
            offset += 1
            result['entropy'] = secret_bytes[offset:offset + entropy_size]
            offset += entropy_size

            # Mnemonic recovery from entropy
            if result['entropy']:
                mnemonic_instance = Mnemonic("english")  # TODO use according to wordlist_selector!
                result['mnemonic'] = mnemonic_instance.to_mnemonic(result['entropy'])

            # passphrase
            if offset < len(secret_bytes):
                passphrase_size = secret_bytes[offset]
                offset += 1
                if passphrase_size > 0 and (offset + passphrase_size) <= len(secret_bytes):
                    passphrase_bytes = secret_bytes[offset:offset + passphrase_size]
                    result['passphrase'] = passphrase_bytes.decode('utf-8')
                else:
                    result['passphrase'] = ""
                offset += passphrase_size
            else:
                result['passphrase'] = ""

            # descriptor
            # Extract the descriptor size (first 2 bytes)
            if (offset + 2) <= len(secret_bytes):
                descriptor_size = int.from_bytes(secret_bytes[offset:offset+2], byteorder='big')
                logger.debug(f"Decoded descriptor size: {descriptor_size}")
                offset += 2

                # Extract and decode the raw descriptor bytes
                if (offset + descriptor_size) <= len(secret_bytes):
                    descriptor_bytes = secret_bytes[offset:offset+descriptor_size]
                    try:
                        result['descriptor'] = descriptor_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        result['descriptor'] = descriptor_bytes.hex()
            else:
                logger.debug(f"No descriptor field")
                result['descriptor'] = ""

            return result
        except Exception as e:
            error_msg = f"Error decoding password secret: {str(e)}"
            logger.error(error_msg)
            return result

    def decode_masterseed(self, secret_dict: Dict[str, Any]) -> Dict[str, Any]:
        result = self.decode_1byte_secret(secret_dict)
        result["masterseed"] = result["secret_decoded"]
        return result

    def decode_2fa(self, secret_dict: Dict[str, Any]) -> Dict[str, Any]:
        result = self.decode_1byte_secret(secret_dict)
        result["secret2fa"] = result["secret_decoded"]
        return result

    def decode_pubkey(self, secret_dict: Dict[str, Any]) -> Dict[str, Any]:
        result = self.decode_1byte_secret(secret_dict)
        result["pubkey"] = result["secret_decoded"]
        return result

    def decode_data(self, secret_dict: Dict[str, Any]) -> Dict[str, Any]:
        result = self.decode_2bytes_secret(secret_dict)
        result["data"] = result["secret_decoded"]
        return result

    def decode_descriptor(self, secret_dict: Dict[str, Any]) -> Dict[str, Any]:
        result = self.decode_2bytes_secret(secret_dict)
        result["descriptor"] = result["secret_decoded"]
        return result

    "Decoding simple secrets with 1bytes size, like Pubkey, Masterseed & 2FA"
    def decode_1byte_secret(self, secret_dict: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("decode_1byte_secret")
        result = secret_dict
        try:
            # Initialiser les champs
            secret_bytes = binascii.unhexlify(secret_dict['secret'])
            offset = 0
            secret_size = secret_bytes[offset]
            offset += 1
            secret1b_bytes = secret_bytes[offset:offset + secret_size]
            result['secret_bytes'] = secret1b_bytes
            result['secret_decoded'] = secret1b_bytes.hex()

            return result
        except Exception as e:
            error_msg = f"Unexpected error during 1byte secret decoding: {str(e)}"
            logger.error(error_msg)
            result['secret_decoded'] = error_msg
            return result

    "Decoding secrets with 2bytes size, like Data & Descriptor"
    def decode_2bytes_secret(self, secret_dict: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("decode_2bytes_secret start")
        result = secret_dict
        try:
            # Initialiser les champs
            secret_bytes = binascii.unhexlify(secret_dict['secret'])

            # Extract the text size (first 2 bytes)
            if len(secret_bytes) < 2:
                result["secret_decoded"] = "Failed to decode data (not enough bytes)"
                return result

            secret_size = int.from_bytes(secret_bytes[:2], byteorder='big')
            logger.debug(f"Decoded text size: {secret_size}")

            # Extract and decode the raw text bytes
            secret2b_bytes = secret_bytes[2:2 + secret_size]
            try:
                result['secret_decoded'] = secret2b_bytes.decode('utf-8')
            except UnicodeDecodeError:
                result['secret_decoded'] = secret2b_bytes.hex()

            return result

        except Exception as e:
            error_msg = f"Unexpected error during 2bytes secret decoding: {str(e)}"
            logger.error(error_msg)
            result['secret_decoded'] = error_msg
            return result

    "Decoding default for unsupported secret format"
    def decode_default(self, secret_dict: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("decode_default")
        result = secret_dict
        try:
            # Initialiser les champs
            secret_bytes = binascii.unhexlify(secret_dict['secret'])
            result['secret_bytes'] = secret_bytes
            result['secret_decoded'] = secret_bytes.hex()
            return result
        except Exception as e:
            error_msg = f"Unexpected error during secret default decoding: {str(e)}"
            logger.error(error_msg)
            result['secret_decoded'] = error_msg
            return result

    ##########################
    """ IMPORTING SECRETS """
    ##########################

    def generate_random_seed(self, mnemonic_length):
        logger.info(f"generate_random_seed length {mnemonic_length}")
        strength = 128 if mnemonic_length == 12 else 256
        mnemonic = Mnemonic("english").generate(strength=strength)
        return mnemonic

    def import_password(self, label: str, password: str, login: str, url: str = None):
        logger.info("import_password start")

        # perform some checks
        # exceptions should be managed in the calling method
        if not label:
            raise ValueError("The label field is mandatory.")
        if not password:
            raise ValueError("No password provided!")

        if len(label.encode('utf-8')) > 127:
            logger.debug(f"Label is too long (max 127 bytes):  {len(label.encode('utf-8'))}")
            raise ValueError("Label is too long (max 127 bytes)!")

        if len(password.encode('utf-8')) > 255:
            raise ValueError("Password is too long (max 255 bytes)!")

        if login:
            if len(login.encode('utf-8')) > 255:
                raise ValueError("Login is too long (max 255 bytes)!")

        if url:
            if len(url.encode('utf-8')) > 255:
                raise ValueError("Url is too long (max 255 bytes)!")

        # encode secret
        secret_encoded = bytes([len(password.encode('utf-8'))]) + password.encode('utf-8')
        if login != "":
            secret_encoded += bytes([len(login.encode('utf-8'))]) + login.encode('utf-8')
        if url != "":
            secret_encoded += bytes([len(url.encode('utf-8'))]) + url.encode('utf-8')

        # for v1, secret size is limited to 255 bytes
        if self.card_status.get('protocol_version') < 2:
            if len(secret_encoded) > 255:
                raise ValueError("Payload is too long for Seedkeeper v1 (max 255 bytes)!")

        # create dict object for import
        secret_type = TYPE_PASSWORD  # password
        export_rights = 0x01  # export in plaintext allowed by default
        secret_dic = {
            'header': self.cc.make_header(secret_type, export_rights, label),
            'secret_list': list(secret_encoded)
        }

        # verify PIN
        self.view.update_verify_pin()

        # import encoded secret into card
        try:
            sid, fingerprint = self.cc.seedkeeper_import_secret(secret_dic)
        except UnexpectedSW12Error as ex:
            if "0x9c01" in str(ex):  # no memory left
                raise ValueError("Not enough memory available!")
            else:
                raise

        # update secret_headers if it is already populated and set flag
        # if secret_headers is None, we will have to regenerate it completely
        if self.view.secret_headers is not None:
            secret_header = {
                'label': label,
                'type': secret_type,
                'subtype': 0x00,
                'export_rights': export_rights,
                'id': sid,
                'fingerprint': fingerprint
            }
            self.view.secret_headers = [secret_header] + self.view.secret_headers  # prepend
            self.view.seedkeeper_secret_headers_need_update = True

        logger.info(f"Password imported successfully with id: {sid} and fingerprint: {fingerprint}")

        return sid, fingerprint

    def import_masterseed_mnemonic(self, label: str, mnemonic: str, passphrase: Optional[str] = None, descriptor: Optional[str] = None):
        logger.info("001 Starting masterseed import process")

        # perform some checks
        # exceptions should be managed in the calling method
        if not label:
            raise ValueError("The label field is mandatory.")
        if not mnemonic:
            raise ValueError("No mnemonic provided!")

        if len(label.encode('utf-8')) > 127:
            raise ValueError("Label is too long (max 127 bytes)!")

        if passphrase:
            if len(passphrase.encode('utf-8')) > 255:
                raise ValueError("Passphrase is too long (max 255 bytes)!")

        if descriptor:
            if len(descriptor.encode('utf-8')) > 65535:
                raise ValueError("descriptor is too long (max 65535 bytes)!")

        # Validate the mnemonic
        # mnemonic = mnemonic.strip()
        # word_count = len(mnemonic.split())
        # if word_count not in [12, 24]:
        #     raise ValueError(f"002 Invalid mnemonic word count: {word_count}. Must be 12 or 24.")

        # Verify mnemonic validity
        MNEMONIC = Mnemonic("english")
        if not MNEMONIC.check(mnemonic):
            raise ValueError("Invalid mnemonic")

        # Generate entropy from mnemonic
        entropy = MNEMONIC.to_entropy(mnemonic)

        # Generate seed
        salt = "mnemonic" + (passphrase or "")
        seed = hashlib.pbkdf2_hmac("sha512", mnemonic.encode("utf-8"), salt.encode("utf-8"), 2048)

        # Prepare the secret data
        wordlist_selector = 0x00  # english
        entropy_list = list(entropy)
        seed_list = list(seed)
        passphrase_list = list(passphrase.encode('utf-8')) if passphrase else []
        descriptor_list = list(descriptor.encode('utf-8')) if descriptor else []

        secret_list = (
                [len(seed_list)] +
                seed_list +
                [wordlist_selector] +
                [len(entropy_list)] +
                entropy_list +
                [len(passphrase_list)] +
                passphrase_list +
                list(len(descriptor_list).to_bytes(2, byteorder='big')) +
                descriptor_list
        )

        # for v1, secret size is limited to 255 bytes
        if self.card_status.get('protocol_version') < 2:
            if len(secret_list) > 255:
                raise ValueError("Payload is too long for Seedkeeper v1 (max 255 bytes)!")

        # Prepare the header
        secret_type = TYPE_MASTERSEED
        export_rights = 0x01  # SECRET_EXPORT_ALLOWED
        subtype = 0x01  # SECRET_SUBTYPE_BIP39

        secret_dic = {
            'header': self.cc.make_header(secret_type, export_rights, label, subtype=subtype),
            'secret_list': secret_list
        }

        # verify PIN
        self.view.update_verify_pin()

        # Import the secret
        try:
            sid, fingerprint = self.cc.seedkeeper_import_secret(secret_dic)
        except UnexpectedSW12Error as ex:
            if "0x9c01" in str(ex):  # no memory left
                raise ValueError("Not enough memory available!")
            else:
                raise

        # update secret_headers if it is already populated and set flag
        # if secret_headers is None, we will have to regenerate it completely
        if self.view.secret_headers is not None:
            secret_header = {
                'label': label,
                'type': secret_type,
                'subtype': 0x01,
                'export_rights': export_rights,
                'id': sid,
                'fingerprint': fingerprint
            }
            self.view.secret_headers = [secret_header] + self.view.secret_headers  # prepend
            self.view.seedkeeper_secret_headers_need_update = True

        logger.info(f"Masterseed imported successfully with id: {sid} and fingerprint: {fingerprint}")
        return sid, fingerprint

    def import_data(self, label: str, data: str):
        logger.info("import_data start")

        # Validate input
        if not label:
            raise ValueError("Label is required")
        if not data:
            raise ValueError("Data is required")

        # Prepare the secret data
        secret_type = TYPE_DATA
        secret_subtype = 0x00  # SECRET_SUBTYPE_DEFAULT
        export_rights = 0x01  # SECRET_EXPORT_ALLOWED

        # Encode the data
        data_bytes = data.encode('utf-8')
        data_size = len(data_bytes)
        secret_list = list(data_size.to_bytes(2, byteorder='big')) + list(data_bytes)

        # for v1, secret size is limited to 255 bytes
        if self.card_status.get('protocol_version') < 2:
            if len(secret_list) > 255:
                raise ValueError("Payload is too long for Seedkeeper v1 (max 255 bytes)!")

        # Prepare the secret dictionary
        secret_dic = {
            'header': self.cc.make_header(secret_type, export_rights, label, subtype=secret_subtype),
            'secret_list': secret_list
        }

        # Import the secret
        try:
            sid, fingerprint = self.cc.seedkeeper_import_secret(secret_dic)
        except UnexpectedSW12Error as ex:
            if "0x9c01" in str(ex):  # no memory left
                raise ValueError("Not enough memory available!")
            else:
                raise

        # update secret_headers if it is already populated and set flag
        # if secret_headers is None, we will have to regenerate it completely
        if self.view.secret_headers is not None:
            secret_header = {
                'label': label,
                'type': secret_type,
                'subtype': secret_subtype,
                'export_rights': export_rights,
                'id': sid,
                'fingerprint': fingerprint
            }
            self.view.secret_headers = [secret_header] + self.view.secret_headers  # prepend
            self.view.seedkeeper_secret_headers_need_update = True

        logger.info(f"Data imported successfully with id: {sid} and fingerprint: {fingerprint}")
        return sid, fingerprint

    def import_wallet_descriptor(self, label: str, wallet_descriptor: str):
        logger.info("Starting import of wallet descriptor")

        # Validate input
        if not label:
            raise ValueError("Label is required")
        if not wallet_descriptor:
            raise ValueError("Wallet descriptor is required")

        # Prepare the secret data
        secret_type = TYPE_DESCRIPTOR
        secret_subtype = 0x00  # SECRET_SUBTYPE_DEFAULT
        export_rights = 0x01  # SECRET_EXPORT_ALLOWED

        # Encode the wallet descriptor
        descriptor_bytes = wallet_descriptor.encode('utf-8')
        descriptor_size = len(descriptor_bytes)
        secret_list = list(descriptor_size.to_bytes(2, byteorder='big')) + list(descriptor_bytes)

        if descriptor_size > 65535:  # 2^16 - 1, max value for 2 bytes
            raise ValueError("Wallet descriptor is too long (max 65535 bytes)")

        # for v1, secret size is limited to 255 bytes
        if self.card_status.get('protocol_version') < 2:
            if len(secret_list) > 255:
                raise ValueError("Payload is too long for Seedkeeper v1 (max 255 bytes)!")

        # Prepare the secret dictionary
        secret_dic = {
            'header': self.cc.make_header(secret_type, export_rights, label, subtype=secret_subtype),
            'secret_list': secret_list
        }

        # Import the secret
        try:
            sid, fingerprint = self.cc.seedkeeper_import_secret(secret_dic)
        except UnexpectedSW12Error as ex:
            if "0x9c01" in str(ex):  # no memory left
                raise ValueError("Not enough memory available!")
            else:
                raise

        # update secret_headers if it is already populated and set flag
        if self.view.secret_headers is not None:
            # if secret_headers is None, we will have to regenerate it completely
            secret_header = {
                'label': label,
                'type': secret_type,  # todo unify 'type' entry (either str or byte)
                'subtype': secret_subtype,
                'export_rights': export_rights,
                'id': sid,
                'fingerprint': fingerprint
            }
            self.view.secret_headers = [secret_header] + self.view.secret_headers  # prepend
            self.view.seedkeeper_secret_headers_need_update = True

        logger.info(f"Wallet descriptor imported successfully with id: {sid} and fingerprint: {fingerprint}")
        return id, fingerprint

    def import_pubkey(self, label: str, pubkey_bytes: bytes):
        logger.info("import_pubkey start")

        # Validate input
        if label:
            if len(label.encode('utf-8')) > 127:
                raise ValueError("Label is too long (max 127 bytes)!")
        else:
            raise ValueError("The label field is mandatory")

        if pubkey_bytes:
            if len(pubkey_bytes) > 255:
                raise ValueError("Pubkey is too long (max 255 bytes)!")
        else:
            raise ValueError("Pubkey is required")

        # Prepare the secret data
        secret_type = TYPE_PUBKEY
        secret_subtype = 0x00  # SECRET_SUBTYPE_DEFAULT
        export_rights = 0x01  # SECRET_EXPORT_ALLOWED

        # Encode the pubkey
        # pubkey_bytes should be in uncompressed format
        secret_encoded = bytes([len(pubkey_bytes)]) + pubkey_bytes

        # Prepare the secret dictionary
        secret_dic = {
            'header': self.cc.make_header(secret_type, export_rights, label, subtype=secret_subtype),
            'secret_list': list(secret_encoded)
        }

        # Import the secret
        try:
            sid, fingerprint = self.cc.seedkeeper_import_secret(secret_dic)
        except UnexpectedSW12Error as ex:
            if "0x9c01" in str(ex):  # no memory left
                raise ValueError("Not enough memory available!")
            else:
                raise

        # update secret_headers if it is already populated and set flag
        # if secret_headers is None, we will have to regenerate it completely
        if self.view.secret_headers is not None:
            secret_header = {
                'label': label,
                'type': secret_type,
                'subtype': secret_subtype,
                'export_rights': export_rights,
                'id': sid,
                'fingerprint': fingerprint
            }
            self.view.secret_headers = [secret_header] + self.view.secret_headers  # prepend
            self.view.seedkeeper_secret_headers_need_update = True

        logger.info(f"Pubkey imported successfully with id: {sid} and fingerprint: {fingerprint}")
        return sid, fingerprint

