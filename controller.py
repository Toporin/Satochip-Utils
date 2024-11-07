import binascii
import logging
from os import urandom
import sys
from typing import Dict, Any, List

from mnemonic import Mnemonic
from pysatochip.CardConnector import (CardConnector, UninitializedSeedError)

from exceptions import ControllerError, SecretProcessingError, SecretRetrievalError
from log_config import log_method, SUCCESS

seed = None
if (len(sys.argv) >= 2) and (sys.argv[1] in ['-v', '--verbose']):
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(name)s - %(funcName)s() - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
else:
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(name)s - %(funcName)s() - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Controller:

    dic_type = { # todo: move in pysatochip?
        0x10: 'Masterseed',
        0x30: 'BIP39 mnemonic',
        0x40: 'Electrum mnemonic',
        0x50: 'Shamir Secret Share',
        0x60: 'Private Key',
        0x70: 'Public Key',
        0x71: 'Authenticated Public Key',
        0x80: 'Symmetric Key',
        0x90: 'Password',
        0x91: 'Master Password',
        0xA0: 'Certificate',
        0xB0: '2FA secret',
        0xC0: 'Free text',
        0xC1: 'Wallet descriptor'
    }

    def __init__(self, cc, view, loglevel=logging.INFO):
        logger.setLevel(loglevel)
        self.view = view
        self.view.controller = self

        try:
            self.cc = CardConnector(self, loglevel=loglevel)
            logger.info("CardConnector initialized successfully.")
        except Exception as e:
            logger.error("Failed to initialize CardConnector.", exc_info=True)
            raise

        # card infos
        self.card_status = None

    def get_card_status(self): #todo deprecate?
        if self.cc.card_present:
            logger.info("In get_card_status")
            try:
                response, sw1, sw2, self.card_status = self.cc.card_get_status()
                if self.card_status:
                    logger.debug(f"Card satus: {self.card_status}")
                else:
                    logger.error(f"Failed to retrieve card_status")

                self.card_status['applet_full_version_string'] = f"{self.card_status['protocol_major_version']}.{self.card_status['protocol_minor_version']}-{self.card_status['applet_major_version']}.{self.card_status['applet_minor_version']}"
                return self.card_status

            except Exception as e:
                logger.error(f"Failed to retrieve card status: {e}")
                self.card_status = None
                return None

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

    def generate_random_seed(self, mnemonic_length):
        try:
            logger.info(f"In generate_random_seed(), mnemonic_length: {mnemonic_length}")
            strength = 128 if mnemonic_length == 12 else 256 if mnemonic_length == 24 else None

            if strength:
                MNEMONIC = Mnemonic(language="english")
                mnemonic = MNEMONIC.generate(strength=strength)
                return mnemonic
            else:
                logger.warning(f"generate_random_seed: invalid mnemonic length {mnemonic_length}")
                return f"Error: invalid mnemonic length {mnemonic_length}"

        except Exception as e:
            logger.error(f"generate_random_seed: Error generating seed: {e}")
            return f"Exception: {e}"

    def import_seed(self, mnemonic, passphrase =None):
        """Import a seed (and optional passphrase) into a Satochip"""
        try:
            MNEMONIC = Mnemonic(language="english")
            if MNEMONIC.check(mnemonic):  # check that seed is valid
                logger.info("Imported seed is valid.")
                if passphrase is not None:
                    if passphrase in ["", " ", "Type your passphrase here"]:
                        logger.error("Passphrase is blank or empy")
                        self.view.show('WARNING', 'Wrong passphrase: incorrect or blank', 'Ok')
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
        try:
            logger.info("Entering PIN_dialog method")

            def switch_unlock_to_false_and_quit():
                self.view.show_start_frame()
                self.view.update_status()

            while True:
                try:
                    logger.debug("Requesting PIN")
                    pin = self.view.get_passphrase(msg)
                    logger.debug(f"PIN received: pin={'***' if pin else None}")

                    if pin is None:
                        logger.info("PIN request cancelled or window closed")
                        self.view.show("INFO",
                                       'Device cannot be unlocked without PIN code!',
                                       'Ok',
                                       lambda: switch_unlock_to_false_and_quit(),
                                       "./pictures_db/change_pin_popup.jpg")
                        break

                    elif len(pin) < 4:
                        logger.warning("PIN length is less than 4 characters")
                        msg = "PIN must have at least 4 characters."
                        self.view.show("INFO", msg, 'Ok', None,
                                       "./pictures_db/change_pin_popup.jpg")
                    elif len(pin) > 16:
                        logger.warning("PIN length is more than 16 characters")
                        msg = "PIN must have maximum 16 characters."
                        self.view.show("INFO", msg, 'Ok', None,
                                       "./pictures_db/change_pin_popup.jpg")
                    else:
                        logger.info("PIN length is valid")
                        pin = pin.encode('utf8')
                        try:
                            self.cc.card_verify_PIN_simple(pin)
                            break
                        except Exception as e:
                            logger.info(f"exception from PIN dialog: {e}")
                            self.view.show('ERROR', str(e), 'Ok', None,
                                           "./pictures_db/change_pin_popup.jpg")

                except Exception as e:
                    logger.error(f"An error occurred while requesting PIN: {e}", exc_info=True)

        except Exception as e:
            logger.critical(f"An unexpected error occurred in PIN_dialog: {e}", exc_info=True)

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
                self.setup_done = True
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
        # get authentikey
        try:
            authentikey = self.cc.card_bip32_get_authentikey()
        except UninitializedSeedError:
            # seed dialog...
            authentikey = self.cc.card_bip32_import_seed(seed)
            logger.info(f"authentikey: {authentikey}")
            if authentikey:
                self.is_seeded = True
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
    @log_method
    def retrieve_secrets_stored_into_the_card(self) -> Dict[str, Any]:
        try:
            headers = self.cc.seedkeeper_list_secret_headers()
            logger.log(SUCCESS, f"Secrets retrieved successfully: {headers}")
            return self._format_secret_headers(headers)
        except Exception as e:
            logger.error(f"Error retrieving secrets: {e}")
            raise ControllerError(f"Failed to retrieve secrets: {e}")

    def _format_secret_headers(self, headers: List[Dict[str, Any]]) -> Dict[str, Any]:
        # todo refactor & clean
        formatted_headers = []
        for header in headers:
            formatted_header = {
                'id': int(header['id']),  # Convertir l'ID en entier
                'type': Controller.dic_type.get(header['type'], hex(header['type'])),
                'subtype': Controller.dic_type.get(header['subtype'], hex(header['subtype'])),
                'origin': Controller.dic_type.get(header['origin'], hex(header['origin'])),
                'export_rights': Controller.dic_type.get(header['export_rights'], hex(header['export_rights'])),
                'label': header['label']
            }
            formatted_headers.append(formatted_header)

        logger.debug(f"Formated headers: {formatted_headers}")
        return {
            'num_secrets': len(headers),
            'headers': formatted_headers
        }

    @log_method
    def retrieve_details_about_secret_selected(self, secret_id):

        def process_secret(secret_type, secret_value): #todo: purpose?
            logger.info("Processing secret")
            for type in Controller.dic_type:
                if type == secret_type:
                    return f"{secret_value}"

        try:
            logger.info(f"Retrieving details for secret ID: {secret_id}")
            secret_details = self.cc.seedkeeper_export_secret(secret_id)
            logger.debug(f"secret details: {secret_details}")
            logger.debug("Secret details exported from card")

            processed_secret = process_secret(secret_details['type'], secret_details['secret'])
            logger.info(f"Processed secret: {processed_secret}")

            formatted_details = {
                'label': secret_details['label'],
                'type': Controller.dic_type.get(secret_details['type'], hex(secret_details['type'])),
                'subtype': secret_details['subtype'],
                'export_rights': hex(secret_details['export_rights']),
                'secret': processed_secret
            }

            logger.log(SUCCESS, f"Secret details retrieved and processed successfully: {formatted_details}")
            return formatted_details

        except Exception as e:
            logger.error(f"Error retrieving secret details: {e}", exc_info=True)
            raise SecretRetrievalError(f"Failed to retrieve secret details: {e}") from e

    ####################################################################################################################
    """ DECODING SECRETS """
    ####################################################################################################################

    # generic method
    def decode_secret(self, secret: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug(f"Secret type: {secret['type']} and subtype: {secret['subtype']}")
        if secret['type'] == 'Password':
            return self.decode_password(secret)
        elif secret['type'] == 'Masterseed':
            if secret['subtype'] > 0 or secret['subtype'] == '0x1':
                return self.decode_masterseed_mnemonic(secret)
            else:
                return self.decode_masterseed(secret)
        elif secret['type'] == "BIP39 mnemonic":
            return self.decode_mnemonic(secret)
        elif secret['type'] == 'Electrum mnemonic':
            return self.decode_mnemonic(secret)
        elif secret['type'] == 'Wallet descriptor':
            return self.decode_descriptor(secret)
        elif secret['type'] == 'Free text':
            return self.decode_data(secret)
        elif secret['type'] == '2FA secret':
            return self.decode_2fa(secret)
        elif secret['type'] == 'Public Key':
            return self.decode_pubkey(secret)
        else:
            return self.decode_default(secret)

    def decode_password(self, secret_dict: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info("Decoding password secret")

            # Initialiser les champs
            result= secret_dict
            result['password'] = ''
            result['login'] = ''
            result['url'] = ''

            # raw secret field
            secret_bytes= binascii.unhexlify(secret_dict['secret'])

            # todo: refactor this part!!
            # Décoder le contenu complet en UTF-8
            full_content = secret_bytes.decode('utf-8')
            logger.debug(f"Full decoded content: {full_content}")

            # Séparer les parties
            parts = full_content.split('login:')

            if len(parts) > 1:
                # Le mot de passe est la première partie
                result['password'] = parts[0].strip()

                # Traiter le reste
                remaining = parts[1]
                login_url_parts = remaining.split('url:')

                if len(login_url_parts) > 1:
                    result['login'] = login_url_parts[0].strip()
                    result['url'] = login_url_parts[1].strip()
                else:
                    result['login'] = remaining.strip()
            else:
                # Si 'login:' n'est pas trouvé, tout est considéré comme mot de passe
                result['password'] = full_content.strip()

            # Remplacer 'None' par une chaîne vide
            for key in result:
                if result[key] == 'None':
                    result[key] = ''

            return result
        except Exception as e:
            logger.error(f"Error decoding password secret: {str(e)}")

    @log_method
    def decode_password_old(self, result: Dict[str, Any], secret_bytes: bytes) -> Dict[str, Any]:
        # todo clean args and remove secret bytes?
        try:
            logger.info("Decoding password secret")

            # Initialiser les champs
            result['password'] = ''
            result['login'] = ''
            result['url'] = ''

            # Décoder le contenu complet en UTF-8
            full_content = secret_bytes.decode('utf-8')
            logger.debug(f"Full decoded content: {full_content}")

            # Séparer les parties
            parts = full_content.split('login:')

            if len(parts) > 1:
                # Le mot de passe est la première partie
                result['password'] = parts[0].strip()

                # Traiter le reste
                remaining = parts[1]
                login_url_parts = remaining.split('url:')

                if len(login_url_parts) > 1:
                    result['login'] = login_url_parts[0].strip()
                    result['url'] = login_url_parts[1].strip()
                else:
                    result['login'] = remaining.strip()
            else:
                # Si 'login:' n'est pas trouvé, tout est considéré comme mot de passe
                result['password'] = full_content.strip()

            # Remplacer 'None' par une chaîne vide
            for key in result:
                if result[key] == 'None':
                    result[key] = ''

            logger.debug(f"Decoded password secret: {result}")
            return result
        except Exception as e:
            logger.error(f"Error decoding password secret: {str(e)}")
            raise ValueError(f"Failed to decode password secret: {str(e)}") from e

    def decode_mnemonic(self, secret_dict: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info("Decoding mnemonic secret")
            result = secret_dict
            # Initialiser les champs
            secret_bytes = binascii.unhexlify(secret_dict['secret'])
            offset = 0
            mnemonic_size = secret_bytes[offset]
            offset += 1
            mnemonic_bytes= secret_bytes[offset:offset + mnemonic_size]
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
            logger.error(f"Error decoding password secret: {str(e)}")

    def decode_masterseed_mnemonic(self, secret_dict: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info("Decoding masterseed mnemonic secret")
            result = secret_dict
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

            # passphrase
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
                result['descriptor'] = ""

            return result
        except Exception as e:
            logger.error(f"Error decoding password secret: {str(e)}")

    @log_method
    def decode_masterseed_old(self, secret_dict: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info("Starting masterseed decoding process")
            logger.debug(f"Secret dictionary provided: {secret_dict}")

            # Mapping des types de secrets de chaîne à valeur hexadécimale
            secret_type_mapping = {
                "Masterseed": 0x10,
                "BIP39 mnemonic": 0x30,
                "Electrum mnemonic": 0x40
            }

            result = {
                'type': secret_type_mapping.get(secret_dict['type']),
                'subtype': secret_dict.get('subtype', 0x00),  # Default subtype if not provided
                'masterseed': b'',
                'mnemonic': '',
                'passphrase': '',
                'entropy': b'',
                'wordlist_selector': None
            }

            if result['type'] is None:
                raise ValueError(f"Unsupported secret type: {secret_dict['type']}")

            logger.debug(f"Initial result dictionary: {result}")

            # Convertir la chaîne hexadécimale du secret en bytes
            try:
                logger.debug(f"Secret_dict['secret'] before secret_bytes: {secret_dict['secret']}")
                secret_bytes = binascii.unhexlify(secret_dict['secret'])
                logger.debug(f"Secret bytes: {(secret_bytes)}")
            except binascii.Error:
                raise ValueError("Invalid hexadecimal string provided for secret")

            offset = 0

            if result['type'] == 0x10:  # SECRET_TYPE_MASTER_SEED
                logger.debug(f"Decoding SECRET_TYPE_MASTER_SEED with subtype: {hex(result['subtype'])}")

                if result['subtype'] in [0x00, 0x01]:  # DEFAULT or BIP39
                    logger.debug(f"Subtype is default or BIP39: {hex(result['subtype'])}")
                    masterseed_size = secret_bytes[offset]
                    offset += 1
                    result['masterseed'] = secret_bytes[offset:offset + masterseed_size]

                    if result['subtype'] == 0x00:  # default masterseed:
                        result['masterseed'] = secret_bytes[offset:].hex()

                    logger.debug(
                        f"The masterseed: {result['masterseed']} had been store into result_dict['masterseed']")
                    offset += masterseed_size

                    if result['subtype'] == 0x01:  # BIP39
                        result['wordlist_selector'] = secret_bytes[offset]
                        offset += 1

                        entropy_size = secret_bytes[offset]
                        offset += 1
                        result['entropy'] = secret_bytes[offset:offset + entropy_size]
                        offset += entropy_size

                        # Génération de la mnemonic à partir de l'entropie
                        # Mnemonic generation from entripy
                        if result['entropy']:
                            mnemonic_instance = Mnemonic(
                                "english")  # Utiliser le sélecteur de liste pour d'autres langues si nécessaire
                            result['mnemonic'] = mnemonic_instance.to_mnemonic(result['entropy'])
                            result['masterseed'] = secret_bytes[1:offset - (entropy_size + 2)].hex()
                            logger.debug(f"Generated Mnemonic: {result['mnemonic']} {result['masterseed']}")

                        logger.debug(f"secret_bytes length: {len(secret_bytes)}")
                        logger.debug(f"offset value: {offset}")
                        logger.debug(f"secret_bytes content: {secret_bytes.hex()}")

                        passphrase_size = secret_bytes[offset]
                        offset += 1
                        if passphrase_size > 0:
                            result['passphrase'] = secret_bytes[offset:offset + passphrase_size].decode('utf-8')
                else:
                    raise ValueError(f"Unknown subtype for SECRET_TYPE_MASTER_SEED: {hex(result['subtype'])}")

            elif result['type'] in [0x30, 0x40]:  # SECRET_TYPE_BIP39_MNEMONIC or SECRET_TYPE_ELECTRUM_MNEMONIC
                logger.debug(f"Decoding {'BIP39_MNEMONIC' if result['type'] == 0x30 else 'ELECTRUM_MNEMONIC'}")

                if result['subtype'] == 0x00:  # SECRET_SUBTYPE_DEFAULT
                    mnemonic_size = secret_bytes[offset]
                    offset += 1
                    result['mnemonic'] = secret_bytes[offset:offset + mnemonic_size]
                    offset += mnemonic_size

                    passphrase_size = secret_bytes[offset] if offset < len(secret_bytes) else 0
                    offset += 1
                    if passphrase_size > 0 and offset < len(secret_bytes):
                        result['passphrase'] = secret_bytes[offset:offset + passphrase_size]
                else:
                    raise ValueError(f"Unknown subtype for BIP39/ELECTRUM_MNEMONIC: {hex(result['subtype'])}")

            else:
                raise ValueError(f"Unsupported secret type for masterseed: {hex(result['type'])}")

            # Vérification de la mnémonique
            if result['mnemonic']:
                mnemonic = result['mnemonic']
                mnemonic_instance = Mnemonic("english")  # Nous supposons l'anglais par défaut
                if not mnemonic_instance.check(mnemonic):
                    logger.debug(f"Maybe mnemonic: {mnemonic} is electrum only")

            logger.info("Masterseed successfully decoded")
            logger.debug(f"Decoded: {result}")
            return result

        except ValueError as e:
            logger.error(f"Validation error during masterseed decoding: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during masterseed decoding: {str(e)}")
            raise ControllerError(f"Failed to decode masterseed: {str(e)}") from e

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

    @log_method
    def decode_free_text_old(self, secret_dict: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info("Starting free text decoding process")
            logger.debug(f"Secret dictionary provided: {secret_dict}")

            result = {
                'type': secret_dict['type'],
                'label': secret_dict['label'],
                'text': ''
            }

            # Convert the hexadecimal string of the secret to bytes
            try:
                secret_bytes = binascii.unhexlify(secret_dict['secret'])
                logger.debug(f"Secret bytes: {secret_bytes.hex()}")
            except binascii.Error:
                raise ValueError("Invalid hexadecimal string provided for secret")

            # Extract the text size (first 2 bytes)
            if len(secret_bytes) < 2:
                raise ValueError("Secret is too short to contain size information")
            text_size = int.from_bytes(secret_bytes[:2], byteorder='big')
            logger.debug(f"Decoded text size: {text_size}")

            # Extract and decode the raw text bytes
            raw_text_bytes = secret_bytes[2:]
            if len(raw_text_bytes) != text_size:
                raise ValueError(
                    f"Mismatch between declared text size ({text_size}) and actual data size ({len(raw_text_bytes)})")

            try:
                decoded_text = raw_text_bytes.decode('utf-8')
                result['text'] = decoded_text
                logger.debug(f"Decoded text: {decoded_text}")
            except UnicodeDecodeError:
                raise ValueError("Failed to decode text as UTF-8")

            logger.log(SUCCESS, "Free text successfully decoded")
            return result

        except ValueError as e:
            logger.error(f"Validation error during free text decoding: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during free text decoding: {str(e)}")
            raise ControllerError(f"Failed to decode free text: {str(e)}") from e

    def decode_descriptor(self, secret_dict: Dict[str, Any]) -> Dict[str, Any]:
        result = self.decode_2bytes_secret(secret_dict)
        result["descriptor"] = result["secret_decoded"]
        return result

    @log_method
    def decode_wallet_descriptor_old(self, secret_dict: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info("Starting wallet descriptor decoding process")
            logger.debug(f"Secret dictionary provided: {secret_dict}")

            result = {
                'type': secret_dict['type'],
                'label': secret_dict['label'],
                'descriptor': ''
            }

            # Convert the hexadecimal string of the secret to bytes
            try:
                secret_bytes = binascii.unhexlify(secret_dict['secret'])
                logger.debug(f"Secret bytes: {secret_bytes.hex()}")
            except binascii.Error:
                raise ValueError("Invalid hexadecimal string provided for secret")

            # Extract the descriptor size (first 2 bytes)
            if len(secret_bytes) < 2:
                raise ValueError("Secret is too short to contain size information")
            descriptor_size = int.from_bytes(secret_bytes[:2], byteorder='big')
            logger.debug(f"Decoded descriptor size: {descriptor_size}")

            # Extract and decode the raw descriptor bytes
            raw_descriptor_bytes = secret_bytes[2:]
            if len(raw_descriptor_bytes) != descriptor_size:
                raise ValueError(
                    f"Mismatch between declared descriptor size ({descriptor_size}) and actual data size ({len(raw_descriptor_bytes)})")

            try:
                decoded_descriptor = raw_descriptor_bytes.decode('utf-8')
                result['descriptor'] = decoded_descriptor
                logger.debug(f"Decoded descriptor: {decoded_descriptor}")
            except UnicodeDecodeError:
                raise ValueError("Failed to decode descriptor as UTF-8")

            logger.log(SUCCESS, "Wallet descriptor successfully decoded")
            return result

        except ValueError as e:
            logger.error(f"Validation error during wallet descriptor decoding: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during wallet descriptor decoding: {str(e)}")
            raise ControllerError(f"Failed to decode wallet descriptor: {str(e)}") from e

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