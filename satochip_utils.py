import argparse
import logging
import os
import platform
import sys
import tkinter
from typing import Optional

import pysatochip

from utils import get_config_path
from version import VERSION
from view import View

logger = logging.getLogger(__name__)

LOG_FORMAT = '%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(name)s - %(funcName)s() - %(message)s'
LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'
LOG_FILENAME = "satotools.log"
# third-party libraries that are too verbose at DEBUG level and irrelevant for troubleshooting
# (urllib3 would also log explorer URLs, which may contain API keys)
NOISY_LOGGERS = ('PIL', 'urllib3')


def get_application_path() -> str:
    """Determine and return the application path."""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sato-Tools: manage your Satochip, Seedkeeper, Satodime and Satocash cards")
    parser.add_argument('-v', '--verbose', action='store_true', help="enable debug logs")
    parser.add_argument('-l', '--log-file', nargs='?', const='', default=None, metavar='PATH',
                        help=f"also write logs to PATH (default: ~/.satotools/{LOG_FILENAME} for executables, "
                             f"{LOG_FILENAME} in the source directory otherwise)")
    # parse_known_args: ignore extra args added by the OS (e.g. '-psn_*' on macOS)
    args, _ = parser.parse_known_args()
    return args


def setup_logging(verbose: bool, log_file: Optional[str]) -> None:
    """Configure logging for the whole application (root logger and pysatochip).

    Module loggers (including pysatochip's) stay at NOTSET and inherit the root level.
    log_file must be an absolute path, as the working directory changes afterwards.
    """
    level = logging.DEBUG if verbose else logging.INFO
    handlers = []
    # sys.stderr is None in windowed executables (pyinstaller console=False on Windows)
    if sys.stderr is not None:
        handlers.append(logging.StreamHandler())
    file_error = None
    if log_file:
        try:
            handlers.append(logging.FileHandler(log_file, mode='a', encoding='utf-8'))
        except OSError as ex:
            file_error = ex
    if not handlers:
        handlers.append(logging.NullHandler())
    logging.basicConfig(level=level, format=LOG_FORMAT, datefmt=LOG_DATEFMT, handlers=handlers)
    pysatochip.set_log_level(level)
    for name in NOISY_LOGGERS:
        logging.getLogger(name).setLevel(logging.INFO)

    logger.debug(f"Sato-Tools {VERSION} - Python {platform.python_version()} - {platform.platform()} - "
                f"frozen: {getattr(sys, 'frozen', False)} - loglevel: {logging.getLevelName(level)}")
    if file_error is not None:
        logger.warning(f"Cannot write logs to file {log_file}: {file_error}")
    elif log_file:
        logger.info(f"Logging to file: {log_file}")


def resolve_log_file(log_file_arg: Optional[str]) -> Optional[str]:
    """Return the absolute path of the log file, or None if file logging is disabled."""
    if log_file_arg is None:
        return None
    if log_file_arg == '':
        # same directory as the config file (the app dir is a temp dir in executables)
        if getattr(sys, 'frozen', False):
            return os.path.join(os.path.dirname(get_config_path()), LOG_FILENAME)
        return os.path.join(get_application_path(), LOG_FILENAME)
    return os.path.abspath(os.path.expanduser(log_file_arg))


def log_uncaught_exception(exc_type, exc_value, exc_traceback) -> None:
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


def log_tk_callback_exception(exc_type, exc_value, exc_traceback) -> None:
    # exceptions raised in tkinter callbacks bypass sys.excepthook
    logger.error("Unhandled exception in Tk callback", exc_info=(exc_type, exc_value, exc_traceback))


def check_cert_dir(application_path: str) -> None:
    cert_dir = os.path.join(application_path, 'pysatochip', 'cert')
    logger.info(f"Cert directory: {cert_dir}")
    if not os.path.exists(cert_dir):
        logger.error(f"Cert directory not found: {cert_dir}")
        return
    logger.info("Cert directory found")
    for cert_file in os.listdir(cert_dir):
        cert_path = os.path.join(cert_dir, cert_file)
        if os.path.isfile(cert_path):
            logger.info(f"Cert file found: {cert_path}")
        else:
            logger.warning(f"Expected cert file not found: {cert_path}")


def configure_view(view: View) -> None:
    """Configure the view properties."""
    logger.info("Setting window properties")
    view.resizable(False, False)
    view.title("Satochip Tools")

    # Add these lines to set the window icon
    #icon_path = os.path.join(get_application_path(), "satochip_utils.ico")
    icon_path = os.path.join(get_application_path(), "satochip_utils.png")
    if os.path.exists(icon_path):
        #view.iconbitmap(icon_path)
        view.iconphoto(False, tkinter.PhotoImage(file=icon_path))
    else:
        logger.warning(f"Icon file not found: {icon_path}")


def main() -> None:
    args = parse_args()
    # resolve the log file path before changing the working directory
    setup_logging(args.verbose, resolve_log_file(args.log_file))
    sys.excepthook = log_uncaught_exception

    application_path = get_application_path()
    logger.info(f"Application path: {application_path}")
    # Set working directory to application path
    os.chdir(application_path)
    check_cert_dir(application_path)

    view = View()
    view.report_callback_exception = log_tk_callback_exception
    configure_view(view)
    view.mainloop()


if __name__ == '__main__':
    main()
