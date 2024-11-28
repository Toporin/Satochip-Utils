import logging
import sys
import os
import tkinter

from view import View


def get_application_path() -> str:
    """Determine and return the application path."""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


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


if (len(sys.argv) >= 2) and (sys.argv[1] in ['-v', '--verbose']):
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(name)s - %(funcName)s() - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
else:
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(name)s - %(funcName)s() - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

logging.info(f"Application path: {application_path}")

# Set working directory to application path
os.chdir(application_path)

logger = logging.getLogger(__name__)
logger.info("loglevel: " + str(logger.getEffectiveLevel()))

# Construct the path to the cert directory
cert_dir = os.path.join(application_path, 'pysatochip', 'cert')
logger.info(f"Cert directory: {cert_dir}")

# Check if the cert directory exists
if not os.path.exists(cert_dir):
    logger.error(f"Cert directory not found: {cert_dir}")
else:
    logger.info("Cert directory found")
    # Check if the cert files exist
    for cert_file in os.listdir(cert_dir):
        cert_path = os.path.join(cert_dir, cert_file)
        if os.path.isfile(cert_path):
            logger.info(f"Cert file found: {cert_path}")
        else:
            logger.warning(f"Expected cert file not found: {cert_path}")

if __name__ == '__main__':
    view = View(logger.getEffectiveLevel())
    view.resizable(False, False)
    configure_view(view)
    view.mainloop()
