import subprocess
import os
import sys
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_pyinstaller():
    try:
        pyinstaller_path = os.path.join(sys.prefix, 'Scripts', 'pyinstaller.exe')
        if not os.path.isfile(pyinstaller_path):
            raise FileNotFoundError(f"PyInstaller non trouvé : {pyinstaller_path}")

        command = [
            pyinstaller_path,
            "--onefile",
            "--name", "satochip_utils.exe",
            "--add-data", "pysatochip\\pysatochip\\cert\\*;pysatochip/pysatochip/cert",
            "--add-data", "pictures_db\\*;pictures_db",
            "--add-data", "pysatochip\\pysatochip\\CardConnector.py;pysatochip",
            "satochip_utils.py"
        ]

        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logger.info("Build Windows terminé avec succès.")
        logger.debug(f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    except Exception as e:
        logger.error(f"Erreur lors du build Windows : {e}")
        raise

if __name__ == "__main__":
    run_pyinstaller()