import binascii
import hashlib
import json
import logging
from os import urandom
from typing import Dict, Any, Optional
from mnemonic import Mnemonic
from pysatochip.CardConnector import (CardConnector, UninitializedSeedError, UnexpectedSW12Error, PinBlockedError)
from pysatochip.JCconstants import STATE_SEALED, STATE_UNSEALED, STATE_UNINITIALIZED, DIC_CODE_BY_ASSET, SIZE_CONTRACT, \
    SIZE_TOKENID, SIZE_DATA
from pysatochip.slip44 import DICT_SLIP44_BY_SYMBOL
from pysatochip.version import SATODIME_PROTOCOL_VERSION, SATODIME_PROTOCOL_MAJOR_VERSION, \
    SATODIME_PROTOCOL_MINOR_VERSION
from pycryptotools.coins import UnsupportedCoin, Bitcoin, BitcoinCash, Litecoin, Ethereum, EthereumClassic, \
    Counterparty, Polygon

from constants import INS_DIC, RES_DIC, TYPE_PASSWORD, TYPE_MASTERSEED, TYPE_DATA, TYPE_DESCRIPTOR, TYPE_PUBKEY, \
    TYPE_BIP39_MNEMONIC, TYPE_ELECTRUM_MNEMONIC, TYPE_2FA_SECRET, TYPE_DIC, DEBUG_ADDR, STATUS_DIC, STATUS_COLOR_DIC, \
    COIN_DICT

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DEBUG_EXPLORER = True

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

        # satodime
        self.apikeys = {}
        self.satodime_status = None
        self.satodime_nb_vaults = 0 # None?
        self.satodime_vaults_status = []
        self.satodime_vaults_event = []
        self.satodime_vaults_info = []
        self.satodime_vaults_coin_info = []
        self.satodime_vaults_asset_list = []

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

    ###########################
    """MY SECRETS MANAGEMENT"""
    ###########################

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

    ########################
    """ DECODING SECRETS """
    ########################

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

    ##########################
    """ SATODIME METHODS """
    ##########################

    def get_coin(self, key_slip44_hex: str, apikeys: dict):

        # if msb is 0, this means we use testnet
        key_slip44_list = list(bytes.fromhex(key_slip44_hex))
        is_testnet = (key_slip44_list[0] & 0x80) == 0x00
        logger.debug("In get_coin(): is_testnet: " + str(is_testnet))
        # now set msb to 1 to normalize
        key_slip44_list[0] = (key_slip44_list[0] | 0x80)
        key_slip44_hex = bytes(key_slip44_list).hex()
        logger.debug("In get_coin(): key_slip44_hex: " + key_slip44_hex)

        if key_slip44_hex == "80000000":
            coin = Bitcoin(is_testnet, apikeys=apikeys)
        elif key_slip44_hex == "80000002":
            coin = Litecoin(is_testnet, apikeys=apikeys)
        # elif key_slip44_hex == "80000003":
        #     coin = Doge(is_testnet, apikeys=apikeys)
        # elif key_slip44_hex == "80000005":
        #     coin = Dash(is_testnet, apikeys=apikeys)
        elif key_slip44_hex == "80000009":
            coin = Counterparty(is_testnet, apikeys=apikeys)
        elif key_slip44_hex == "8000003c":
            coin = Ethereum(is_testnet, apikeys=apikeys)
        elif key_slip44_hex == "8000003d":
            coin = EthereumClassic(is_testnet, apikeys=apikeys)
        # elif key_slip44_hex == "80000089":
        #     coin = RSK(is_testnet, apikeys=apikeys)
        elif key_slip44_hex == "80000091":
            coin = BitcoinCash(is_testnet, apikeys=apikeys)  # todo: convert to cashaddress?
        # elif key_slip44_hex == "80000207":
        #     coin = BinanceSmartChain(is_testnet, apikeys=apikeys)
        elif key_slip44_hex == "800003c6":
            coin = Polygon(is_testnet, apikeys=apikeys)
        else:
            coin = UnsupportedCoin(is_testnet, key_slip44_hex=key_slip44_hex)
        return coin

    def satodime_on_connect(self):
        logger.info('In satodime_on_connect()')

        # check setup
        card_info = {}
        card_info['is_owner'] = False
        card_info['is_error'] = False
        card_info['error'] = 'No error'
        card_info['about'] = 'card info are stored in this dict'  # to do!

        if (self.cc.card_present):
            # get card status
            # try:
            #     (response, sw1, sw2, d) = self.cc.card_get_status()
            # except Exception as ex:
            #     logger.warning(f"Exception during card_get_status: {ex}")
            #     msg = (f"Error while getting card status. \nTry to remove and insert the card again.")

            # get satodime status
            try:
                (response, sw1, sw2, self.satodime_status) = self.cc.satodime_get_status()
            except Exception as ex:
                logger.warning(f"Exception during satodime_get_status(): {ex}")
                # (response, sw1, sw2, satodime_status) = ([], 0x00, 0x00, {})
                self.satodime_status = {'unlock_counter': [], 'max_num_keys': 0, 'satodime_keys_status': []}

            self.satodime_nb_vaults = self.satodime_status['max_num_keys']
            self.satodime_vaults_status = self.satodime_status['satodime_keys_status']
            logger.info(f'In satodime_on_connect() self.satodime_nb_vaults: {self.satodime_nb_vaults}')
            logger.info(f'In satodime_on_connect() self.satodime_vaults_status: {self.satodime_vaults_status}')

            # logger.debug(f'In main_menu satodime_vaults_info: {self.satodime_vaults_info}')
            # logger.debug(f'In main_menu card_event_slots0: {self.card_event_slots}')

            # check version
            # if (self.cc.card_type == 'Satodime'):
            #     card_info['card_status'] = d
            #     v_supported = SATODIME_PROTOCOL_VERSION
            #     v_applet = d["protocol_version"]
            #     logger.info(
            #         f"Satodime version={v_applet} SatodimeTool supported version= {v_supported}")  # debugSatochip
            #     if (v_supported < v_applet):
            #         msg = ((
            #                    'The version of your Satodime is higher than supported by SatodimeTool. You should update SatodimeTool to ensure correct functioning!') + '\n'
            #                + f'    Satodime version: {d["protocol_major_version"]}.{d["protocol_minor_version"]}' + '\n'
            #                + f'    Supported version: {SATODIME_PROTOCOL_MAJOR_VERSION}.{SATODIME_PROTOCOL_MINOR_VERSION}')
            #         self.request('show_error', msg)

            # get authentikey TODO: only keep authentikey_comp_hex?
            try:
                self.authentikey = self.cc.card_export_authentikey()
                self.authentikey_hex = self.authentikey.get_public_key_bytes(compressed=False).hex()
                self.authentikey_comp_hex = self.authentikey.get_public_key_bytes(compressed=True).hex()
                card_info['authentikey_hex'] = self.authentikey_hex
                card_info['authentikey_comp_hex'] = self.authentikey_comp_hex
            except Exception as ex:
                msg = f"Exception during card_export_authentikey:  {ex}"
                logger.warning(msg)
                self.request('show_error', msg)
                card_info['is_error'] = True
                card_info['error'] = msg
                return card_info

            # get certificate & validation
            try:
                is_authentic, txt_ca, txt_subca, txt_device, txt_error = self.cc.card_verify_authenticity()
                card_info['is_authentic'] = is_authentic
                card_info['cert_ca'] = txt_ca
                card_info['cert_subca'] = txt_subca
                card_info['cert_device'] = txt_device
                card_info['cert_error'] = txt_error

                # TODO: message if card is not authenticated?

            except Exception as ex:
                logger.warning(f"Error while checking card authenticity: {str(ex)}")
                card_info['is_error'] = True
                card_info['error'] = repr(ex)
                return card_info

            # return true if wizard finishes correctly
            return card_info

        else:
            # no card present
            self.satodime_vaults_info = []
            card_info['is_error'] = True
            card_info['error'] = "No card found. Please insert card"
            return card_info

    def satodime_vaults_get_info(self):
        logger.info('In satodime_get_vaults_info()')

        if self.satodime_vaults_info == []:
            self.satodime_vaults_info = self.satodime_nb_vaults * [{}]
            self.satodime_vaults_coin_info = self.satodime_nb_vaults * [{}]
            self.satodime_vaults_asset_list = self.satodime_nb_vaults * [[]]

        logger.info(f'In satodime_get_vaults_info() self.satodime_vaults_info: {self.satodime_vaults_info}')
        logger.info(f'In satodime_get_vaults_info() self.satodime_nb_vaults: {self.satodime_nb_vaults}')

        # get basic info for each vault from smartcard
        for vault_nbr in range(self.satodime_nb_vaults):  # range(self.satodime_nb_vaults):
            self.satodime_vault_get_basic_info(vault_nbr)

        # get coin info from blockchain explorer
        for vault_nbr in range(self.satodime_nb_vaults):
            self.satodime_vault_get_coin_info(vault_nbr)

        # get asset info from blockchain explorer
        for vault_nbr in range(self.satodime_nb_vaults):
            self.satodime_vault_get_asset_list(vault_nbr)

    def satodime_vault_get_basic_info(self, vault_nbr):
        logger.info(f'In satodime_vault_get_basic_info vault: {vault_nbr}')

        if (self.cc.card_present):

            # get keyslot status
            try:
                (response, sw1, sw2, vault_info) = self.cc.satodime_get_keyslot_status(vault_nbr)
            except Exception as ex:
                logger.warning(f"Exception during satodime_vault_get_basic_info(): {ex}")
                vault_info = {}

            # get pubkey
            if self.satodime_vaults_status[vault_nbr] in [STATE_SEALED, STATE_UNSEALED]:
                try:
                    (response, sw1, sw2, pubkey_list, pubkey_comp_list) = self.cc.satodime_get_pubkey(
                        vault_nbr)
                    pubkey_hex = bytes(pubkey_list).hex()
                    vault_info['pubkey_hex'] = pubkey_hex
                    logger.info('PUBKEY:' + pubkey_hex)

                    # recover address from pubkey
                    key_slip44_hex = vault_info['key_slip44_hex']
                    logger.info('key_slip44_hex:' + key_slip44_hex)
                    try:
                        coin = self.get_coin(key_slip44_hex, self.apikeys)
                        vault_info['coin'] = coin
                        vault_info['name'] = coin.display_name
                        vault_info['symbol'] = coin.coin_symbol

                        if DEBUG_EXPLORER:
                            # use mockup address for testing UI
                            addr = DEBUG_ADDR.get(coin.coin_symbol, coin.pubtoaddr(bytes(pubkey_list)))
                        else:
                            addr = coin.pubtoaddr(bytes(pubkey_list))
                        logger.info('address: ' + addr)
                        vault_info['address'] = addr

                    except Exception as ex:
                        vault_info['is_error'] = True
                        vault_info['error'] = str(ex)
                        logger.warning(f'Exception with coin: {str(ex)}')

                except Exception as ex:
                    (pubkey_list, pubkey_comp_list) = None, None
                    vault_info['is_error'] = True
                    vault_info['error'] = str(ex)
                    logger.warning(f'Error in satodime_get_pubkey: {str(ex)}')

            else:  # STATE_UNINITIALIZED
                (pubkey_list, pubkey_comp_list) = None, None

            # update state with gathered info
            self.satodime_vaults_info[vault_nbr] = vault_info

        # update layout
        # logger.debug(f'In main_menu satodime_vaults_info: {self.satodime_vaults_info}')
        # logger.debug(f'In main_menu card_event_slots2: {self.card_event_slots}')
        self.card_event = False
        self.satodime_vaults_event = []  # all slots are up-to-date

    def satodime_vault_get_coin_info(self, vault_nbr):
        logger.info(f'In satodime_vault_get_coin_info vault: {vault_nbr}')

        if self.cc.card_present:
            if self.satodime_vaults_status[vault_nbr] in [STATE_SEALED, STATE_UNSEALED]:
                vault_info = self.satodime_vaults_info[vault_nbr]
                try:
                    # get previously recovered address
                    coin = vault_info['coin']
                    addr = vault_info['address']
                    # get coin_info for address
                    coin_info = coin.get_coin_info(addr)
                    self.satodime_vaults_coin_info[vault_nbr] = coin_info
                    print(f"VAULT #{vault_nbr} coin_info: {coin_info}")
                except Exception as ex:
                    logger.warning(f"Exception in satodime_vault_get_coin_info: {str(ex)}")
                    logger.warning(f"Exception in satodime_vault_get_coin_info: coin: {vault_info['coin']} addr: {vault_info['address']}")

    def satodime_vault_get_asset_list(self, vault_nbr):
        logger.info(f'In satodime_vault_get_asset_info vault: {vault_nbr}')

        if self.cc.card_present:
            if self.satodime_vaults_status[vault_nbr] in [STATE_SEALED, STATE_UNSEALED]:
                vault_info = self.satodime_vaults_info[vault_nbr]
                try:
                    # get previously recovered address
                    coin = vault_info['coin']
                    addr = vault_info['address']
                    # get coin_info for address
                    asset_list = coin.get_asset_list(addr)
                    self.satodime_vaults_asset_list[vault_nbr] = asset_list
                    print(f"VAULT #{vault_nbr} asset_list: {asset_list}")
                except Exception as ex:
                    logger.warning(f"Exception in satodime_vault_get_asset_list: {str(ex)}")
                    logger.warning(f"Exception in satodime_vault_get_asset_list: coin: {vault_info['coin']} addr: {vault_info['address']}")

    def satodime_seal_vault(self, vault_nbr, blockchain, is_testnet, entropy_bytes):
        logger.info(f'In satodime_seal_vault vault: {vault_nbr}')
        if self.cc.card_present:
            if self.satodime_vaults_status[vault_nbr] == STATE_UNINITIALIZED:
                try:
                    logger.info(f'In satodime_seal_vault vault: seal vault!')
                    if len(entropy_bytes) > 32:
                        entropy_bytes = hashlib.sha256(entropy_bytes).digest()
                    else:
                        entropy_bytes = entropy_bytes + (32 - len(entropy_bytes)) * bytes([0])
                    (response, sw1, sw2, pubkey_list, pubkey_comp_list) = self.cc.satodime_seal_key(vault_nbr, entropy_bytes)
                    # update vault state & frame
                    if sw1 == 0x90 and sw2 == 0x00:
                        logger.info(f'In satodime_seal_vault vault sealed successfully!')
                        # import blockchain meta data
                        # metadata part0
                        RFU1 = 0x00
                        RFU2 = 0x00
                        key_asset = 0x01  # 'Coin'  # use default
                        key_slip44 = COIN_DICT.get(blockchain, 0x80000000)
                        if is_testnet:
                            key_slip44 = (key_slip44 & 0x7FFFFFFF)  # set  msb to 0
                        key_slip44 = list(key_slip44.to_bytes(4, 'big'))
                        # key_contract_bytes = b''
                        key_contract = SIZE_CONTRACT * [0x00]  # use default
                        # key_tokenid = ''
                        key_tokenid = SIZE_TOKENID * [0x00]  # use default
                        try:
                            (response, sw1, sw2) = self.cc.satodime_set_keyslot_status_part0(
                                vault_nbr, RFU1, RFU2,
                                key_asset, key_slip44,
                                key_contract, key_tokenid
                            )
                        except Exception as ex:
                            logger.warning(f"Exception during satodime_set_keyslot_status_part0: {ex}")

                        # metadata part1
                        #key_data == '':
                        key_data = SIZE_DATA * [0x00] # use default
                        try:
                            (response, sw1, sw2) = self.cc.satodime_set_keyslot_status_part1(vault_nbr, key_data)
                        except Exception as ex:
                            logger.warning(f"Exception during satodime_set_keyslot_status_part1: {ex}")

                        # update state
                        self.satodime_vaults_status[vault_nbr] = STATE_SEALED
                        self.satodime_vault_get_basic_info(vault_nbr)
                        self.satodime_vault_get_coin_info(vault_nbr)
                        self.satodime_vaults_asset_list[vault_nbr] = []

                        # reset vault frame to force refresh on next view
                        self.view.satodime_vault_frames[vault_nbr] = None

                        # show popup then display vault
                        self.view.show(
                            "SUCCESS",
                            f"Vault #{vault_nbr} sealed successfully!",
                            "Ok",
                            self.view.show_satodime_vault(vault_nbr),
                            "./pictures_db/edit_label_popup.jpg" # todo
                        )

                except Exception as ex:
                    logger.warning(f"Exception in satodime_unseal_vault: {str(ex)}")

    def satodime_unseal_vault(self, vault_nbr):
        logger.info(f'In satodime_unseal_vault vault: {vault_nbr}')

        if self.cc.card_present:
            if self.satodime_vaults_status[vault_nbr] == STATE_SEALED:
                try:
                    logger.info(f'In satodime_unseal_vault vault: unseal vault!')
                    (response, sw1, sw2, entropy_list, privkey_list) = self.cc.satodime_unseal_key(vault_nbr)
                    # update vault state & frame
                    if sw1 == 0x90 and sw2 == 0x00:
                        # update state
                        self.satodime_vaults_status[vault_nbr] = STATE_UNSEALED
                        self.satodime_vaults_info[vault_nbr]['privkey_bytes'] = bytes(privkey_list)
                        self.satodime_vaults_info[vault_nbr]['entropy_bytes'] = bytes(entropy_list)
                        coin = self.satodime_vaults_info[vault_nbr]['coin']
                        self.satodime_vaults_info[vault_nbr]['wif'] = coin.encode_privkey(privkey_list)

                        # update frame
                        vault_frame = self.view.satodime_vault_frames[vault_nbr]
                        # status_str = STATUS_DIC.get(STATE_UNSEALED, 'unknown')
                        # status_color = STATUS_COLOR_DIC.get(STATE_UNSEALED, 'black')
                        # vault_frame.vaultcard.status_value.configure(
                        #     text=status_str,
                        #     text_color=status_color,
                        # )
                        #vault_frame.update_frame(vault_nbr)
                        vault_frame.update_frame_by_status(vault_nbr, STATE_UNSEALED)

                        # show popup then display vault
                        self.view.show(
                            "SUCCESS",
                            f"Vault unsealed successfully",
                            "Ok",
                            self.view.show_satodime_vault(vault_nbr),
                            "./pictures_db/edit_label_popup.jpg"  # todo
                        )

                except Exception as ex:
                    logger.warning(f"Exception in satodime_unseal_vault: {str(ex)}")

    def satodime_reset_vault(self, vault_nbr):
        logger.info(f'In satodime_reset_vault vault: {vault_nbr}')

        if self.cc.card_present:
            if self.satodime_vaults_status[vault_nbr] == STATE_UNSEALED:
                try:
                    logger.info(f'In satodime_reset_vault vault: resetting vault!')
                    (response, sw1, sw2) = self.cc.satodime_reset_key(vault_nbr)
                    # update vault state & frame
                    if sw1 == 0x90 and sw2 == 0x00:
                        # update state
                        self.satodime_vaults_status[vault_nbr] = STATE_UNINITIALIZED
                        self.satodime_vaults_coin_info[vault_nbr] = {}
                        self.satodime_vaults_asset_list[vault_nbr] = []

                        # reset frame
                        self.view.satodime_vault_frames[vault_nbr] = None  # force refresh of frame on next view

                        # show popup then display vault
                        self.view.show(
                            "SUCCESS",
                            f"Vault reset successfully",
                            "Ok",
                            self.view.show_satodime_vault(vault_nbr),
                            "./pictures_db/edit_label_popup.jpg"  # todo
                        )

                except Exception as ex:
                    logger.warning(f"Exception in satodime_reset_vault: {str(ex)}")

    def satodime_export_privkey(self, vault_nbr) -> (bytes, bytes):
        logger.info(f'In satodime_reset_vault vault: {vault_nbr}')
        if self.cc.card_present:
            if self.satodime_vaults_status[vault_nbr] == STATE_UNSEALED:
                try:
                    (response, sw1, sw2, entropy_list, privkey_list) = self.cc.satodime_get_privkey(vault_nbr)

                    self.satodime_vaults_info[vault_nbr]['privkey_bytes'] = bytes(privkey_list)
                    self.satodime_vaults_info[vault_nbr]['entropy_bytes'] = bytes(entropy_list)
                    # privkey_bytes is the sha256(entropy_bytes)
                    # entropy_bytes_hash = hashlib.sha256(bytes(entropy_list)).digest()
                    # logger.warning(f"DEBUG: privkey_hex   {bytes(privkey_list).hex()}")
                    # logger.warning(f"DEBUG: hash(entropy) {entropy_bytes_hash.hex()}")

                    coin = self.satodime_vaults_info[vault_nbr]['coin']
                    wif = coin.encode_privkey(privkey_list)
                    self.satodime_vaults_info[vault_nbr]['wif'] = wif
                    return bytes(privkey_list), bytes(entropy_list), wif
                except Exception as ex:
                    logger.warning(f"Exception in satodime_reset_vault: {str(ex)}")



