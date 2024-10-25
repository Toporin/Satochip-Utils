import logging
import sys
from colorama import Fore, Back, Style, init
import functools

# Initialize colorama
init(autoreset=True)

# Add a new logging level
SUCCESS = 25  # between WARNING and INFO
logging.addLevelName(SUCCESS, 'SUCCESS')


def success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS):
        self._log(SUCCESS, message, args, **kwargs)


def list_all_loggers():
    root_logger = logging.getLogger()
    print("Root Logger Handlers:", root_logger.handlers)
    for name, logger in logging.root.manager.loggerDict.items():
        if isinstance(logger, logging.Logger):
            print(
                f"Logger: {name} - Handlers: {logger.handlers} - Level: {logger.level} - Propagate: {logger.propagate}")


logging.Logger.success = success


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': Style.BRIGHT + Fore.WHITE,
        'INFO': Fore.BLUE,
        'SUCCESS': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE
    }

    # Ajouter une couleur spécifique pour CardConnector
    CARD_CONNECTOR_COLOR = Back.LIGHTBLACK_EX  # Choisissez la couleur qui vous convient

    SPECIAL_LOGS = [
        "Logging card status",
        "Card presence: True",
        "Applet major version: 0",
        "Needs 2FA: False",
        "Is seeded: True",
        "Setup done: True",
        "Card type: SeedKeeper",
        "Card label: None",
        "Tries remaining: 5"
    ]

    def format(self, record):
        # Appliquer une couleur spéciale si le log provient de CardConnector
        if 'CardConnector' in record.name:
            log_color = self.CARD_CONNECTOR_COLOR
        else:
            log_color = self.COLORS.get(record.levelname, Fore.WHITE)

        # Si le message fait partie des logs spéciaux, appliquer une autre couleur
        if any(special_log in record.msg for special_log in self.SPECIAL_LOGS):
            log_color = Fore.MAGENTA

        log_fmt = f'{log_color}%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(name)s - %(funcName)s() - %(message)s{Style.RESET_ALL}'
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


def log_method(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)

        # Log entry with a distinct format
        logger.debug(f"{Fore.CYAN}▼ ENTERING IN {func.__name__.upper()} ▼{Style.RESET_ALL}")

        try:
            result = func(*args, **kwargs)

            # Log exit with a different distinct format
            logger.debug(f"{Fore.MAGENTA}▲ EXITING FROM {func.__name__.upper()} ▲{Style.RESET_ALL}")

            return result
        except Exception as e:
            # Log exception with a different color
            logger.exception(f"{Fore.RED + Back.YELLOW}! Exception in {func.__name__}: {e}{Style.RESET_ALL}")
            raise

    return wrapper


def setup_logging():
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(ColoredFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if '-v' in sys.argv or '--verbose' in sys.argv else logging.INFO)

    # Vérifie si le root_logger a des handlers
    if not root_logger.hasHandlers():
        root_logger.addHandler(console_handler)

    # Logs de test pour vérifier
    root_logger.debug("Debug logging is enabled")
    root_logger.info("Info logging is enabled")
    root_logger.log(SUCCESS, "Success logging is enabled")

    # Simuler un log venant de CardConnector pour vérifier la couleur
    card_connector_logger = logging.getLogger('pysatochip.CardConnector')
    card_connector_logger.info("This is a log from CardConnector")

    return root_logger.level == logging.DEBUG


def get_logger(name):
    return logging.getLogger(name)
