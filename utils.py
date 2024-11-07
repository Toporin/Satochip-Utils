import tkinter
import customtkinter
import logging

import pyqrcode

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def toggle_entry_visibility(entry: customtkinter.CTkEntry):
    try:
        current_state = entry.cget("show")
        new_state = "" if current_state == "*" else "*"
        entry.configure(show=new_state)
    except Exception as e:
        logger.error(f"018 Error toggling passphrase visibility: {e}", exc_info=True)


def toggle_textbox_visibility(textbox: customtkinter.CTkTextbox, original_text):
    try:
        textbox.configure(state='normal')
        # Obtenir le contenu actuel de la textbox
        current_text = textbox.get("1.0", "end-1c")

        if current_text == '*' * len(original_text):
            # Si la textbox contient uniquement des étoiles, afficher le texte original
            textbox.delete("1.0", "end")
            textbox.insert("1.0", original_text)
            textbox.configure(state='disabled')
        else:
            # Sinon, masquer le texte avec des étoiles
            textbox.delete("1.0", "end")
            textbox.insert("1.0", '*' * len(original_text))
            textbox.configure(state='disabled')
    except Exception as e:
        logger.error(f"018 Error toggling mnemonic visibility: {e}", exc_info=True)

def show_qr_code(qr_data: str, label: customtkinter.CTkLabel): #todo implement seedqr!!
    # Fonction pour générer et afficher le QR code
    qr = pyqrcode.create(qr_data, error='L')
    qr_xbm = qr.xbm(scale=3) #if len(mnemonic.split()) <= 12 else qr.xbm(scale=2) # todo: tune scale
    # Convertir le code XBM en image Tkinter
    qr_bmp = tkinter.BitmapImage(data=qr_xbm)
    label.configure(image=qr_bmp)
    label.image = qr_bmp  # Prévenir le garbage collection
    label.place()

