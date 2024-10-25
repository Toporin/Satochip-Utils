import gc
import logging
import sys
import os
import time
import tkinter
from typing import Optional, Dict, Callable, Any, Tuple

import customtkinter
from customtkinter import CTkImage
import webbrowser
from PIL import Image, ImageTk
from pysatochip.version import PYSATOCHIP_VERSION

from controller import Controller
from exceptions import MenuCreationError, MenuDeletionError, ViewError, ButtonCreationError, FrameClearingError
from log_config import SUCCESS, log_method
from version import VERSION

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

# Constants
BG_MAIN_MENU = "#21283b"
BG_BUTTON = "#e1e1e0"
BG_HOVER_BUTTON = "grey"
BUTTON_TEXT_COLOR = "white"
DEFAULT_BG_COLOR = "whitesmoke"
HIGHLIGHT_COLOR = "#D3D3D3"
MAIN_MENU_COLOR = "#202738"
BUTTON_COLOR = "#e1e1e0"
HOVER_COLOR = "grey"
TEXT_COLOR = "black"

#ICON_PATH = "./pictures_db/icon_"
ICON_PATH = "./pictures_db/"

class View(customtkinter.CTk):
    def __init__(self, loglevel=logging.INFO):
        try:
            logger.setLevel(loglevel)
            logger.debug("Log level set to INFO")
            logger.info("Starting View.__init__()")
            super().__init__()

            # status infos
            self.welcome_in_display = True

            # seedkeeper state
            self.in_backup_process = False

            try:
                logger.info("Initializing controller")
                self.controller = Controller(None, self, loglevel=loglevel)
                logger.info("Controller initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize the controller: {e}", exc_info=True)

            try:
                logger.debug("Initializing main window")
                self.main_window()
                logger.debug("Main window initialized successfully")

                logger.debug("Creating main frame")
                self.main_frame = customtkinter.CTkFrame(self, width=1000, height=600, bg_color="white",
                                                         fg_color="white")
                self.main_frame.place(relx=0.5, rely=0.5, anchor="center")
                logger.debug("Main frame created successfully")
            except Exception as e:
                logger.error(f"Failed to initialize the main window or create the main frame: {e}", exc_info=True)

            try:
                # Widget declaration -> Maybe unnecessary but marked as error if not declared before
                # TODO: clean code
                logger.debug("Declaring widgets")
                self.current_frame = None
                self.canvas = None
                self.background_photo = None
                self.create_background_photo = None
                self.header = None
                self.text_box = None
                self.button = None
                self.finish_button = None
                self.menu = None
                #self.main_menu = None
                #self.seedkeeper_menu = None
                self.counter = None
                self.display_menu = False
                logger.debug("Widgets declared successfully")
            except Exception as e:
                logger.error(f"Failed to declare widgets: {e}", exc_info=True)

            try:
                # Launching initialization starting with welcome view
                logger.debug("Launching welcome view")
                self.welcome()
                logger.debug("Welcome view launched successfully")

                self.protocol("WM_DELETE_WINDOW", lambda: [self.on_close()])
                logger.debug("WM_DELETE_WINDOW protocol set successfully")
            except Exception as e:
                logger.error(f"Failed to launch welcome view or set WM_DELETE_WINDOW protocol: {e}", exc_info=True)

            logger.info("Initialization of View.__init__() completed successfully")
        except Exception as e:
            logger.critical(f"An unexpected error occurred in __init__: {e}", exc_info=True)

    def main_window(self, width=None, height=None):
        logger.debug("IN View.main_window")
        try:
            self.title("SATOCHIP UTILS")
            logger.debug("Window title set to 'SATOCHIP UTILS'")

            window_width = 1000
            window_height = 600
            logger.debug(f"Window dimensions set to width: {window_width}, height: {window_height}")

            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            logger.debug(f"Screen dimensions obtained: width: {screen_width}, height: {screen_height}")

            center_x = int((screen_width - window_width) / 2)
            center_y = int((screen_height - window_height) / 2)
            logger.debug(f"Window position calculated: center_x: {center_x}, center_y: {center_y}")

            self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
            logger.debug("Window geometry set successfully")
        except Exception as e:
            logger.critical(f"An unexpected error occurred in main_window: {e}", exc_info=True)
        logger.debug("OUT View.main_window")

    def on_close(self):
        logger.info("IN View.on_close : Closing App")
        try:
            # Changement de l'état de l'application
            # self.app_open = False
            # logger.debug("app_open set to False")

            # Destruction de la fenêtre principale
            self.destroy()
            logger.debug("Main window destroyed")

            # Déconnexion de la carte
            self.controller.cc.card_disconnect()
            logger.debug("Card disconnected successfully")
        except Exception as e:
            logger.error(f"An unexpected error occurred in on_close: {e}", exc_info=True)
        logger.debug("OUT View.on_close")

    def restart_app(self):
        self.destroy()
        os.execl(sys.executable, sys.executable, *sys.argv)

    ##############
    """ UTILS """

    def clear_current_frame(self):
        logger.debug("In View.clear_current_frame()")
        try:
            logger.debug("Starting clear_current_frame method")

            # Helper function to log and destroy widgets
            def log_and_destroy(widget, widget_name):
                if widget:
                    try:
                        logger.debug(f"Destroying {widget_name}")
                        widget.place_forget()
                        logger.debug(f"{widget_name} destroyed successfully")
                    except Exception as e:
                        logger.warning(f"An error occurred while destroying {widget_name}: {e}", exc_info=True)
                else:
                    logger.debug(f"No {widget_name} to destroy")

            # Clear children widgets of current frame
            if self.current_frame.winfo_children():
                logger.debug("Clearing children widgets of current frame")
                for widget in self.current_frame.winfo_children():
                    try:
                        widget.place_forget()
                    except Exception as e:
                        logger.warning(f"An error occurred while destroying a child widget: {e}", exc_info=True)
                logger.debug("Children widgets cleared successfully")
            else:
                logger.debug("No children widgets to clear in current frame")

            # Destroy individual widgets
            log_and_destroy(self.header, "header widget")
            log_and_destroy(self.header, "header widget")
            log_and_destroy(self.text_box, "text box widget")
            log_and_destroy(self.current_frame, "current frame")

            logger.debug("clear_current_frame method completed successfully")
            logger.debug("OUT View.clear_current_frame")
        except Exception as e:
            logger.error(f"An unexpected error occurred in clear_current_frame: {e}", exc_info=True)


    def _clear_current_frame(self): # todo merge with clear_current_frame
        try:
            def _unbind_mousewheel():
                self.unbind_all("<MouseWheel>")
                self.unbind_all("<Button-4>")
                self.unbind_all("<Button-5>")

            _unbind_mousewheel()
            if self.app_open is True and self.current_frame is not None:
                logger.info("001 Starting current frame clearing process")
                if hasattr(self, 'current_frame') and self.current_frame:
                    for widget in self.current_frame.winfo_children():
                        widget.destroy()
                        logger.debug("002 Widget destroyed")
                    self.current_frame.destroy()
                    logger.debug("003 Current frame destroyed")
                    self.current_frame = None
                    if self.mnemonic_textbox_active is True and self.mnemonic_textbox is not None:
                        self.mnemonic_textbox.destroy()
                        self.mnemonic_textbox_active = False
                        self.mnemonic_textbox = None
                    elif self.password_text_box_active is True and self.password_text_box is not None:
                        self.password_text_box.destroy()
                        self.password_text_box_active = False
                        self.password_text_box = None
                    logger.debug("004 Current frame reference set to None")
                else:
                    pass

            # Nettoyage des attributs spécifiques
            attributes_to_clear = ['header', 'canvas', 'background_photo', 'text_box', 'button', 'finish_button',
                                   'menu']
            for attr in attributes_to_clear:
                if hasattr(self, attr):
                    attr_value = getattr(self, attr)
                    if attr_value:
                        if isinstance(attr_value, (customtkinter.CTkBaseClass, tkinter.BaseWidget)):
                            attr_value.destroy()
                            logger.debug(f"005 Attribute {attr} destroyed")
                        elif isinstance(attr_value, ImageTk.PhotoImage):
                            del attr_value
                            logger.debug(f"006 ImageTk.PhotoImage {attr} deleted")
                    setattr(self, attr, None)
                    logger.debug(f"007 Attribute {attr} set to None")

            # Réinitialisation des variables d'état si nécessaire
            self.display_menu = False
            self.counter = None
            logger.debug("008 State variables reset")

            # Forcer le garbage collector
            gc.collect()
            logger.debug("009 Garbage collection forced")

            logger.log(SUCCESS, "010 Current frame and associated objects cleared successfully")
        except Exception as e:
            logger.error(f"011 Unexpected error in _clear_current_frame: {e}", exc_info=True)
            raise FrameClearingError(f"012 Failed to clear current frame: {e}") from e

    def _clear_welcome_frame(self):
        try:
            logger.info("Starting to clear welcome frame")
            if hasattr(self, 'welcome_frame'):
                try:
                    self.welcome_frame.destroy()
                    logger.debug("frame destroyed")
                    delattr(self, 'welcome_frame')
                    logger.debug("attribute removed")
                    logger.log(SUCCESS, "Welcome frame cleared successfully")
                except Exception as e:
                    logger.error(f"Error while clearing welcome frame: {e}", exc_info=True)
                    raise FrameClearingError(f"Failed to clear welcome frame: {e}") from e
            else:
                logger.warning("No welcome frame to clear")
        except Exception as e:
            logger.error(f"Unexpected error in _clear_welcome_frame: {e}", exc_info=True)
            raise FrameClearingError(f"009 Unexpected error during welcome frame clearing: {e}") from e


    def make_text_bold(self, size=18):
        logger.debug("make_text_bold start")
        result = customtkinter.CTkFont(weight="bold", size=size)
        return result

    def make_text_size_at(self, size=18):
        logger.debug("Entering make_text_bold method")
        result = customtkinter.CTkFont(size=size)
        return result

    def create_an_header(self, title_text: str = "", icon_name: str = None, fg_bg_color=None):
        try:
            logger.debug("create_an_header start")

            # Créer le cadre de l'en-tête
            header_frame = customtkinter.CTkFrame(self, fg_color="whitesmoke", bg_color="whitesmoke", width=750, height=40)

            # Creating header with title and icon
            title_text = f"   {title_text}"
            icon_path = f"{ICON_PATH}{icon_name}"
            logger.debug(f"Loading icon from path: {icon_path}")

            # Charger et redimensionner l'image de l'icône
            image = Image.open(icon_path)
            image = image.resize((40, 40), Image.LANCZOS)
            logger.debug("Icon image resized successfully")

            # Convertir l'image en PhotoImage
            photo_image = ImageTk.PhotoImage(image)
            logger.debug("Icon image converted to PhotoImage successfully")

            # Créer le bouton avec l'image de l'icône
            button = customtkinter.CTkButton(
                header_frame, text=title_text, image=photo_image,
                font=customtkinter.CTkFont(family="Outfit", size=25,weight="bold"),
                bg_color="whitesmoke", fg_color="whitesmoke", text_color="black",
                hover_color="whitesmoke", compound="left"
            )
            button.image = photo_image  # Garder une référence de l'image
            button.place(rely=0.5, relx=0, anchor="w")

            logger.debug("create_an_header method completed successfully")
            return header_frame

        except Exception as e:
            logger.error(f"An unexpected error occurred in create_an_header: {e}", exc_info=True)

    def create_an_header_for_welcome(self, title_text: str = None, icon_name: str = None, label_text: str = None):
        icon_path = f"./pictures_db/welcome_logo.png"
        frame = customtkinter.CTkFrame(self.current_frame, width=380, height=178, bg_color='white')
        frame.place(relx=0.1, rely=0.03, anchor='nw')

        logo_canvas = customtkinter.CTkCanvas(frame, width=400, height=400, bg='black')
        logo_canvas.place(relx=0.5, rely=0.5, anchor='center')

        image = Image.open(icon_path)
        photo = ImageTk.PhotoImage(image)

        logo_canvas_width = logo_canvas.winfo_reqwidth()
        logo_canvas_height = logo_canvas.winfo_reqheight()
        image_width = photo.width()
        image_height = photo.height()

        # Calculer la position pour centrer l'image
        x_center = (logo_canvas_width - image_width) // 2
        y_center = (logo_canvas_height - image_height) // 2

        # Afficher l'image dans le canvas au centre
        logo_canvas.create_image(x_center, y_center, anchor='nw', image=photo)
        logo_canvas.image = photo

    def create_frame(self, bg_fg_color: str = "whitesmoke", width: int = 1000, height: int = 600) -> customtkinter.CTkFrame:
        logger.debug("View.create_frame() start")
        frame = customtkinter.CTkFrame(
            self.main_frame,
            width=width, height=height,
            bg_color=bg_fg_color,
            fg_color=bg_fg_color)
        return frame

    def create_label(self, text, bg_fg_color: str = "whitesmoke", frame=None) -> customtkinter.CTkLabel:
        # todo use frame
        logger.debug("view.create_label start")
        label = customtkinter.CTkLabel(
            self.current_frame,
            text=text,
            bg_color=bg_fg_color,
            fg_color=bg_fg_color,
            font=customtkinter.CTkFont(family="Outfit", size=18,weight="normal")
        )
        return label

    def create_button(self, text: str = None, command=None, frame=None) -> customtkinter.CTkButton:
        logger.debug("View.create_button() start")
        button = customtkinter.CTkButton(
            self.current_frame,
            text=text,
            width=120, height=35, corner_radius=100,
            font=customtkinter.CTkFont(family="Outfit", size=18, weight="normal"),
            bg_color='white', fg_color=MAIN_MENU_COLOR,
            hover_color=HOVER_COLOR, cursor="hand2",
            command=command)
        return button

    def create_button_for_main_menu_item(
            self,
            frame: customtkinter.CTkFrame,
            button_label: str,
            icon_name: str,
            rel_y: float,
            rel_x: float,
            state: str,
            command: Optional[Callable] = None,
            text_color: str = 'white',
    ) -> Optional[customtkinter.CTkButton]:
        logger.info(f"001 Starting main menu button creation for '{button_label}'")

        icon_path = f"{ICON_PATH}{icon_name}"
        image = Image.open(icon_path)
        image = image.resize((25, 25), Image.LANCZOS)
        photo_image = customtkinter.CTkImage(image)

        button = customtkinter.CTkButton(
            frame,
            text=button_label,
            text_color=text_color,
            font=customtkinter.CTkFont(family="Outfit", weight="normal", size=18),
            image=photo_image,
            bg_color=BG_MAIN_MENU,
            fg_color=BG_MAIN_MENU,
            hover_color=BG_MAIN_MENU,
            compound="left",
            cursor="hand2",
            command=command,
            state=state
        )
        #button.image = photo_image  # keep a reference!
        button.place(rely=rel_y, relx=rel_x, anchor="e") # todo use w anchor and revise relatives coordinates

        return button

    def create_entry(self, show_option: str = "")-> customtkinter.CTkEntry:
        logger.debug("create_entry start")
        entry = customtkinter.CTkEntry(
            self.current_frame, width=555, height=37, corner_radius=10,
            bg_color='white', fg_color=BUTTON_COLOR, border_color=BUTTON_COLOR,
            show=show_option, text_color='grey'
        )
        return entry

    def update_textbox(self, text):
        try:
            logger.debug("Entering update_textbox method")

            try:
                logger.debug("Clearing the current content of the textbox")
                self.text_box.delete(1.0, "end")  # Efface le contenu actuel
                logger.debug("Textbox content cleared")
            except Exception as e:
                logger.error(f"An error occurred while clearing the textbox content: {e}", exc_info=True)
                raise

            try:
                logger.debug("Inserting new text into the textbox")
                self.text_box.insert("end", text)
                logger.debug("New text inserted into textbox")
            except Exception as e:
                logger.error(f"An error occurred while inserting new text into the textbox: {e}", exc_info=True)
                raise

            logger.debug("Exiting update_textbox method successfully")
        except Exception as e:
            logger.error(f"An unexpected error occurred in update_textbox: {e}", exc_info=True)

    @staticmethod
    def create_background_photo(self, picture_path):
        logger.info("UTILS: View.create_background_photo() | creating background photo")
        try:
            logger.info(f"Entering create_background_photo method with path: {picture_path}")

            try:
                if getattr(sys, 'frozen', False):
                    application_path = sys._MEIPASS
                    logger.info(f"Running in a bundled application, application path: {application_path}")
                else:
                    application_path = os.path.dirname(os.path.abspath(__file__))
                    logger.info(f"Running in a regular script, application path: {application_path}")
            except Exception as e:
                logger.error(f"An error occurred while determining application path: {e}", exc_info=True)
                return None

            try:
                pictures_path = os.path.join(application_path, picture_path)
                logger.debug(f"Full path to background photo: {pictures_path}")
            except Exception as e:
                logger.error(f"An error occurred while constructing the full path: {e}", exc_info=True)
                return None

            try:
                background_image = Image.open(pictures_path)
                logger.info("Background image opened successfully")
            except FileNotFoundError as e:
                logger.error(f"File not found: {pictures_path}, {e}", exc_info=True)
                return None
            except Exception as e:
                logger.error(f"An error occurred while opening the background image: {e}", exc_info=True)
                return None

            try:
                photo_image = ImageTk.PhotoImage(background_image)
                logger.info("Background photo converted to PhotoImage successfully")
            except Exception as e:
                logger.error(f"An error occurred while converting the background image to PhotoImage: {e}",
                             exc_info=True)
                return None

            logger.info("Background photo created successfully")
            return photo_image
        except Exception as e:
            logger.error(f"An unexpected error occurred in create_background_photo: {e}", exc_info=True)
            return None

    def create_canvas(self, frame=None) -> customtkinter.CTkCanvas:
        try:
            logger.debug("UTILS: View.create_canvas() | creating canvas")
            try:
                canvas = customtkinter.CTkCanvas(self.current_frame, bg="whitesmoke", width=1000, height=599)
                logger.debug("Canvas created successfully")
            except Exception as e:
                logger.error(f"An error occurred while creating the canvas: {e}", exc_info=True)
                raise
            logger.debug("Exiting create_canvas method successfully")
            logger.debug("canvas create successfully")
            return canvas
        except Exception as e:
            logger.error(f"An unexpected error occurred in create_canvas: {e}", exc_info=True)
            return None

    def show(self, title, msg: str, button_txt="Ok", cmd=None, icon_path=None):
        try:
            logger.info(f"Show Popup  {title} {msg}")

            # Création de la fenêtre popup
            popup = customtkinter.CTkToplevel(self)
            popup.title(title)
            popup.configure(fg_color='whitesmoke')
            logger.debug("Popup window created and titled")

            # Désactiver la fermeture du popup via le bouton de fermeture standard
            popup.protocol("WM_DELETE_WINDOW", lambda: close_show())
            logger.debug("Popup close button disabled")

            popup_width = 400
            popup_height = 200

            # Rendre la fenêtre modale
            popup.transient(self)  # Set to be on top of the main window
            popup.wait_visibility() # patch _tkinter.TclError: grab failed: window not viewable
            popup.grab_set()  # Grab all events
            logger.debug("Popup set to be modal")

            # Calcul pour centrer le popup par rapport à la fenêtre principale
            position_right = int(self.winfo_screenwidth() / 2 - popup_width / 2)
            position_down = int(self.winfo_screenheight() / 2 - popup_height / 2)
            popup.geometry(f"{popup_width}x{popup_height}+{position_right}+{position_down}")
            logger.debug("Popup window centered")

            # Ajouter une icône si icon_path est défini
            if icon_path:
                icon_image = Image.open(icon_path)
                icon = customtkinter.CTkImage(light_image=icon_image, size=(30, 30))
                icon_label = customtkinter.CTkLabel(popup, image=icon, text=f"\n{msg}", compound='top',
                                                    font=customtkinter.CTkFont(family="Outfit",
                                                                               size=18,
                                                                               weight="normal"))
                icon_label.pack(pady=(20, 10))  # Ajout d'un padding différent pour l'icône
                logger.debug("Icon added to popup")
            else:
                # Ajout d'un label dans le popup
                label = customtkinter.CTkLabel(popup, text=msg,
                                               font=customtkinter.CTkFont(family="Outfit", size=14, weight="bold"))
                label.pack(pady=20)
                logger.debug("Label added to popup")

            def close_show():
                if cmd:
                    popup.destroy()
                    cmd()
                else:
                    popup.destroy()

            # Ajout d'un bouton pour fermer le popup
            self.show_button = customtkinter.CTkButton(popup, text=button_txt, fg_color=MAIN_MENU_COLOR,
                                                       hover_color=HOVER_COLOR,
                                                       bg_color='whitesmoke',
                                                       width=120, height=35, corner_radius=34,
                                                       font=customtkinter.CTkFont(family="Outfit",
                                                                                  size=18,
                                                                                  weight="normal"),
                                                       command=lambda: close_show())
            self.show_button.pack(pady=20)

            logger.debug("Button added to popup")

            logger.debug("Exiting show method successfully")

        except Exception as e:
            logger.error(f"An error occurred in show: {e}", exc_info=True)
            raise

    #################
    """ MAIN MENU """

    def main_menu(self, state=None, frame=None):
        logger.info("IN View.main_menu")
        try:
            if state is None:
                state = "normal" if self.controller.cc.card_present else "disabled"
                logger.info(f"Card {'detected' if state == 'normal' else 'undetected'}, setting state to {state}")

            menu_frame = customtkinter.CTkFrame(self.current_frame, width=250, height=600,
                                                bg_color=MAIN_MENU_COLOR,
                                                fg_color=MAIN_MENU_COLOR, corner_radius=0, border_color="black",
                                                border_width=0)
            logger.debug("Menu frame created successfully")

            # todo: cancel the function below
            def refresh_main_menu():
                try:
                    logger.info("Refreshing main menu")
                    menu_frame.destroy()
                    self.menu = self.main_menu()
                    self.menu.place(relx=0.250, rely=0.5, anchor="e")
                except Exception as e:
                    logger.error(f"An error occurred in refresh_main_menu: {e}", exc_info=True)

            # Logo section
            image_frame = customtkinter.CTkFrame(menu_frame, bg_color=MAIN_MENU_COLOR, fg_color=MAIN_MENU_COLOR,
                                                 width=284, height=126)
            image_frame.place(rely=0, relx=0.5, anchor="n")
            logo_image = Image.open("./pictures_db/logo.png")
            logo_photo = ImageTk.PhotoImage(logo_image)
            canvas = customtkinter.CTkCanvas(image_frame, width=284, height=127, bg=MAIN_MENU_COLOR,
                                             highlightthickness=0)
            canvas.pack(fill="both", expand=True)
            canvas.create_image(142, 63, image=logo_photo, anchor="center")
            canvas.image = logo_photo  # conserver une référence
            logger.debug("Logo section setup complete")

            if self.controller.cc.card_present:
                if not self.controller.cc.setup_done:
                    logger.info("Setup not done, enabling 'Setup My Card' button")
                    self.create_button_for_main_menu_item(
                        menu_frame,
                        "Setup My Card",
                        "setup_my_card.png",
                        0.26, 0.60,
                        command=lambda: self.setup_my_card_pin(), state='normal'
                    )
                else:
                    if not self.controller.cc.is_seeded and self.controller.cc.card_type != "Satodime":
                        logger.info("Card not seeded, enabling 'Setup Seed' button")
                        self.create_button_for_main_menu_item(
                            menu_frame,
                            "Setup Seed",
                            "seed.png",
                            0.26, 0.575,
                            command=lambda: self.setup_my_card_seed(), state='normal'
                        )
                    else:
                        logger.info("Setup completed, disabling 'Setup Done' button")
                        self.create_button_for_main_menu_item(
                            menu_frame,
                            "Setup Done" if self.controller.cc.card_present else 'Insert Card',
                            "setup_done.jpg" if self.controller.cc.card_present else "insert_card.jpg",
                            0.26, 0.575 if self.controller.cc.card_present else 0.595,
                            command=lambda: None, state='disabled'
                        )
            else:
                logger.info("Card not present, setting 'Setup My Card' button state")
                self.create_button_for_main_menu_item(
                    menu_frame,
                    "Insert a Card",
                    "insert_card.jpg",
                    0.26, 0.585,
                    command=lambda: None, state='normal'
                )

            if self.controller.cc.card_type != "Satodime" and self.controller.cc.setup_done:
                logger.debug("Enabling 'Change Pin' button")
                self.create_button_for_main_menu_item(
                    menu_frame,
                    "Change Pin",
                    "change_pin.png",
                    0.33, 0.57,
                    command=lambda: self.change_pin(),
                    state='normal'
                )
            else:
                logger.info(f"Card type is {self.controller.cc.card_type} | Disabling 'Change Pin' button")
                self.create_button_for_main_menu_item(
                    menu_frame,
                    "Change Pin",
                    "change_pin_locked.jpg",
                    0.33, 0.57,
                    command=lambda: self.change_pin(),
                    state='disabled'
                )

            if self.controller.cc.setup_done:
                self.create_button_for_main_menu_item(
                    menu_frame,
                    "Edit Label",
                    "edit_label.png",
                    0.40, 0.546,
                    command=lambda: [self.edit_label()], state='normal'
                )
            else:
                self.create_button_for_main_menu_item(
                    menu_frame,
                    "Edit Label",
                    "edit_label_locked.jpg",
                    0.40, 0.546,
                    command=lambda: self.edit_label(), state='disabled'
                )

            def before_check_authenticity():
                logger.info("IN View.main_menu() | Requesting card verification PIN")
                if self.controller.cc.card_type != "Satodime":
                    if self.controller.cc.is_pin_set():
                        self.controller.cc.card_verify_PIN_simple()
                    else:
                        self.controller.PIN_dialog(f'Unlock your {self.controller.cc.card_type}')

            if self.controller.cc.setup_done:
                self.create_button_for_main_menu_item(
                    menu_frame,
                    "Check Authenticity",
                    "auth.png",
                    0.47, 0.66,
                    command=lambda: [before_check_authenticity(), self.check_authenticity()], state='normal'
                )
            else:
                self.create_button_for_main_menu_item(
                    menu_frame,
                    "Check Authenticity",
                    "check_authenticity_locked.jpg",
                    0.47, 0.66,
                    command=lambda: self.check_authenticity(), state='disabled'
                )
            if self.controller.cc.card_present:
                if self.controller.cc.card_type != "Satodime":
                    self.create_button_for_main_menu_item(
                        menu_frame,
                        "Reset my Card",
                        "reset.png",
                        0.54, 0.595,
                        command=lambda: self.reset_my_card_window(), state='normal'
                    )
                else:
                    # TODO: remove button?
                    self.create_button_for_main_menu_item(
                        menu_frame,
                        "Reset my Card",
                        "reset_locked.jpg",
                        0.54, 0.595,
                        command=lambda: None, state='disabled'
                    )
                self.create_button_for_main_menu_item(
                    menu_frame,
                    "About",
                    "about.jpg",
                    rel_y=0.73, rel_x=0.5052,
                    command=lambda: self.about(), state='normal'
                )
            else:
                self.create_button_for_main_menu_item(
                    menu_frame,
                    "Reset my Card",
                    "reset_locked.jpg",
                    0.54, 0.595,
                    command=lambda: None, state='disabled'
                )
                self.create_button_for_main_menu_item(
                    menu_frame,
                    "About",
                    "about_locked.jpg",
                    rel_y=0.73, rel_x=0.5052,
                    command=lambda: self.about(), state='disabled'
                )

            self.create_button_for_main_menu_item(
                menu_frame,
                "Go to the Webshop",
                "webshop.png",
                0.95, 0.67,
                command=lambda: webbrowser.open("https://satochip.io/shop/", new=2), state='normal'
            )

            logger.info("Main menu setup complete")
            return menu_frame

        except Exception as e:
            logger.error(f"An error occurred in main_menu: {e}", exc_info=True)

    ################################
    """ SEEDKEEPER MENU """

    def create_seedkeeper_menu(self):
        try:
            logger.info("create_seedkeeper_menu start")
            menu = self._seedkeeper_lateral_menu()
            return menu
        except Exception as e:
            logger.error(f"005 Error in create_seedkeeper_menu: {e}", exc_info=True)
            raise MenuCreationError(f"006 Failed to create Seedkeeper menu: {e}") from e

    def _seedkeeper_lateral_menu(
            self,
            state=None,
            frame=None
    ) -> customtkinter.CTkFrame:
        try:
            logger.info("001 Starting Seedkeeper lateral menu creation")
            if self.menu:
                self.menu.destroy()
                logger.debug("002 Existing menu destroyed")

            if state is None:
                state = "normal" if self.controller.cc.card_present else "disabled"
                logger.info(
                    f"003 Card {'detected' if state == 'normal' else 'undetected'}, setting state to {state}")

            menu_frame = customtkinter.CTkFrame(self.main_frame, width=250, height=600,
                                                bg_color=BG_MAIN_MENU,
                                                fg_color=BG_MAIN_MENU, corner_radius=0, border_color="black",
                                                border_width=0)
            logger.debug("004 Main menu frame created")

            # Logo section
            image_frame = customtkinter.CTkFrame(menu_frame, bg_color=BG_MAIN_MENU, fg_color=BG_MAIN_MENU,
                                                 width=284, height=126)
            image_frame.place(rely=0, relx=0.5, anchor="n")
            logo_image = Image.open("./pictures_db/logo.png")
            logo_photo = ImageTk.PhotoImage(logo_image)
            canvas = customtkinter.CTkCanvas(image_frame, width=284, height=127, bg=BG_MAIN_MENU,
                                             highlightthickness=0)
            canvas.pack(fill="both", expand=True)
            canvas.create_image(142, 63, image=logo_photo, anchor="center")
            canvas.image = logo_photo  # conserver une référence
            logger.debug("005 Logo section created")

            if self.controller.cc.card_present:
                logger.log(SUCCESS, "006 Card Present")
            else:
                logger.error(f"007 Card not present")

            # Menu items
            self.create_button_for_main_menu_item(menu_frame,
                                                   "My secrets" if self.controller.cc.card_present else "Insert card",
                                                   "secrets.png" if self.controller.cc.card_present else "insert_card.jpg",
                                                   0.26, 0.585 if self.controller.cc.card_present else 0.578,
                                                   state=state,
                                                   command=self.show_view_my_secrets if self.controller.cc.card_present else None)
            self.create_button_for_main_menu_item(menu_frame, "Generate",
                                                   "generate.png" if self.controller.cc.card_present else "generate_locked.png",
                                                   0.33, 0.56, state=state,
                                                   command=self.show_view_generate_secret if self.controller.cc.card_present else None,
                                                   text_color="white" if self.controller.cc.card_present else "grey")
            self.create_button_for_main_menu_item(menu_frame, "Import",
                                                   "import.png" if self.controller.cc.card_present else "import_locked.png",
                                                   0.40, 0.51, state=state,
                                                   command=self.show_view_import_secret if self.controller.cc.card_present else None,
                                                   text_color="white" if self.controller.cc.card_present else "grey")
            self.create_button_for_main_menu_item(menu_frame, "Logs",
                                                   "logs.png" if self.controller.cc.card_present else "settings_locked.png", # todo icon when locked
                                                   0.47, 0.49, state=state,
                                                   command=self.show_view_logs if self.controller.cc.card_present else None,
                                                   text_color="white" if self.controller.cc.card_present else "grey")
            self.create_button_for_main_menu_item(menu_frame, "Settings",
                                                   "settings.png" if self.controller.cc.card_present else "settings_locked.png",
                                                   0.74, 0.546, state=state,
                                                   command=self.about if self.controller.cc.card_present else None,
                                                   text_color="white" if self.controller.cc.card_present else "grey")
            self.create_button_for_main_menu_item(menu_frame, "Help", "help.png", 0.81, 0.49, state='normal',
                                                   command=self.show_view_help, text_color="white")
            self.create_button_for_main_menu_item(menu_frame, "Go to the webshop", "webshop.png", 0.95, 0.82,
                                                   state='normal',
                                                   command=lambda: webbrowser.open("https://satochip.io/shop/",
                                                                                   new=2))
            logger.debug("008 Menu items created")
            logger.log(SUCCESS, "009 Seedkeeper lateral menu created successfully")
            return menu_frame
        except Exception as e:
            logger.error(f"010 Unexpected error in _seedkeeper_lateral_menu: {e}", exc_info=True)
            raise MenuCreationError(f"011 Failed to create Seedkeeper lateral menu: {e}") from e

    @log_method
    def _delete_seedkeeper_menu(self):
        try:
            logger.info("001 Starting Seedkeeper menu deletion")
            if hasattr(self, 'menu') and self.menu:
                self.menu.destroy()
                logger.debug("002 Menu widget destroyed")
                self.menu = None
                logger.debug("003 Menu attribute set to None")
            logger.log(SUCCESS, "004 Seedkeeper menu deleted successfully")
        except Exception as e:
            logger.error(f"005 Unexpected error in _delete_seedkeeper_menu: {e}", exc_info=True)
            raise MenuDeletionError(f"006 Failed to delete Seedkeeper menu: {e}") from e

    ####################################################################################################################
    """ METHODS TO DISPLAY A VIEW FROM SEEDKEEPER MENU SELECTION """

    # SEEDKEEPER MENU SELECTION
    @log_method
    def show_view_my_secrets(self):
        try:
            self.in_backup_process = False
            logger.info("001 Initiating show secrets process")
            self.welcome_in_display = False
            self._clear_welcome_frame()
            self._clear_current_frame()
            logger.debug("002 Welcome frame cleared")

            secrets_data = self.controller.retrieve_secrets_stored_into_the_card()
            logger.debug(f"Fetched {len(secrets_data['headers'])} headers")
            # for header in secrets_data['headers']:
            #     logger.debug(f"Header: {header}")

            # TODO why reset some pubkey??
            # card_status = self.controller.get_card_status()
            # if card_status['protocol_version'] > 1:
            #     for secret in secrets_data['headers']:
            #         if secret['type'] == "Public Key":
            #             self.controller.cc.seedkeeper_reset_secret(secret['id'])
            logger.debug("003 Secrets data retrieved from card")
            self.view_my_secrets(secrets_data)
            logger.log(SUCCESS, "004 Secrets displayed successfully")
        except Exception as e:
            logger.error(f"005 Error in show_secrets: {e}", exc_info=True)
            raise ViewError(f"006 Failed to show secrets: {e}") from e

    @log_method
    def show_view_generate_secret(self):
        try:
            self.in_backup_process = False
            logger.info("001 Initiating secret generation process")
            self.welcome_in_display = False
            logger.debug("002 Welcome frame cleared")
            self._clear_current_frame()
            self.view_generate_secret()
            logger.log(SUCCESS, "003 Secret generation process initiated")
        except Exception as e:
            logger.error(f"004 Error in show_generate_secret: {e}", exc_info=True)
            raise ViewError(f"005 Failed to show generate secret: {e}")

    @log_method
    def show_view_import_secret(self):
        try:
            self.in_backup_process = False
            logger.info("001 Initiating secret import process")
            self.welcome_in_display = False
            self._clear_current_frame()
            logger.debug("002 Welcome frame cleared")
            self.view_import_secret()
            logger.log(SUCCESS, "002 Secret import process initiated")
        except Exception as e:
            logger.error(f"003 Error in import_secret: {e}", exc_info=True)
            raise ViewError(f"004 Failed to import secret: {e}") from e

    @log_method
    def show_view_logs(self):
        self.in_backup_process = False
        total_number_of_logs, total_number_available_logs, logs = self.controller.get_logs()
        self.view_logs_details(logs)

    @log_method
    def show_view_settings(self):
        try:
            self.in_backup_process = False
            logger.info("001 Displaying settings")
            self._delete_seedkeeper_menu()
            logger.debug("002 Seedkeeper menu deleted")
            self.view_start_setup()
            logger.debug("003 Setup started")
            self.create_satochip_utils_menu()
            logger.debug("004 Satochip utils menu created")
            logger.log(SUCCESS, "005 Settings displayed successfully")
        except Exception as e:
            logger.error(f"006 Error in show_settings: {e}", exc_info=True)
            raise ViewError(f"007 Failed to show settings: {e}") from e

    @log_method
    def show_view_help(self):
        try:
            logger.info("001 Displaying help information")
            self.in_backup_process = False
            self.welcome_in_display = False
            self._clear_current_frame()
            self._clear_welcome_frame()
            logger.debug("002 Welcome and current frames cleared")
            self.view_help()
            logger.log(SUCCESS, "003 Help information displayed successfully")
        except Exception as e:
            logger.error(f"003 Error in show_help: {e}", exc_info=True)
            raise ViewError(f"004 Failed to show help: {e}") from e

    ################################
    """ UTILS FOR CARD CONNECTOR """

    def update_status(self, isConnected=None):
        try:
            if self.controller.cc.mode_factory_reset == True:
                # we are in factory reset mode
                if isConnected is True:
                    logger.info(f"Card inserted for Reset Factory!")
                    try:
                        # Mettre à jour les labels et les boutons en fonction de l'insertion de la carte
                        # self.reset_button.configure(text='Reset', state='normal')
                        self.show_button.configure(text='Reset', state='normal')
                        logger.debug("Labels and button updated for card insertion")
                    except Exception as e:
                        logger.error(f"An error occurred while updating labels and button for card insertion: {e}",
                                     exc_info=True)

                elif isConnected is False:
                    logger.info(f"Card removed for Reset Factory!")
                    try:
                        # Mettre à jour les labels et les boutons en fonction du retrait de la carte
                        self.show_button.configure(text='Insert card', state='disabled')
                        logger.debug("Labels and button updated for card removal")
                    except Exception as e:
                        logger.error(f"An error occurred while updating labels and button for card removal: {e}",
                                     exc_info=True)
                else:  # None
                    pass
            else:
                # normal mode
                logger.info("CC UTILS: View.update_status | Entering update_status method")
                if isConnected is True:
                    try:
                        logger.info("Getting card status")
                        self.controller.get_card_status()

                        if not self.welcome_in_display: # TODO?
                            self.start_setup()
                    except Exception as e:
                        logger.error(f"An error occurred while getting card status: {e}", exc_info=True)

                elif isConnected is False:
                    try:
                        logger.info("Card disconnected, resetting status")
                        self.start_setup()
                    except Exception as e:
                        logger.error(f"An error occurred while resetting card status: {e}", exc_info=True)
                    logger.info("Exiting update_status method successfully")

                else: # isConnected is None
                    pass

        except Exception as e:
            logger.error(f"An unexpected error occurred in update_status method: {e}", exc_info=True)

    def get_passphrase(self, msg):
        try:
            logger.info("CC UTILS: IN View.get_passphrase() | Creating new popup window for PIN entry")

            # Création d'une nouvelle fenêtre pour le popup
            popup = customtkinter.CTkToplevel(self)
            popup.title("PIN Required")
            popup.configure(fg_color='whitesmoke')
            popup.protocol("WM_DELETE_WINDOW", lambda: [popup.destroy()])  # Désactive le bouton de fermeture

            # Définition de la taille et position du popup
            popup_width = 400
            popup_height = 200

            position_right = int(self.winfo_screenwidth() / 2 - popup_width / 2)
            position_down = int(self.winfo_screenheight() / 2 - popup_height / 2)

            popup.geometry(f"{popup_width}x{popup_height}+{position_right}+{position_down}")
            logger.debug(
                f"Popup window geometry set to {popup_width}x{popup_height} at position ({position_right}, {position_down})")

            try:
                # Ajout d'un label avec une image dans le popup
                icon_image = Image.open("./pictures_db/change_pin_popup.jpg")
                icon = customtkinter.CTkImage(light_image=icon_image, size=(20, 20))
                icon_label = customtkinter.CTkLabel(popup, image=icon, text=f"\nEnter the PIN code of your card.",
                                                    compound='top',
                                                    font=customtkinter.CTkFont(family="Outfit",
                                                                               size=18,
                                                                               weight="normal"))
                icon_label.pack(pady=(0, 10))  # Ajout d'un padding différent pour l'icône
                logger.debug("Label added to popup")
            except Exception as e:
                logger.error(f"An error occurred while adding label to popup: {e}", exc_info=True)

            try:
                # Ajout d'un champ d'entrée
                passphrase_entry = customtkinter.CTkEntry(popup, show="*", corner_radius=10, border_width=0,
                                                          width=229, height=37,
                                                          bg_color='whitesmoke',
                                                          fg_color=BUTTON_COLOR,
                                                          text_color='grey')
                popup.after(100, passphrase_entry.focus_force)
                passphrase_entry.pack(pady=15)
                logger.debug("Entry field added to popup")
            except Exception as e:
                logger.error(f"An error occurred while adding entry field to popup: {e}", exc_info=True)

            # Variables pour stocker les résultats
            pin = None

            # Fonction pour soumettre la passphrase et fermer le popup
            def submit_passphrase():
                try:
                    nonlocal pin
                    pin = passphrase_entry.get()
                    popup.destroy()
                    logger.debug("Passphrase submitted and popup destroyed")
                except Exception as e:
                    logger.error(f"An error occurred in submit_passphrase: {e}", exc_info=True)

            try:
                # Bouton pour soumettre la passphrase
                submit_button = customtkinter.CTkButton(popup, bg_color='whitesmoke', fg_color=MAIN_MENU_COLOR,
                                                        width=120, height=35, corner_radius=34,
                                                        hover_color=HOVER_COLOR, text="Submit",
                                                        command=submit_passphrase,
                                                        font=customtkinter.CTkFont(family="Outfit",
                                                                                   size=18,
                                                                                   weight="normal")
                                                        )
                submit_button.pack(pady=10)
                logger.debug("Submit button added to popup")
            except Exception as e:
                logger.error(f"An error occurred while adding submit button to popup: {e}", exc_info=True)

            try:
                # Rendre la fenêtre modale
                popup.transient(self)  # Set to be on top of the main window
                popup.bind('<Return>', lambda event: submit_passphrase())
                logger.debug("Popup set to be on top of the main window")

                # Attendre que la fenêtre popup soit détruite
                self.wait_window(popup)
                logger.debug("Waiting for popup window to be destroyed")

                # Retourner les résultats
                logger.info(f"Returning results: pin={'****' if pin else None}")
                return pin

            except Exception as e:
                logger.error(f"An error occurred while setting popup modal behavior: {e}", exc_info=True)
                return None

        except Exception as e:
            logger.error(f"An error occurred in get_passphrase: {e}", exc_info=True)
            return None

    #############
    """ VIEWS """

    def welcome(self):
        logger.info("IN View.welcome() | Entering in the method")
        try:
            logger.debug("Entering welcome method")
            frame_name = "welcome"
            button_label = "Let's go!"

            if self.current_frame is not None:
                logger.debug("Clearing current frame")
                self.clear_current_frame()
                logger.debug("Current frame cleared")

            logger.debug("Creating new frame and background")
            self.current_frame = View.create_frame(self)
            self.current_frame.place(relx=0.5, rely=0.5, anchor="center")
            self.background_photo = View.create_background_photo(self, "./pictures_db/welcome_in_satochip_utils.png")
            self.canvas = View.create_canvas(self)
            self.canvas.place(relx=0.5, rely=0.5, anchor="center")
            self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")
            logger.debug("New frame and background created and placed")

            # self.satochip_logo = View.create_background_photo(self, "./pictures_db/icon_logo.png")
            # self.canvas_logo = View.create_canvas(self)
            # self.canvas.place(relx=0.5, rely=0.5, anchor="center")
            # self.canvas.create_image(0, 0, image=self.satochip_logo, anchor="nw")

            logger.debug("Creating header for welcome")
            self.create_an_header_for_welcome('SATOCHIP', 'welcome_logo.png', 'Secure the future.') # todo args not used remove
            logger.debug("Header created and placed")

            logger.debug("Setting up labels")
            self.label = self.create_label('Satochip-Utils\n______________', MAIN_MENU_COLOR)
            self.label.configure(text_color='white')
            self.label.configure(font=self.make_text_size_at(18))
            self.label.place(relx=0.05, rely=0.4, anchor="w")

            self.label = self.create_label('Your one stop shop to manage your Satochip cards,', MAIN_MENU_COLOR)
            self.label.configure(text_color='white')
            self.label.configure(font=self.make_text_size_at(18))
            self.label.place(relx=0.05, rely=0.5, anchor="w")

            self.label = self.create_label('including Satodime and Seedkeeper.', MAIN_MENU_COLOR)
            self.label.configure(text_color='white')
            self.label.configure(font=self.make_text_size_at(18))
            self.label.place(relx=0.05, rely=0.55, anchor="w")

            self.label = self.create_label('Change your PIN code, reset your card, setup your', MAIN_MENU_COLOR)
            self.label.configure(text_color='white')
            self.label.configure(font=self.make_text_size_at(18))
            self.label.place(relx=0.05, rely=0.65, anchor="w")

            self.label = self.create_label('hardware wallet and many more...', MAIN_MENU_COLOR)
            self.label.configure(text_color='white')
            self.label.configure(font=self.make_text_size_at(18))
            self.label.place(relx=0.05, rely=0.7, anchor="w")
            logger.debug("Labels created and placed")

            logger.debug("Creating and placing the button")
            self.button = View.create_button(self, button_label, command=lambda: [self.start_setup()])
            self.after(2500, self.button.place(relx=0.85, rely=0.93, anchor="center"))
            logger.debug("Button created and placed")

            if self.controller.cc.card_present:
                logger.info("Card present")
            else:
                logger.info("Card is not present, impossible to retrieve card status")

            logger.debug("Exiting welcome method successfully")
        except Exception as e:
            message = f"An unexpected error occurred in welcome method: {e}"
            logger.error(message, exc_info=True)
            raise Exception(message) from e

    def start_setup(self):
        logger.info("IN View.start_setup() | Entering start_setup method")
        frame_name = "start_setup"
        self.welcome_in_display = False

        try:
            if self.current_frame is not None:
                logger.info("Clearing current frame")
                self.clear_current_frame()
                logger.debug("Current frame cleared")

            logger.debug("Creating header")
            self.header = View.create_an_header(self, "Welcome", "home_popup.jpg")
            self.header.place(relx=0.32, rely=0.08, anchor="nw")
            logger.debug("Header created and placed")

            logger.debug("Creating main frame")
            self.current_frame = View.create_frame(self)
            self.current_frame.place(relx=0.5, rely=0.5, anchor="center")
            logger.debug("Main frame created and placed")

            logger.info("Loading background photo")
            if self.controller.cc.card_present:
                logger.info(f"card type: {self.controller.cc.card_type}")
                if self.controller.cc.card_type == "Satochip":
                    self.background_photo = View.create_background_photo(self, "./pictures_db/card_satochip.png")
                    logger.info("bg_photo = satochip")
                elif self.controller.cc.card_type == "SeedKeeper":
                    logger.info(f"card type is {self.controller.cc.card_type}")
                    self.background_photo = View.create_background_photo(self, "./pictures_db/card_seedkeeper.png")
                    logger.info("bg_photo = seedkeeper")
                elif self.controller.cc.card_type == "Satodime":
                    self.background_photo = View.create_background_photo(self, "./pictures_db/card_satodime.png")
            else:
                self.background_photo = View.create_background_photo(self, "./pictures_db/insert_card.png")
                logger.info("bg_photo = no card")

            self.canvas = View.create_canvas(self)
            self.canvas.place(relx=0.250, rely=0.501, anchor="w")
            self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")
            logger.debug("Background photo loaded and placed")

            logger.debug("Setting up labels")
            self.label = View.create_label(self,
                                           "Please insert your card into your smart card" if not self.controller.cc.card_present else f"Your {self.controller.cc.card_type} is connected.")
            self.label.place(relx=0.33, rely=0.27, anchor="w")

            self.label = View.create_label(self,
                                           "reader, and select the action you wish to perform." if not self.controller.cc.card_present else "Select on the menu the action you wish to perform.")
            self.label.place(relx=0.33, rely=0.32, anchor="w")
            logger.debug("Labels created and placed")

            if self.controller.cc.card_type == "SeedKeeper":
                logger.debug("Creating Seedkeeper menu")
                menu = self.create_seedkeeper_menu()
                menu.place(relx=0.250, rely=0.5, anchor="e")
                logger.debug("Seedkeeper menu created and placed")
            else:
                logger.debug("Creating main menu")
                menu = self.main_menu()
                menu.place(relx=0.250, rely=0.5, anchor="e")
                logger.debug("Main menu created and placed")

        except Exception as e:
            message = f"An unexpected error occurred in start_setup: {e}"
            logger.error(message, exc_info=True)
            raise Exception(message) from e

    # for satochip and seedkeeper card
    def setup_my_card_pin(self):
        logger.info(f"IN View.setup_my_card_pin()")
        frame_name = "setup_my_card_pin"
        cancel_button = "Cancel"
        finish_button = "Finish"

        try:
            if self.current_frame is not None:
                try:
                    logger.debug("Clearing current frame")
                    self.clear_current_frame()
                    logger.debug("Current frame cleared")
                except Exception as e:
                    logger.error(f"An error occurred while clearing current frame: {e}", exc_info=True)

            try:
                logger.debug("Creating new frame")
                self.current_frame = View.create_frame(self)
                self.current_frame.place(relx=0.5, rely=0.5, anchor="center")
                logger.debug("New frame created and placed")
            except Exception as e:
                logger.error(f"An error occurred while creating new frame: {e}", exc_info=True)

            try:
                logger.debug("Creating main menu")
                if not self.controller.cc.setup_done:
                    menu = self.main_menu('disabled')
                else:
                    menu = self.main_menu()
                menu.place(relx=0.250, rely=0.5, anchor="e")
                logger.debug("Main menu created and placed")
            except Exception as e:
                logger.error(f"An error occurred while creating main menu: {e}", exc_info=True)

            try:
                logger.debug("Creating header")
                self.header = View.create_an_header(self, f"Setup my card",
                                                    "change_pin_popup.jpg")
                self.header.place(relx=0.32, rely=0.05, anchor="nw")
                logger.debug("Header created and placed")
            except Exception as e:
                logger.error(f"An error occurred while creating header: {e}", exc_info=True)

            try:
                logger.debug("setup paragraph")
                text = View.create_label(self, "Create your personal PIN code.")
                text.place(relx=0.33, rely=0.2, anchor="w")
                text = View.create_label(self, "We strongly encourage you to set up a strong password between 4 and 16")
                text.place(relx=0.33, rely=0.25, anchor="w")
                text = View.create_label(self, "characters. You can use symbols, lower and upper cases, letters and ")
                text.place(relx=0.33, rely=0.3, anchor="w")
                text = View.create_label(self, "numbers.")
                text.place(relx=0.33, rely=0.35, anchor="w")

                logger.debug("Setting up PIN entry fields")
                # edit PIN
                edit_pin_label = View.create_label(self, "New PIN code :")
                edit_pin_label.configure(font=self.make_text_size_at(18))
                edit_pin_label.place(relx=0.33, rely=0.45, anchor="w")
                edit_pin_entry = View.create_entry(self, "*")
                self.after(100, edit_pin_entry.focus_force)
                if self.controller.cc.card_type == "Satodime":
                    edit_pin_entry.configure(state='disabled')
                edit_pin_entry.place(relx=0.327, rely=0.52, anchor="w")

                # confirm PIN edition
                edit_confirm_pin_label = View.create_label(self, "Repeat new PIN code :")
                edit_confirm_pin_label.configure(font=self.make_text_size_at(18))
                edit_confirm_pin_label.place(relx=0.33, rely=0.65, anchor="w")
                edit_confirm_pin_entry = View.create_entry(self, "*")
                if self.controller.cc.card_type == "Satodime":
                    edit_confirm_pin_entry.configure(state='disabled')
                edit_confirm_pin_entry.place(relx=0.327, rely=0.72, anchor="w")
                logger.debug("PIN entry fields created and placed")
            except Exception as e:
                logger.error(f"An error occurred while setting up PIN entry fields: {e}", exc_info=True)

            try:
                logger.debug("Creating cancel and finish buttons")
                self.cancel_button = View.create_button(self, "Cancel",
                                                        lambda: self.start_setup())
                self.cancel_button.place(relx=0.7, rely=0.9, anchor="w")

                self.finish_button = View.create_button(self, "Save PIN",
                                                        lambda: self.controller.setup_card_pin(edit_pin_entry.get(), edit_confirm_pin_entry.get()))
                self.finish_button.place(relx=0.85, rely=0.9, anchor="w")
                self.bind('<Return>', lambda event: self.controller.setup_card_pin(edit_pin_entry.get(), edit_confirm_pin_entry.get()))
                logger.debug("Cancel and finish buttons created and placed")
            except Exception as e:
                logger.error(f"An error occurred while creating cancel and finish buttons: {e}", exc_info=True)

            logger.debug("Exiting setup_my_card_pin method successfully")
        except Exception as e:
            logger.error(f"An unexpected error occurred in setup_my_card_pin: {e}", exc_info=True)

    # only for satochip card
    def setup_my_card_seed(self):
        frame_name = "setup_my_card_seed"
        try:

            if self.current_frame is not None:
                try:
                    logger.debug("Clearing current frame")
                    self.clear_current_frame()
                    logger.debug("Current frame cleared")
                except Exception as e:
                    logger.error(f"An error occurred while clearing current frame: {e}", exc_info=True)

            try:
                logger.debug("Creating new frame")
                self.current_frame = View.create_frame(self)
                self.current_frame.place(relx=0.5, rely=0.5, anchor="center")
                logger.debug("New frame created and placed")
            except Exception as e:
                logger.error(f"An error occurred while creating new frame: {e}", exc_info=True)

            try:
                logger.debug("Creating main menu")
                menu = self.main_menu(state='disabled')
                menu.place(relx=0.250, rely=0.5, anchor="e")
                logger.debug("Main menu created and placed")
            except Exception as e:
                logger.error(f"An error occurred while creating main menu: {e}", exc_info=True)

            try:
                logger.debug("Creating header")
                self.header = View.create_an_header(self, "Seed My Card", "seed_popup.jpg")
                self.header.place(relx=0.32, rely=0.05, anchor="nw")
                logger.debug("Header created and placed")
            except Exception as e:
                logger.error(f"An error occurred while creating header: {e}", exc_info=True)

            logger.debug("setup paragraph")
            text = View.create_label(self, "Set up your Satochip hardware wallet as a new device to get started.")
            text.place(relx=0.33, rely=0.17, anchor="w")
            text = View.create_label(self, "Import or generate a new mnemonic seedphrase and generate new")
            text.place(relx=0.33, rely=0.22, anchor="w")
            text = View.create_label(self, "private keys that will be stored within the chip memory.")
            text.place(relx=0.33, rely=0.27, anchor="w")

            radio_value = customtkinter.StringVar(value="")
            value_checkbox_passphrase = customtkinter.StringVar(value="off")
            radio_value_mnemonic = customtkinter.StringVar(value="")
            generate_with_passphrase = False  # use a passphrase?
            logger.debug(f"Settings radio_value: {radio_value}, generate_with_passphrase: {generate_with_passphrase}")

            def on_text_box_click(event):
                if self.text_box.get("1.0", "end-1c") == "Type your existing seedphrase here":
                    self.text_box.delete("1.0", "end")

            def update_radio_mnemonic_length():
                if radio_value_mnemonic.get() == "generate_12":
                    logger.debug("Generate seed of 12 words")
                    mnemonic_length = 12
                elif radio_value_mnemonic.get() == "generate_24":
                    logger.debug("Generate seed of 24 words")
                    mnemonic_length = 24

                mnemonic = self.controller.generate_random_seed(mnemonic_length)
                self.update_textbox(mnemonic)

            def update_radio_selection():
                nonlocal generate_with_passphrase
                self.import_seed = False

                if radio_value.get() == "import":
                    self.import_seed = True
                    logger.debug("Import seed")
                    self.cancel_button.place_forget()
                    self.finish_button.place(relx=0.85, rely=0.9, anchor="w")
                    self.cancel_button.place(relx=0.7, rely=0.9, anchor="w")
                    radio_button_generate_seed.place_forget()
                    radio_button_import_seed.place_forget()
                    radio_button_generate_12_words.place_forget()
                    radio_button_generate_24_words.place_forget()
                    passphrase_entry.place_forget()
                    self.text_box.place_forget()
                    warning_label.place_forget()
                    radio_button_import_seed.place(relx=0.33, rely=0.35, anchor="w")
                    self.text_box.delete(1.0, "end")
                    self.text_box.configure(width=550, height=80)
                    self.text_box.insert(text="Type your existing seedphrase here", index=1.0)
                    self.text_box.bind("<FocusIn>", on_text_box_click)
                    self.text_box.place(relx=0.35, rely=0.45, anchor="w")
                    checkbox_passphrase.place(relx=0.35, rely=0.58, anchor="w")
                    radio_button_generate_seed.place(relx=0.33, rely=0.75, anchor="w")

                elif radio_value.get() == "generate":
                    self.import_seed = False
                    logger.debug("Generate seed")
                    self.cancel_button.place_forget()
                    self.finish_button.place(relx=0.85, rely=0.9, anchor="w")
                    self.cancel_button.place(relx=0.7, rely=0.9, anchor="w")
                    radio_button_import_seed.place_forget()
                    radio_button_generate_seed.place_forget()
                    checkbox_passphrase.place_forget()
                    passphrase_entry.place_forget()
                    self.text_box.delete(1.0, "end")
                    self.text_box.place_forget()
                    warning_label.place_forget()
                    radio_button_import_seed.place(relx=0.33, rely=0.35, anchor="w")
                    radio_button_generate_seed.place(relx=0.33, rely=0.41, anchor="w")
                    radio_button_generate_12_words.place(relx=0.38, rely=0.47, anchor="w")
                    radio_button_generate_24_words.place(relx=0.53, rely=0.47, anchor="w")
                    self.text_box.configure(width=550, height=80)
                    self.text_box.place(relx=0.37, rely=0.56, anchor="w")
                    warning_label.place(relx=0.52, rely=0.64, anchor="w")
                    checkbox_passphrase.place(relx=0.38, rely=0.70, anchor="w")

            def update_checkbox_passphrase():
                nonlocal generate_with_passphrase
                if radio_value.get() == "import":
                    if value_checkbox_passphrase.get() == "on":
                        logger.debug("Generate seed with passphrase")
                        generate_with_passphrase = True
                        passphrase_entry.place_forget()
                        passphrase_entry.place(relx=0.35, rely=0.65, anchor="w")
                        passphrase_entry.configure(placeholder_text="Type your passphrase here")
                    else:
                        generate_with_passphrase = False
                        passphrase_entry.place_forget()

                elif radio_value.get() == "generate":
                    if value_checkbox_passphrase.get() == "on":
                        logger.debug("Generate seed with passphrase")
                        generate_with_passphrase = True
                        passphrase_entry.place_forget()
                        passphrase_entry.place(relx=0.37, rely=0.76, anchor="w")
                        passphrase_entry.configure(placeholder_text="Type your passphrase here")
                    else:
                        generate_with_passphrase = False
                        passphrase_entry.place_forget()

            def update_verify_pin():
                if self.controller.cc.is_pin_set():
                    self.controller.cc.card_verify_PIN_simple()
                else:
                    self.controller.PIN_dialog(f'Unlock your {self.controller.cc.card_type}')

            try:
                logger.debug("Setting up radio buttons and entry fields")
                radio_button_import_seed = customtkinter.CTkRadioButton(self.current_frame,
                                                                        text="I already have a seedphrase",
                                                                        variable=radio_value, value="import",
                                                                        font=customtkinter.CTkFont(family="Outfit",
                                                                                                   size=14,
                                                                                                   weight="normal"),
                                                                        bg_color="whitesmoke", fg_color="green",
                                                                        hover_color="green",
                                                                        command=update_radio_selection)
                radio_button_import_seed.place(relx=0.33, rely=0.35, anchor="w")

                radio_button_generate_seed = customtkinter.CTkRadioButton(self.current_frame,
                                                                     text="I want to generate a new seedphrase",
                                                                     variable=radio_value, value="generate",
                                                                     font=customtkinter.CTkFont(family="Outfit",
                                                                                                size=14,
                                                                                                weight="normal"),
                                                                     bg_color="whitesmoke", fg_color="green",
                                                                     hover_color="green",
                                                                     command=update_radio_selection, )
                radio_button_generate_seed.place(relx=0.33, rely=0.42, anchor="w")

                radio_button_generate_12_words = customtkinter.CTkRadioButton(self.current_frame,
                                                                              text="12 - words",
                                                                              variable=radio_value_mnemonic,
                                                                              value="generate_12",
                                                                              font=customtkinter.CTkFont(
                                                                                  family="Outfit",
                                                                                  size=14,
                                                                                  weight="normal"),
                                                                              bg_color="whitesmoke", fg_color="green",
                                                                              hover_color="green",
                                                                              command=update_radio_mnemonic_length)
                radio_button_generate_24_words = customtkinter.CTkRadioButton(self.current_frame,
                                                                              text="24 - words",
                                                                              variable=radio_value_mnemonic, value="generate_24",
                                                                              font=customtkinter.CTkFont(
                                                                                  family="Outfit",
                                                                                  size=14,
                                                                                  weight="normal"),
                                                                              bg_color="whitesmoke", fg_color="green",
                                                                              hover_color="green",
                                                                              command=update_radio_mnemonic_length)

                checkbox_passphrase = customtkinter.CTkCheckBox(self.current_frame,
                                                                text="Use a passphrase (optional)",
                                                                command=update_checkbox_passphrase,
                                                                variable=value_checkbox_passphrase,
                                                                onvalue="on",
                                                                offvalue="off")

                passphrase_entry = View.create_entry(self)

                self.text_box = customtkinter.CTkTextbox(self, corner_radius=20,
                                                         bg_color="whitesmoke", fg_color=BUTTON_COLOR,
                                                         border_color=BUTTON_COLOR, border_width=1,
                                                         width=557, height=83,
                                                         text_color="grey",
                                                         font=customtkinter.CTkFont(family="Outfit", size=13,
                                                                                    weight="normal"))

                warning_text = "Your mnemonic is important, be sure to save it in a safe place!"
                warning_label = customtkinter.CTkLabel(
                    self.current_frame,
                    text=warning_text,
                    text_color="red",
                    font=customtkinter.CTkFont(family="Outfit", size=12, weight="normal"))

                self.cancel_button = View.create_button(self, "Back",
                                                        command=lambda: self.start_setup()
                                                        )
                self.cancel_button.place(relx=0.85, rely=0.9, anchor="w")

                self.finish_button = View.create_button(self, "Import",
                                                        command=lambda: [
                                                            update_verify_pin(),
                                                            self.controller.import_seed(
                                                                self.text_box.get(1.0, "end-1c"),
                                                                passphrase_entry.get() if generate_with_passphrase else None,
                                                            )
                                                        ])
                # self.finish_button.place(relx=0.85, rely=0.9, anchor="w")
                logger.debug("Radio buttons and entry fields set up")

            except Exception as e:
                logger.error(f"An error occurred while setting up radio buttons and entry fields: {e}", exc_info=True)

            logger.debug("Exiting setup_my_card_seed method successfully")
        except Exception as e:
            logger.error(f"An unexpected error occurred in setup_my_card_seed: {e}", exc_info=True)

    def change_pin(self):
        try:
            logger.info("IN View.change_pin() | Entering change_pin method")
            if self.current_frame is not None:
                try:
                    logger.debug("Clearing current frame")
                    self.clear_current_frame()
                    logger.debug("Current frame cleared")
                except Exception as e:
                    logger.error(f"An error occurred while clearing current frame: {e}", exc_info=True)

            frame_name = "change_pin"
            try:
                logger.debug("Creating new frame")
                self.current_frame = View.create_frame(self)
                self.current_frame.place(relx=0.5, rely=0.5, anchor="center")
                logger.debug("New frame created and placed")
            except Exception as e:
                logger.error(f"An error occurred while creating new frame: {e}", exc_info=True)

            try:
                logger.debug("Creating main menu")
                menu = self.main_menu()
                menu.place(relx=0.250, rely=0.5, anchor="e")
                logger.debug("Main menu created and placed")
            except Exception as e:
                logger.error(f"An error occurred while creating main menu: {e}", exc_info=True)

            try:
                logger.debug("Creating header")
                self.header = View.create_an_header(self, "Change PIN ", "change_pin_popup.jpg")
                self.header.place(relx=0.32, rely=0.05, anchor="nw")
                logger.debug("Header created and placed")
            except Exception as e:
                logger.error(f"An error occurred while creating header: {e}", exc_info=True)

            try:
                logger.debug("setup paragraph")
                text = View.create_label(self, "Change your personal PIN code. ")
                text.place(relx=0.33, rely=0.17, anchor="w")
                text = View.create_label(self, "We strongly encourage you to set up a strong password between 4 and 16")
                text.place(relx=0.33, rely=0.22, anchor="w")
                text = View.create_label(self, "characters. You can use symbols, lower and upper cases, letters and ")
                text.place(relx=0.33, rely=0.27, anchor="w")
                text = View.create_label(self, "numbers.")
                text.place(relx=0.33, rely=0.32, anchor="w")

                logger.debug("Setting up PIN entry fields")
                # input current PIN
                current_pin_label = View.create_label(self, "Current PIN:")
                current_pin_label.configure(font=self.make_text_size_at(18))
                current_pin_label.place(relx=0.33, rely=0.40, anchor="w")
                current_pin_entry = View.create_entry(self, "*")
                self.after(100, current_pin_entry.focus_force)
                current_pin_entry.place(relx=0.33, rely=0.45, anchor="w")

                # input new PIN
                new_pin_label = View.create_label(self, "New PIN code:")
                new_pin_label.configure(font=self.make_text_size_at(18))
                new_pin_label.place(relx=0.33, rely=0.55, anchor="w")
                new_pin_entry = View.create_entry(self, "*")
                new_pin_entry.place(relx=0.33, rely=0.60, anchor="w")

                # confirm new PIN
                confirm_new_pin_label = View.create_label(self, "Repeat new PIN code:")
                confirm_new_pin_label.configure(font=self.make_text_size_at(18))
                confirm_new_pin_label.place(relx=0.33, rely=0.70, anchor="w")
                confirm_new_pin_entry = View.create_entry(self, "*")
                confirm_new_pin_entry.place(relx=0.33, rely=0.75, anchor="w")
                logger.debug("PIN entry fields created and placed")
            except Exception as e:
                logger.error(f"An error occurred while setting up PIN entry fields: {e}", exc_info=True)

            try:
                logger.debug("Creating cancel and finish buttons")
                cancel_button = View.create_button(self, "Cancel", lambda: self.start_setup())
                cancel_button.place(relx=0.7, rely=0.9, anchor="w")

                finish_button = View.create_button(self, "Change it",
                                                   lambda: self.controller.change_card_pin(current_pin_entry.get(),
                                                                                           new_pin_entry.get(),
                                                                                           confirm_new_pin_entry.get()))

                finish_button.place(relx=0.85, rely=0.9, anchor="w")
                self.bind('<Return>', lambda event: self.controller.change_card_pin(
                    current_pin_entry.get(),
                    new_pin_entry.get(),
                    confirm_new_pin_entry.get()))
                logger.debug("Cancel and finish buttons created and placed")

            except Exception as e:
                logger.error(f"An error occurred while creating cancel and finish buttons: {e}", exc_info=True)

            logger.debug("Exiting change_pin method successfully")
        except Exception as e:
            logger.error(f"An unexpected error occurred in change_pin: {e}", exc_info=True)

    def edit_label(self):
        try:
            logger.info("IN View.edit_label() | Entering edit_label method")
            frame_name = "edit_label"
            cancel_button = "Cancel"
            finish_button = "Finish"

            if self.current_frame is not None:
                try:
                    logger.debug("Clearing current frame")
                    self.clear_current_frame()
                    logger.debug("Current frame cleared")
                except Exception as e:
                    logger.error(f"An error occurred while clearing current frame: {e}", exc_info=True)

            try:
                logger.debug("Creating new frame")
                self.current_frame = View.create_frame(self)
                self.current_frame.place(relx=0.5, rely=0.5, anchor="center")
                logger.debug("New frame created and placed")
            except Exception as e:
                logger.error(f"An error occurred while creating new frame: {e}", exc_info=True)

            try:
                logger.debug("Creating main menu")
                menu = self.main_menu()
                menu.place(relx=0.250, rely=0.5, anchor="e")
                logger.debug("Main menu created and placed")
            except Exception as e:
                logger.error(f"An error occurred while creating main menu: {e}", exc_info=True)

            try:
                logger.debug("Creating header")

                header_conditional_title = "Edit Label"
                header_conditional_label = f"Find a friendly name for your {self.controller.cc.card_type} Card."

                self.header = View.create_an_header(self,
                                                    header_conditional_title,
                                                    "edit_label_popup.jpg")

                self.header.place(relx=0.32, rely=0.05, anchor="nw")
                logger.debug("Header created and placed")
            except Exception as e:
                logger.error(f"An error occurred while creating header: {e}", exc_info=True)

            try:
                logger.debug("setup paragraph")
                text = View.create_label(self, f"Edit the label of your {self.controller.cc.card_type}.")
                text.place(relx=0.33, rely=0.17, anchor="w")
                text = View.create_label(self,
                                         "The label is a tag that identifies your card. It can be used to distinguish ")
                text.place(relx=0.33, rely=0.22, anchor="w")
                text = View.create_label(self, "several cards, or to associate it with a person, a name or a story.")
                text.place(relx=0.33, rely=0.27, anchor="w")

                logger.debug("Setting up label entry fields")
                edit_card_label = View.create_label(self, "Label :")
                edit_card_label.place(relx=0.33, rely=0.4, anchor="w")
                edit_card_entry = View.create_entry(self)
                self.after(100, edit_card_entry.focus_force)

                edit_card_entry.place(relx=0.33, rely=0.45, anchor="w")
                logger.debug("Label entry fields created and placed")
            except Exception as e:
                logger.error(f"An error occurred while setting up label entry fields: {e}", exc_info=True)

            try:
                logger.debug("Creating cancel and finish buttons")
                self.cancel_button = View.create_button(self, cancel_button,
                                                        lambda: self.start_setup())

                self.cancel_button.place(relx=0.7, rely=0.9, anchor="w")

                finish_button_conditional_label = "Change it"

                self.finish_button = View.create_button(self,
                                                        finish_button_conditional_label,
                                                        lambda:
                                                        self.controller.edit_label(edit_card_entry.get()))

                self.finish_button.place(relx=0.85, rely=0.9, anchor="w")
                self.bind('<Return>', lambda event: self.controller.edit_label(edit_card_entry.get()))
                logger.debug("Cancel and finish buttons created and placed")
            except Exception as e:
                logger.error(f"An error occurred while creating cancel and finish buttons: {e}", exc_info=True)
            if self.controller.cc.card_type != "Satodime":
                logger.info("IN View.change_pin() | Requesting card verification PIN")
                if self.controller.cc.is_pin_set():
                    self.controller.cc.card_verify_PIN_simple()
                else:
                    self.controller.PIN_dialog(f'Unlock your {self.controller.cc.card_type}')

            logger.debug("Exiting edit_label method successfully")
        except Exception as e:
            logger.error(f"An unexpected error occurred in edit_label: {e}", exc_info=True)

    def check_authenticity(self):
        if self.controller.cc.card_present:
            logger.info("Card detected: checkin authenticity")
            is_authentic, txt_ca, txt_subca, txt_device, txt_error = self.controller.cc.card_verify_authenticity()
            if txt_error != "":
                txt_device = txt_error + "\n------------------\n" + txt_device

        try:
            logger.info("IN View.check_authenticity | Entering check_authenticity method")

            if self.current_frame is not None:
                try:
                    logger.debug("Clearing current frame")
                    self.clear_current_frame()
                    logger.debug("Current frame cleared")
                except Exception as e:
                    logger.error(f"An error occurred while clearing current frame: {e}", exc_info=True)

            try:
                logger.debug("Creating new frame")
                self.current_frame = View.create_frame(self)
                self.current_frame.place(relx=0.5, rely=0.5, anchor="center")
                logger.debug("New frame created and placed")

                self.header = View.create_an_header(self, "Check authenticity", "check_authenticity_popup.jpg")
                self.header.place(relx=0.32, rely=0.05, anchor="nw")
            except Exception as e:
                logger.error(f"An error occurred while creating new frame: {e}", exc_info=True)

            certificate_radio_value = customtkinter.StringVar(value="")

            def update_radio_selection():
                try:
                    if certificate_radio_value.get() == 'root_ca_certificate':
                        logger.info(f"Button clicked: {certificate_radio_value.get()}")
                        self.update_textbox(txt_ca)
                        self.text_box.place(relx=0.33, rely=0.4, anchor="nw")
                    if certificate_radio_value.get() == 'sub_ca_certificate':
                        logger.info(f"Button clicked: {certificate_radio_value.get()}")
                        self.update_textbox(txt_subca)
                        self.text_box.place(relx=0.33, rely=0.4, anchor="nw")
                    if certificate_radio_value.get() == 'device_certificate':
                        logger.info(f"Button clicked: {certificate_radio_value.get()}")
                        self.update_textbox(txt_device)
                        self.text_box.place(relx=0.33, rely=0.4, anchor="nw")
                except Exception as e:
                    logger.error(f"An error occurred in update_radio_selection: {e}", exc_info=True)

            try:
                text = View.create_label(self, f"Check whether or not you have a genuine Satochip card.")
                text.place(relx=0.33, rely=0.17, anchor="w")

                text = View.create_label(self, f"Status:")
                text.configure(font=self.make_text_bold())
                text.place(relx=0.33, rely=0.27, anchor="w")
                if self.controller.cc.card_present:
                    if is_authentic:
                        icon_image = Image.open("./pictures_db/genuine_card.jpg")
                        icon = customtkinter.CTkImage(light_image=icon_image, size=(30, 30))
                        icon_label = customtkinter.CTkLabel(self.current_frame, image=icon,
                                                            text=f"Your card is authentic. ",
                                                            compound='right', bg_color="whitesmoke", fg_color="whitesmoke",
                                                            font=customtkinter.CTkFont(family="Outfit",
                                                                                       size=18,
                                                                                       weight="normal"))
                        icon_label.place(relx=0.4, rely=0.267, anchor="w")
                    else:
                        icon_image = Image.open("./pictures_db/not_genuine_card.jpg")
                        icon = customtkinter.CTkImage(light_image=icon_image, size=(30, 30))
                        icon_label = customtkinter.CTkLabel(self.current_frame, image=icon,
                                                            text=f"Your card is not authentic. ",
                                                            compound='right', bg_color="whitesmoke", fg_color="whitesmoke",
                                                            font=customtkinter.CTkFont(family="Outfit",
                                                                                       size=18,
                                                                                       weight="normal"))
                        icon_label.place(relx=0.4, rely=0.267, anchor="w")

                        text = View.create_label(self, f"Warning!")
                        text.configure(font=self.make_text_bold())
                        text.place(relx=0.33, rely=0.7, anchor="w")
                        text = View.create_label(self, f"We could not authenticate the issuer of this card.")
                        text.place(relx=0.33, rely=0.75, anchor="w")
                        text = View.create_label(self,
                                                 f"If you did not load the card applet by yourself, be extremely careful!")
                        text.place(relx=0.33, rely=0.8, anchor="w")
                        text = View.create_label(self,
                                                 f"Contact support@satochip.io to report any suspicious device.")
                        text.place(relx=0.33, rely=0.85, anchor="w")

                logger.debug("Setting up radio buttons")
                self.root_ca_certificate = customtkinter.CTkRadioButton(self.current_frame,
                                                                        text="Root CA certificate",
                                                                        variable=certificate_radio_value,
                                                                        value="root_ca_certificate",
                                                                        font=customtkinter.CTkFont(family="Outfit",
                                                                                                   size=14,
                                                                                                   weight="normal"),
                                                                        bg_color="whitesmoke", fg_color="green",
                                                                        hover_color="green",
                                                                        command=update_radio_selection)
                self.root_ca_certificate.place(relx=0.33, rely=0.35, anchor="w")

                self.sub_ca_certificate = customtkinter.CTkRadioButton(self.current_frame,
                                                                       text="Sub CA certificate",
                                                                       variable=certificate_radio_value,
                                                                       value="sub_ca_certificate",
                                                                       font=customtkinter.CTkFont(family="Outfit",
                                                                                                  size=14,
                                                                                                  weight="normal"),
                                                                       bg_color="whitesmoke", fg_color="green",
                                                                       hover_color="green",
                                                                       command=update_radio_selection)
                self.sub_ca_certificate.place(relx=0.50, rely=0.35, anchor="w")

                self.device_certificate = customtkinter.CTkRadioButton(self.current_frame,
                                                                       text="Device certificate",
                                                                       variable=certificate_radio_value,
                                                                       value="device_certificate",
                                                                       font=customtkinter.CTkFont(family="Outfit",
                                                                                                  size=14,
                                                                                                  weight="normal"),
                                                                       bg_color="whitesmoke", fg_color="green",
                                                                       hover_color="green",
                                                                       command=update_radio_selection)
                self.device_certificate.place(relx=0.67, rely=0.35, anchor="w")
                logger.debug("Radio buttons set up")
            except Exception as e:
                logger.error(f"An error occurred while setting up radio buttons: {e}", exc_info=True)

            try:
                logger.info("Setting up text box")
                self.text_box = customtkinter.CTkTextbox(self, corner_radius=10,
                                                         bg_color='whitesmoke', fg_color=BUTTON_COLOR,
                                                         border_color=BUTTON_COLOR, border_width=0,
                                                         width=581, height=228 if is_authentic else 150,
                                                         text_color="grey",
                                                         font=customtkinter.CTkFont(family="Outfit", size=13,
                                                                                    weight="normal"))
                logger.debug("Text box set up")

                self.cancel_button = View.create_button(self, "Back",
                                                        lambda: self.start_setup())
                self.cancel_button.place(relx=0.85, rely=0.9, anchor="w")
                if self.controller.cc.card_type != "Satodime":
                    try:
                        self.controller.cc.card_verify_PIN_simple()
                    except Exception as e:
                        self.start_setup()

            except Exception as e:
                logger.error(f"An error occurred while setting up text box: {e}", exc_info=True)

            try:
                logger.info("Creating and placing main menu")
                self.menu = self.main_menu()
                self.menu.place(relx=0.250, rely=0.5, anchor="e")
                logger.debug("Main menu created and placed")
            except Exception as e:
                logger.error(f"An error occurred while creating main menu: {e}", exc_info=True)

            logger.info("Exiting check_authenticity method successfully")
        except Exception as e:
            logger.error(f"An unexpected error occurred in check_authenticity: {e}", exc_info=True)

    def click_reset_button(self):
        try:
            logger.info("Attempting to reset the card.")
            try:
                # self.reset_card_button.configure(state='disabled')
                logger.info("Reset button disabled.")
            except Exception as e:
                logger.error(f"An error occurred while disabling the reset button: {e}", exc_info=True)

            try:
                logger.info("Calling controller.cc.card_reset_factory()")
                #(response, sw1, sw2) = self.controller.card_transmit_reset()
                (response, sw1, sw2) = self.controller.cc.card_reset_factory_signal()
                logger.info(f"card_reset_factory response: {hex(256 * sw1 + sw2)}")
            except Exception as e:
                logger.error(f"An error occurred during card_reset_factory call: {e}", exc_info=True)
                return

            try:
                if sw1 == 0xFF and sw2 == 0x00:
                    logger.info("Factory reset successful. Disconnecting the card.")
                    #self.controller.cc.card_factory_disconnect()
                    self.controller.cc.card_disconnect()
                    msg = 'The card has been reset to factory\nRemaining counter: 0'
                    self.show('SUCCESS', msg, "Ok", lambda: self.restart_app(),
                              "./pictures_db/reset_popup.jpg")
                    logger.info("Card has been reset to factory. Counter set to 0.")
                elif sw1 == 0xFF and sw2 == 0xFF:
                    logger.info("Factory reset aborted. The card must be removed after each reset.")
                    msg = 'RESET ABORTED!\n Remaining counter: MAX.'
                    self.show('ABORTED', msg, "Ok",
                              lambda: [self.controller.cc.set_mode_factory_reset(False), self.start_setup()],
                              "./pictures_db/reset_popup.jpg")
                    logger.info("Reset aborted. Counter set to MAX.")
                elif sw1 == 0xFF and sw2 > 0x00:
                    logger.info(f"Factory reset in progress. Remaining counter: {sw2}")
                    self.counter = str(sw2) + "/4"
                    msg = f"Please follow the instruction bellow.\n{self.counter}"
                    self.show('IN PROGRESS', msg, "Remove card", lambda: self.click_reset_button(),
                              "./pictures_db/reset_popup.jpg")
                    self.show_button.configure(state='disabled')

                    logger.info("Card needs to be removed and reinserted to continue.")
                elif sw1 == 0x6F and sw2 == 0x00:
                    logger.info("Factory reset failed with error code 0x6F00.")
                    self.counter = "Unknown error " + str(hex(256 * sw1 + sw2))
                    msg = f"The factory reset failed\n{self.counter}"
                    self.show('FAILED', msg, "Ok", None, "./pictures_db/reset_popup.jpg")

                elif sw1 == 0x6D and sw2 == 0x00:
                    logger.info("Factory reset failed with error code 0x6D00.")
                    self.counter = "Instruction not supported - error code: " + str(hex(256 * sw1 + sw2))
                    msg = f"The factory reset failed\n{self.counter}"
                    self.show('FAILED', msg, "Ok", None,"./pictures_db/reset_popup.jpg")

            except Exception as e:
                logger.error(f"An error occurred while processing the factory reset response: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"An unexpected error occurred during the factory reset process: {e}", exc_info=True)

    def reset_my_card_window(self):
        self.controller.cc.set_mode_factory_reset(True)

        self.in_reset_card = 'display'
        logger.info(f'in reset card: {self.in_reset_card}')

        try:
            if self.current_frame is not None:
                try:
                    logger.debug("Clearing current frame")
                    self.clear_current_frame()
                    logger.debug("Current frame cleared")
                except Exception as e:
                    logger.error(f"An error occurred while clearing current frame: {e}", exc_info=True)

            try:
                logger.info("Creating new frame for reset card window")
                self.current_frame = View.create_frame(self)
                self.current_frame.place(relx=0.5, rely=0.5, anchor="center")
                logger.debug("New frame created and placed")
            except Exception as e:
                logger.error(f"An error occurred while creating new frame: {e}", exc_info=True)

            self.background_photo = View.create_background_photo(self, "./pictures_db/reset_my_card.png")
            self.canvas = View.create_canvas(self)
            self.canvas.place(relx=0.250, rely=0.501, anchor="w")
            self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")
            logger.debug("Background photo loaded and placed")

            try:
                logger.info("Creating header")
                self.header = View.create_an_header(self, f"Reset Your {self.controller.cc.card_type}", "reset_popup.jpg")
                self.header.place(relx=0.32, rely=0.05, anchor="nw")
                logger.debug("Header created and placed")

                logger.debug("setup paragraph")
                text = View.create_label(self,
                                         f"Resetting your card to factory settings removes all private keys, saved ")
                text.place(relx=0.33, rely=0.17, anchor="w")
                text = View.create_label(self,
                                         "information, and settings (PIN code) from your device.")
                text.place(relx=0.33, rely=0.22, anchor="w")

                text = View.create_label(self, "Before your start: be sure to have a backup of its content; either the")
                text.place(relx=0.33, rely=0.32, anchor="w")
                text = View.create_label(self,
                                         f"seedphrase or any other passwords stored in it.")
                text.place(relx=0.33, rely=0.37, anchor="w")

                text = View.create_label(self,
                                         "The reset process is simple: click on “Reset”, follow the pop-up wizard and")
                text.place(relx=0.33, rely=0.47, anchor="w")
                text = View.create_label(self,
                                         "remove your card from the chip card reader, insert it again. And do that")
                text.place(relx=0.33, rely=0.52, anchor="w")
                text = View.create_label(self,
                                         "several times.")
                text.place(relx=0.33, rely=0.57, anchor="w")
            except Exception as e:
                logger.error(f"An error occurred while creating header: {e}", exc_info=True)

            try:
                logger.info("Creating counter label")
                self.counter_label = customtkinter.CTkLabel(self, text="Card isn't reset actually",
                                                            bg_color='white', fg_color='white',
                                                            font=customtkinter.CTkFont(family="Outfit",
                                                                                       size=30,
                                                                                       weight="bold"))
                # self.counter_label.place(relx=0.25, rely=0.53, anchor='w')
                logger.debug("Counter label created and placed")
            except Exception as e:
                logger.error(f"An error occurred while creating counter label: {e}", exc_info=True)

            try:
                logger.info("Creating quit button")

                def click_cancel_button():
                    try:
                        logger.info("Executing quit button action")
                        self.controller.cc.set_mode_factory_reset(False)
                        time.sleep(0.5) # todo remove?
                        self.start_setup()
                    except Exception as e:
                        logger.error(f"An error occurred while quitting and redirecting: {e}", exc_info=True)

                def click_start_button():
                    try:
                        msg = f"Please follow the instruction bellow."
                        self.show('IN PROGRESS', msg, "Remove card", lambda: self.click_reset_button(),
                                  "./pictures_db/reset_popup.jpg")
                        self.show_button.configure(state='disabled')
                    except Exception as e:
                        logger.error(f"An error occurred while quitting and redirecting: {e}", exc_info=True)

                self.cancel_button = View.create_button(self, 'Cancel',
                                                        lambda: click_cancel_button())
                self.cancel_button.place(relx=0.7, rely=0.9, anchor="w")

                self.reset_button = View.create_button(self,
                                                       'Start',
                                                       lambda: click_start_button())
                self.reset_button.place(relx=0.85, rely=0.9, anchor="w")

                menu = self.main_menu()
                menu.place(relx=0.250, rely=0.5, anchor="e")

            except Exception as e:
                logger.error(f"An error occurred while creating quit button: {e}", exc_info=True)

            logger.info("IN View.reset_my_card_window() | Attempting to switch to factory observer")
            try:
                logger.debug("switch to factory observer successfully")
            except Exception as e:
                logger.error(f"An error occurred during the switch to factory observer: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"An unexpected error occurred in reset_my_card_window: {e}", exc_info=True)

    def about(self):
        # TODO: add reset seed button (for satochip only)
        # TODO: implement nfc enable/disable (depending on card & version)
        # TODO: implement 2FA disable/enable (only satochip)

        try:
            logger.info("IN View.edit_label() | Entering edit_label method")
            frame_name = "edit_label"
            cancel_button = "Cancel"
            finish_button = "Finish"

            if self.current_frame is not None:
                try:
                    logger.debug("Clearing current frame")
                    self.clear_current_frame()
                    logger.debug("Current frame cleared")
                except Exception as e:
                    logger.error(f"An error occurred while clearing current frame: {e}", exc_info=True)

            try:
                logger.debug("Creating new frame")
                self.current_frame = View.create_frame(self)
                self.current_frame.place(relx=0.5, rely=0.5, anchor="center")
                logger.debug("New frame created and placed")
            except Exception as e:
                logger.error(f"An error occurred while creating new frame: {e}", exc_info=True)

            try:
                logger.debug("Creating main menu")
                menu = self.main_menu()
                menu.place(relx=0.250, rely=0.5, anchor="e")
                logger.debug("Main menu created and placed")
            except Exception as e:
                logger.error(f"An error occurred while creating main menu: {e}", exc_info=True)

            try:
                logger.debug("Creating header")

                self.header = View.create_an_header(self,
                                                    "About",
                                                    "about_popup.jpg")

                self.header.place(relx=0.32, rely=0.05, anchor="nw")

                self.background_photo = View.create_background_photo(self, "./pictures_db/about_background.png")
                self.canvas = View.create_canvas(self)
                self.canvas.place(relx=0.250, rely=0.501, anchor="w")
                self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")

                def unlock():
                    if self.controller.cc.card_type != "Satodime":
                        if self.controller.cc.is_pin_set():
                            self.controller.cc.card_verify_PIN_simple()
                        else:
                            try:
                                self.controller.PIN_dialog(f'Unlock your {self.controller.cc.card_type}')
                            except Exception as e:
                                self.start_setup()
                    self.update_status()
                    self.about()

                # card infos
                card_information = self.create_label("Card information")
                card_information.place(relx=0.33, rely=0.25, anchor="w")
                card_information.configure(font=self.make_text_bold())

                applet_version = self.create_label(f"Applet version: {self.controller.card_status['applet_full_version_string']}")
                if self.controller.cc.card_type == "Satodime" or self.controller.cc.is_pin_set():
                    if self.controller.cc.card_type != "Satodime":
                        self.controller.cc.card_verify_PIN_simple()
                    card_label_named = self.create_label(f"Label: [{self.controller.get_card_label_infos()}]")
                    is_authentic, txt_ca, txt_subca, txt_device, txt_error = self.controller.cc.card_verify_authenticity()
                    if is_authentic:
                        card_genuine = self.create_label(f"Genuine: YES")
                    else:
                        card_genuine = self.create_label("Genuine: NO")
                elif not self.controller.cc.setup_done:
                    watch_all = self.create_label("Card requires setup")
                    watch_all.place(relx=0.33, rely=0.17)
                    unlock_button = self.create_button("Setup card", lambda: self.setup_my_card_pin())
                    unlock_button.configure(font=self.make_text_size_at(15))
                    unlock_button.place(relx= 0.55, rely=0.17)
                    card_label_named = self.create_label(f"Label: [UNKNOWN]")
                    card_genuine = self.create_label(f"Genuine: [UNKNOWN]")
                else:
                    watch_all = self.create_label("PIN required to look at complete information")
                    watch_all.place(relx=0.33, rely=0.17)
                    unlock_button = self.create_button("Unlock", lambda: [unlock()])
                    unlock_button.configure(font=self.make_text_size_at(15))
                    unlock_button.place(relx=0.75, rely=0.17)
                    card_label_named = self.create_label(f"Label: [UNKNOWN]")
                    card_genuine = self.create_label(f"Genuine: [UNKNOWN]")

                card_label_named.place(relx=0.33, rely=0.28)
                applet_version.place(relx=0.33, rely=0.33)
                card_genuine.place(relx=0.33, rely=0.38)

                # card configuration
                card_configuration = self.create_label("Card configuration")
                card_configuration.place(relx=0.33, rely=0.48, anchor="w")
                card_configuration.configure(font=self.make_text_bold())
                if self.controller.cc.card_type != "Satodime":
                    pin_information = self.create_label(f"PIN counter:[{self.controller.card_status['PIN0_remaining_tries']}] tries remaining")
                    pin_information.place(relx=0.33, rely=0.52)
                else:
                    pin_information = self.create_label("No PIN required")
                    pin_information.place(relx=0.33, rely=0.52)

                # for a next implementation of 2FA functionality you have the code below
                if self.controller.cc.card_type == "Satochip":
                    two_FA = self.create_label(f"2FA enabled" if self.controller.cc.needs_2FA else f"2FA disabled")
                    two_FA.place(relx=0.33, rely=0.58)
                    # if self.controller.cc.needs_2FA:
                    #     self.button_2FA = self.create_button("Disable 2FA", None)
                    # else:
                    #     self.button_2FA = self.create_button("Enable 2FA")
                    # self.button_2FA.configure(font=self.make_text_size_at(15), state='disabled')
                    # self.button_2FA.place(relx=0.5, rely=0.58)

                # card connectivity
                card_connectivity = self.create_label("Card connectivity")
                card_connectivity.place(relx=0.33, rely=0.68, anchor="w")
                card_connectivity.configure(font=self.make_text_bold())

                if self.controller.cc.nfc_policy == 0:
                    nfc = self.create_label(f"NFC enabled")
                    #self.button_nfc = self.create_button("Disable NFC")
                elif self.controller.cc.nfc_policy == 1:
                    nfc = self.create_label(f"NFC disabled:")
                    #self.button_nfc = self.create_button("Enable NFC")
                else:
                    nfc = self.create_label(f"NFC: [BLOCKED]")
                nfc.place(relx=0.33, rely=0.715)
                #self.button_nfc.configure(font=self.make_text_size_at(15), state='disabled')
                #self.button_nfc.place(relx=0.5, rely=0.71)

                # software information
                software_information = self.create_label("Software information")
                software_information.place(relx=0.33, rely=0.81, anchor="w")
                software_information.configure(font=self.make_text_bold())
                app_version = self.create_label(f"Satochip-utils version: {VERSION}")
                app_version.place(relx=0.33, rely=0.83)
                pysatochip_version = self.create_label(f"Pysatochip version: {PYSATOCHIP_VERSION}")
                pysatochip_version.place(relx=0.33, rely=0.88)
                back_button = View.create_button(self,
                                                       'Back',
                                                       lambda: self.start_setup())
                back_button.place(relx=0.85, rely=0.9, anchor="w")

                logger.debug("Header created and placed")
            except Exception as e:
                logger.error(f"An error occurred while creating header: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"An error occurred while creating header: {e}", exc_info=True)


    ##########################
    '''SEEDKEEPER OPTIONS'''


