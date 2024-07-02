import subprocess
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_pyinstaller():
    try:
        command = [
            "pyinstaller",
            "--onefile",
            "--target-arch", "universal2",
            "--name", "satochip_utils",
            "--add-data", "pictures_db/*:pictures_db",
            "--add-data", "pysatochip/cert/*:pysatochip/cert",
            "--hidden-import", "PIL._tkinter_finder",
            "satochip_utils.py"
        ]

        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logger.info("Build macOS terminé avec succès.")
        logger.debug(f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")

        # Création du DMG
        dmg_command = [
            "create-dmg",
            "--volname", "Satochip Utils",
            "--window-pos", "200", "120",
            "--window-size", "600", "300",
            "--icon-size", "100",
            "--icon", "satochip_utils", "200", "150",
            "--hide-extension", "satochip_utils",
            "--app-drop-link", "400", "150",
            "dist/Satochip_Utils.dmg",
            "dist/"
        ]

        result = subprocess.run(dmg_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logger.info("Création du DMG terminée avec succès.")
        logger.debug(f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    except Exception as e:
        logger.error(f"Erreur lors du build macOS : {e}")
        raise

if __name__ == "__main__":
    run_pyinstaller()