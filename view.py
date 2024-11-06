import binascii
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
from exceptions import MenuCreationError, MenuDeletionError, ViewError, ButtonCreationError, FrameClearingError, \
    FrameCreationError, HeaderCreationError, UIElementError, SecretFrameCreationError, ControllerError
from frameCardAbout import FrameCardAbout
from frameCardAuthenticity import FrameCardAuthenticity
from frameCardChangePin import FrameCardChangePin
from frameCardEditLabel import FrameCardEditLabel
from frameCardFactoryReset import FrameCardFactoryReset
from frameCardImportSeed import FrameCardImportSeed
from frameCardSetupPin import FrameCardSetupPin
from frameMenuNoCard import FrameMenuNoCard
from frameMenuSeedkeeper import FrameMenuSeedkeeper
from frameMenuSettings import FrameMenuSettings
from frameSeedkeeperListSecrets import FrameSeedkeeperListSecrets
from frameSeedkeeperShowPasswordSecret import FrameSeedkeeperShowPasswordSecret
from frameStart import FrameStart
from frameWelcome import FrameWelcome
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

ICON_PATH = "./pictures_db/"


class View(customtkinter.CTk):
    def __init__(self, loglevel=logging.INFO):
        try:
            #logger.setLevel(loglevel)
            logger.setLevel(logging.DEBUG)
            logger.debug("Log level set to INFO")
            logger.info("Starting View.__init__()")
            super().__init__()

            # status infos
            self.welcome_in_display = True

            # seedkeeper state
            self.in_backup_process = False

            # Initializing controller
            self.controller = Controller(None, self, loglevel=loglevel)

            # Initializing main window
            self.main_window()

            # Creating main frame
            self.main_frame = customtkinter.CTkFrame(self, width=1000, height=600, bg_color="white",
                                                     fg_color="white")
            self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

            # Widget declaration -> Maybe unnecessary but marked as error if not declared before
            # TODO: clean code
            logger.debug("Declaring widgets")
            self.current_frame = None
            self.canvas = None
            self.background_photo = None
            #self.create_background_photo = None
            self.header = None
            self.text_box = None
            self.button = None
            self.finish_button = None # todo: local variable
            self.menu = None
            #self.main_menu = None
            #self.seedkeeper_menu = None
            self.counter = None
            self.display_menu = False
            logger.debug("Widgets declared successfully")

            # frames
            # these will be created when needed using show_* methods
            self.welcome_frame = None
            self.start_frame = None
            # menu frames
            self.seedkeeper_menu_frame = None
            self.settings_menu_frame = None
            # settings frames
            self.setup_card_frame = None
            self.about_frame = None
            self.authenticity_frame = None
            self.edit_label_frame = None
            self.change_pin_frame = None
            self.seed_import_frame = None
            self.factory_reset_frame = None
            # seedkeeper frames
            self.list_secrets_frame = None
            self.seedkeeper_show_password_frame = None

            # widgets (todo: clean)
            self.show_button = None


            # Application state attributes
            # Status de l'application et de certains widgets
            # TODO: remove??
            self.app_open: bool = True
            self.welcome_in_display: bool = True
            self.spot_if_unlock: bool = False
            self.pin_left: Optional[int] = None
            self.mnemonic_textbox_active: bool = False
            self.mnemonic_textbox: Optional[customtkinter.CTkTextbox] = None
            self.password_text_box_active: bool = False
            self.password_text_box: Optional[customtkinter.CTkTextbox] = None

            # Launching initialization starting with welcome view
            self.nocard_menu_frame = FrameMenuNoCard(self)
            self.welcome_frame = FrameWelcome(self)
            self.protocol("WM_DELETE_WINDOW", lambda: [self.on_close()])

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

    def convert_icon_name_to_photo_image(self, filename):
        icon_path = f"{ICON_PATH}{filename}"
        image = Image.open(icon_path)
        image = image.resize((25, 25), Image.LANCZOS)
        photo_image = customtkinter.CTkImage(image)
        return photo_image

    @staticmethod
    def make_text_bold(size=18):
        logger.debug("make_text_bold start")
        result = customtkinter.CTkFont(weight="bold", size=size)
        return result

    def make_text_size_at(self, size=18):
        logger.debug("make_text_size_at start")
        result = customtkinter.CTkFont(size=size)
        return result

    def create_an_header(self, title_text: str = "", icon_name: str = None, fg_bg_color=None, frame = None):
        try:
            logger.debug("create_an_header start")

            if frame is None:
                frame = self.main_frame

            # Créer le cadre de l'en-tête
            header_frame = customtkinter.CTkFrame(frame, fg_color="whitesmoke", bg_color="whitesmoke", width=750, height=40)

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

    def create_an_header_for_welcome(self, frame=None):
        if frame is None:
            frame = self.welcome_frame

        icon_path = f"./pictures_db/welcome_logo.png"
        header = customtkinter.CTkFrame(frame, width=380, height=178, bg_color='white')
        header.place(relx=0.1, rely=0.03, anchor='nw')

        logo_canvas = customtkinter.CTkCanvas(header, width=400, height=400, bg='black')
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

    def _create_an_header( # todo merge with create_an_header
            self,
            title_text: Optional[str] = None,
            icon_name: Optional[str] = None,
    ) -> customtkinter.CTkFrame:
        try:
            logger.info(f"_create_an_header start with title: '{title_text}' and icon: '{icon_name}'")

            header_frame = customtkinter.CTkFrame(
                self.current_frame, fg_color="whitesmoke", bg_color="whitesmoke",
                width=750, height=40
            )

            if title_text and icon_name:
                icon_path = f"{ICON_PATH}{icon_name}"
                image = Image.open(icon_path)
                photo_image = customtkinter.CTkImage(image, size=(40, 40))

                button = customtkinter.CTkButton(
                    header_frame, text=f"   {title_text}", image=photo_image,
                    font=customtkinter.CTkFont(family="Outfit", size=25, weight="bold"),
                    bg_color="whitesmoke", fg_color="whitesmoke", text_color="black",
                    hover_color="whitesmoke", compound="left"
                )
                button.image = photo_image
                button.place(rely=0.5, relx=0, anchor="w")

            return header_frame
        except Exception as e:
            logger.error(f"010 Unexpected error in _create_an_header: {e}", exc_info=True)
            raise HeaderCreationError(f"011 Failed to create header: {e}") from e

    def create_frame(self, bg_fg_color: str = "whitesmoke", width: int = 1000, height: int = 600, frame=None) -> customtkinter.CTkFrame:
        logger.debug("View.create_frame() start")
        if frame is None:
            frame = self.main_frame

        new_frame = customtkinter.CTkFrame(
            frame,
            width=width,
            height=height,
            bg_color=bg_fg_color,
            fg_color=bg_fg_color)
        return new_frame


    def _create_frame(self):
        try:
            logger.info("_create_frame start")
            self._clear_current_frame()
            self.current_frame = customtkinter.CTkFrame(
                self.main_frame, width=750, height=600,
                fg_color=DEFAULT_BG_COLOR, bg_color=DEFAULT_BG_COLOR
            )
            self.current_frame.place(relx=0.250, rely=0.5, anchor='w')
        except Exception as e:
            logger.error(f"004 Error in _create_frame: {e}", exc_info=True)
            raise FrameCreationError(f"005 Failed to create frame: {e}") from e

    def _create_scrollable_frame(
            self,
            parent_frame,
            width,
            height,
            x,
            y
    ) -> customtkinter.CTkFrame:
        try:
            logger.info("_create_scrollable_frame start")

            # Create a frame to hold the canvas and scrollbar
            container = customtkinter.CTkFrame(parent_frame, width=width, height=height, fg_color=DEFAULT_BG_COLOR)
            container.place(x=x, y=y)
            container.pack_propagate(False)  # Prevent the frame from shrinking to fit its contents

            # Create a canvas with specific dimensions
            canvas = customtkinter.CTkCanvas(container, bg=DEFAULT_BG_COLOR, highlightthickness=0)
            canvas.pack(side="left", fill="both", expand=True)

            # Add a scrollbar to the canvas
            scrollbar = customtkinter.CTkScrollbar(container, orientation="vertical", command=canvas.yview)
            scrollbar.pack(side="right", fill="y")

            # Configure scrollbar colors
            scrollbar.configure(fg_color=DEFAULT_BG_COLOR, button_color=DEFAULT_BG_COLOR,
                                button_hover_color=BG_HOVER_BUTTON)

            # Configure the canvas
            canvas.configure(yscrollcommand=scrollbar.set)

            # Create a frame inside the canvas
            inner_frame = customtkinter.CTkFrame(canvas, fg_color=DEFAULT_BG_COLOR)

            # Add that frame to a window in the canvas
            canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor="nw")

            def _configure_inner_frame(event):
                # Update the scrollregion to encompass the inner frame
                canvas.configure(scrollregion=canvas.bbox("all"))

                # Resize the inner frame to fit the canvas width
                canvas.itemconfig(canvas_window, width=canvas.winfo_width())

            inner_frame.bind("<Configure>", _configure_inner_frame)

            def _configure_canvas(event):
                # Resize the inner frame to fit the canvas width
                canvas.itemconfig(canvas_window, width=event.width)

            canvas.bind("<Configure>", _configure_canvas)

            def _on_mousewheel(event):
                # Check if there's actually something to scroll
                if canvas.bbox("all")[3] <= canvas.winfo_height():
                    return  # No scrolling needed, so do nothing

                if event.delta > 0:
                    canvas.yview_scroll(-1, "units")
                elif event.delta < 0:
                    canvas.yview_scroll(1, "units")

            # Bind mouse wheel to the canvas
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

            return inner_frame
        except Exception as e:
            logger.error(f"003 Error in _create_scrollable_frame: {e}", exc_info=True)
            raise FrameCreationError(f"004 Failed to create scrollable frame: {e}") from e

    def create_label(self, text, bg_fg_color: str = "whitesmoke", frame=None) -> customtkinter.CTkLabel:
        # todo use frame
        if frame is None:
            frame = self.current_frame

        logger.debug("view.create_label start")
        label = customtkinter.CTkLabel(
            frame,
            text=text,
            bg_color=bg_fg_color,
            fg_color=bg_fg_color,
            font=customtkinter.CTkFont(family="Outfit", size=18, weight="normal")
        )
        return label

    def create_button(
            self,
            text: str = None,
            command=None,
            frame=None
    ) -> customtkinter.CTkButton:
        logger.debug("View.create_button() start")
        if frame is None:
            frame = self.current_frame

        button = customtkinter.CTkButton(
            frame,
            text=text,
            width=120, height=35, corner_radius=100,
            font=customtkinter.CTkFont(family="Outfit", size=18, weight="normal"),
            bg_color='white', fg_color=MAIN_MENU_COLOR,
            hover_color=HOVER_COLOR, cursor="hand2",
            command=command)
        return button

    def create_button_for_main_menu_item( # todo rename create_menu_button
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
            state=state,
            anchor="w"
        )
        #button.image = photo_image  # keep a reference!
        button.place(rely=rel_y, relx=rel_x, anchor="w")

        return button

    def create_entry(self, show_option: str = "", frame=None)-> customtkinter.CTkEntry:
        logger.debug("create_entry start")
        if frame is None:
            frame = self.current_frame # todo
        entry = customtkinter.CTkEntry(
            frame, width=555, height=37, corner_radius=10,
            bg_color='white', fg_color=BUTTON_COLOR, border_color=BUTTON_COLOR,
            show=show_option, text_color='grey'
        )
        return entry

    def _create_entry(self, show_option: str = "")-> customtkinter.CTkEntry: # todo merge with create_entry
        logger.debug("create_entry start")
        entry = customtkinter.CTkEntry(
            self.current_frame, width=555, height=37, corner_radius=10,
            bg_color='white', fg_color=BUTTON_COLOR, border_color=BUTTON_COLOR,
            show=show_option, text_color='grey'
        )
        return entry

    def update_textbox_old(self, text):
        try:
            logger.debug("update_textbox start")
            # Efface le contenu actuel
            self.text_box.delete(1.0, "end")
            # Inserting new text into the textbox
            self.text_box.insert("end", text)
        except Exception as e:
            logger.error(f"An unexpected error occurred in update_textbox: {e}", exc_info=True)

    def update_textbox(self, text_box, text):
        try:
            logger.debug("update_textbox start")
            # Efface le contenu actuel
            text_box.delete(1.0, "end")
            # Inserting new text into the textbox
            text_box.insert("end", text)
        except Exception as e:
            logger.error(f"An unexpected error occurred in update_textbox: {e}", exc_info=True)

    @staticmethod
    def create_background_photo(picture_path):
        try:
            logger.info(f"create_background_photo method with path: {picture_path}")
            if getattr(sys, 'frozen', False):
                application_path = sys._MEIPASS
                logger.info(f"Running in a bundled application, application path: {application_path}")
            else:
                application_path = os.path.dirname(os.path.abspath(__file__))
                logger.info(f"Running in a regular script, application path: {application_path}")

            pictures_path = os.path.join(application_path, picture_path)
            logger.debug(f"Full path to background photo: {pictures_path}")

            background_image = Image.open(pictures_path)
            photo_image = ImageTk.PhotoImage(background_image)

            return photo_image
        except Exception as e:
            logger.error(f"An unexpected error occurred in create_background_photo: {e}", exc_info=True)
            return None

    def create_canvas(self, width=1000, height=600, frame=None) -> customtkinter.CTkCanvas:
        try:
            logger.debug("View.create_canvas() start")
            if frame is None:
                frame = self.main_frame
            canvas = customtkinter.CTkCanvas(frame, bg="whitesmoke", width=width, height=height)# todo: 599 or 600?
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
            self.show_button = customtkinter.CTkButton(
                popup, text=button_txt, fg_color=MAIN_MENU_COLOR,
                hover_color=HOVER_COLOR, bg_color='whitesmoke',
                width=120, height=35, corner_radius=34,
                font=customtkinter.CTkFont(family="Outfit", size=18, weight="normal"),
                command=lambda: close_show()
            )
            self.show_button.pack(pady=20)

        except Exception as e:
            logger.error(f"An error occurred in show: {e}", exc_info=True)
            raise

    #################
    """ MAIN MENU """

    def show_menu_frame(self):
        logger.info("IN View.show_menu_frame start")
        if self.controller.cc.card_present:
            if self.controller.cc.card_type == "SeedKeeper":
                self.show_seedkeeper_menu()
            else:
                self.show_settings_menu()
        else: # no card
            self.show_nocard_menu()

    def show_settings_menu(self, state=None, frame=None):
        logger.info("IN View.show_settings_menu start")
        if self.settings_menu_frame is None:
            self.settings_menu_frame = FrameMenuSettings(self)
        self.settings_menu_frame.update()
        logger.info("IN View.show_settings_menu before tkraise")
        self.settings_menu_frame.tkraise()
        logger.info("IN View.show_settings_menu after tkraise")

    def show_nocard_menu(self):
        logger.info("IN View.show_settings_menu start")
        self.nocard_menu_frame.tkraise()

    ################################
    """ UTILS FOR CARD CONNECTOR """

    def update_status(self, isConnected=None):
        try:
            if self.controller.cc.mode_factory_reset == True:
                # we are in factory reset mode
                #TODO: refactor?
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
                logger.info("View.update_status start (normal mode)")
                if isConnected is True:
                    try:
                        #logger.info("Getting card status")
                        #self.controller.get_card_status() # todo:neeeded?

                        if self.start_frame is not None: # do not create frame now as it is not main thread
                            self.show_start_frame()
                            self.show_menu_frame()

                    except Exception as e:
                        logger.error(f"An error occurred while getting card status: {e}", exc_info=True)

                elif isConnected is False:
                    try:
                        if self.start_frame is not None: # do not create frame now as it is not main thread
                            self.show_start_frame()
                            self.show_nocard_menu()

                    except Exception as e:
                        logger.error(f"An error occurred while resetting card status: {e}", exc_info=True)

                else: # isConnected is None
                    logger.error("View.update_status isConnected is None (should not happen!)", exc_info=True)

        except Exception as e:
            logger.error(f"An unexpected error occurred in update_status method: {e}", exc_info=True)

    def update_verify_pin(self):
        if self.controller.cc.card_type != "Satodime":
            if self.controller.cc.is_pin_set():
                self.controller.cc.card_verify_PIN_simple()
            else:
                self.controller.PIN_dialog(f'Unlock your {self.controller.cc.card_type}')

    def get_passphrase(self, msg): #todo rename
        try:
            logger.info("View.get_passphrase() start")

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

            # Ajout d'un label avec une image dans le popup
            icon_image = Image.open("./pictures_db/change_pin_popup.jpg")
            icon = customtkinter.CTkImage(light_image=icon_image, size=(20, 20))
            icon_label = customtkinter.CTkLabel(
                popup, image=icon, text=f"\nEnter the PIN code of your card.",
                compound='top',
                font=customtkinter.CTkFont(family="Outfit", size=18, weight="normal")
            )
            icon_label.pack(pady=(0, 10))  # Ajout d'un padding différent pour l'icône
            logger.debug("Label added to popup")

            # Ajout d'un champ d'entrée
            passphrase_entry = customtkinter.CTkEntry(
                popup, show="*", corner_radius=10, border_width=0,
                width=229, height=37, bg_color='whitesmoke',
                fg_color=BUTTON_COLOR, text_color='grey')
            popup.after(100, passphrase_entry.focus_force)
            passphrase_entry.pack(pady=15)
            logger.debug("Entry field added to popup")

            # Variables pour stocker les résultats
            pin = None

            # Fonction pour soumettre la passphrase et fermer le popup
            def submit_passphrase():
                nonlocal pin
                pin = passphrase_entry.get()
                popup.destroy()

            # Bouton pour soumettre la passphrase
            submit_button = customtkinter.CTkButton(
                popup, bg_color='whitesmoke', fg_color=MAIN_MENU_COLOR,
                width=120, height=35, corner_radius=34,
                hover_color=HOVER_COLOR, text="Submit",
                command=submit_passphrase,
                font=customtkinter.CTkFont(family="Outfit", size=18, weight="normal")
            )
            submit_button.pack(pady=10)
            logger.debug("Submit button added to popup")

            # Rendre la fenêtre modale
            popup.transient(self)  # Set to be on top of the main window
            popup.bind('<Return>', lambda event: submit_passphrase())
            logger.debug("Popup set to be on top of the main window")

            # Attendre que la fenêtre popup soit détruite
            self.wait_window(popup)
            logger.debug("Waiting for popup window to be destroyed")

            # Retourner les résultats
            return pin

        except Exception as e:
            logger.error(f"An error occurred in get_passphrase: {e}", exc_info=True)
            return None

    #############
    """ VIEWS """

    def show_start_frame(self):
        logger.info("IN View.show_start_frame() start")
        if self.start_frame is None:
            self.start_frame = FrameStart(self)
        else:
            self.start_frame.update()
            self.start_frame.tkraise()

    def show_setup_card_frame(self):
        if self.setup_card_frame is None:
            self.setup_card_frame = FrameCardSetupPin(self)
        self.setup_card_frame.tkraise()

    def show_seed_import_frame(self):
        if self.seed_import_frame is None:
            self.seed_import_frame = FrameCardImportSeed(self)
        self.seed_import_frame.tkraise()

    def show_change_pin_frame(self):
        if self.change_pin_frame is None:
            self.change_pin_frame = FrameCardChangePin(self)
        self.change_pin_frame.tkraise()

    def show_edit_label_frame(self):
        if self.edit_label_frame is None:
            self.edit_label_frame = FrameCardEditLabel(self)
        self.edit_label_frame.tkraise()

    def show_check_authenticity_frame(self):
        # verify PIN
        self.update_verify_pin()

        if self.authenticity_frame is None:
            self.authenticity_frame = FrameCardAuthenticity(self)
            #self.authenticity_frame = self.create_check_authenticity_frame()
        self.authenticity_frame.place()
        self.authenticity_frame.tkraise()

    def show_factory_reset_frame(self):
        if self.factory_reset_frame is None:
            self.factory_reset_frame = FrameCardFactoryReset(self)
        self.factory_reset_frame.tkraise()

    def show_about_frame(self):
        logger.info("show_about_frame start")
        if self.about_frame is None:
            logger.info("show_about_frame self.about_frame is None")
            self.about_frame = FrameCardAbout(self)
        self.about_frame.update()
        self.about_frame.tkraise()

    ################################
    """ SEEDKEEPER MENU """

    def show_seedkeeper_menu(self, state=None, frame=None):
        logger.info("show_seedkeeper_menu start")
        if self.seedkeeper_menu_frame is None:
            self.seedkeeper_menu_frame = FrameMenuSeedkeeper(self)
        else:
            logger.info("show_seedkeeper_menu seedkeeper_menu_frame is not None, show it")
            #self.settings_menu_frame.place_forget()
            #self.seedkeeper_menu_frame.place()
            self.seedkeeper_menu_frame.tkraise()

    ####################################################################################################################
    """ METHODS TO DISPLAY A VIEW FROM SEEDKEEPER MENU SELECTION """

    # SEEDKEEPER MENU SELECTION
    #@log_method
    def show_view_my_secrets(self):  #todo rename show_seedkeeper_list_secrets
        try:
            logger.debug("show_view_my_secrets start")
            # self.in_backup_process = False
            # self.welcome_in_display = False
            # self._clear_welcome_frame()
            # self._clear_current_frame()

            # verify PIN
            self.update_verify_pin()

            secrets_data = self.controller.retrieve_secrets_stored_into_the_card()
            logger.debug(f"Fetched {len(secrets_data['headers'])} headers")

            #self.view_my_secrets(secrets_data)
            if self.list_secrets_frame is None:
                self.list_secrets_frame = FrameSeedkeeperListSecrets(self)
            self.list_secrets_frame.update(secrets_data)
            self.list_secrets_frame.tkraise()

        except Exception as e:
            logger.error(f"005 Error in show_secrets: {e}", exc_info=True)


    def show_view_secret(self, secret_header):
        logger.log(SUCCESS, f"show_view_secret start")
        # Managing export rights control
        secret_details = {}
        if secret_header['export_rights'] == '0x2':
            secret_details['type'] = secret_header['type']
            secret_details['label'] = secret_header['label']
            secret_details['secret'] = 'Export failed: export not allowed by SeedKeeper policy.'
            secret_details['subtype'] = 0x0 if secret_header['subtype'] == '0x0' else '0x1'
            logger.debug(f"Export_rights: Not allowed for {secret_header} with id {secret_header['id']}")
        else:
            logger.debug(f"Export rights allowed for {secret_header} with id {secret_header['id']}")
            secret_details = self.controller.retrieve_details_about_secret_selected(secret_header['id'])
            secret_details['id'] = secret_header['id']
            logger.debug(f"secret id details: {secret_details} for id: {secret_details['id']}")
        logger.log(SUCCESS, f"Secret details retrieved: {secret_details}")

        # show secret according to type
        if secret_header['type'] == 'Password':
            logger.debug(f"Secret: {secret_header}, with id {secret_header['id']} is a couple login password")
            #self._create_password_secret_frame(secret_details)
            self.show_password_secret(secret_details)
            logger.debug(f"Frame corresponding to {secret_header['type']} details called")
        else:
            pass # TODO unsuported secret type

    def show_password_secret(self, secret):
        if self.seedkeeper_show_password_frame is None:
            self.seedkeeper_show_password_frame = FrameSeedkeeperShowPasswordSecret(self)
        self.seedkeeper_show_password_frame.update(secret)
        self.seedkeeper_show_password_frame.tkraise()

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
    def show_view_help(self): # todo remove, use web link
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

    ##########################
    '''SEEDKEEPER OPTIONS'''

    @log_method
    def view_my_secrets(
            self,
            secrets_data: Dict[str, Any]
    ): #todo remove unused
        """
            This method manages to:
                - Show a list of all secrets stored on the card.
                - Select and display details about each secret from the list.
                - Include specific widgets and buttons according to the secret type/subtype.
                - This method is built using a structural encapsulation approach, meaning that each function within it contains everything necessary for its operation, ensuring modularity and self-sufficiency.
        """

        @log_method
        def _create_secrets_frame():
            try:
                logger.info("001 Creating secrets frame")
                self._create_frame()
            except Exception as e:
                logger.error(f"003 Error creating secrets frame: {e}", exc_info=True)
                raise FrameCreationError(f"004 Failed to create secrets frame: {e}") from e

        @log_method
        def _create_secrets_header():
            try:
                logger.info("Creating secrets header")
                self.header = self._create_an_header("My secrets", "secrets_icon_popup.png")
                self.header.place(relx=0.03, rely=0.08, anchor="nw")
                logger.log(SUCCESS, "Secrets header created successfully")
            except Exception as e:
                logger.error(f"Error creating secrets header: {e}", exc_info=True)
                raise UIElementError(f"Failed to create secrets header: {e}") from e

        @log_method
        def _create_secrets_table(secrets_data):
            logger.debug(f"_create_secrets_table secret data: {secrets_data}")

            def _on_mouse_on_secret(event, buttons):
                for button in buttons:
                    button.configure(fg_color=HIGHLIGHT_COLOR, cursor="hand2")

            def _on_mouse_out_secret(event, buttons):
                for button in buttons:
                    button.configure(fg_color=button.default_color)

            def _show_secret_details(secret):
                try:
                    # Showing details for secret ID: {secret['id']}
                    self._create_frame()

                    # Managing export rights control
                    secret_details = {}
                    if secret['export_rights'] == '0x2':
                        secret_details['type'] = secret['type']
                        secret_details['label'] = secret['label']
                        secret_details['secret'] = 'Export failed: export not allowed by SeedKeeper policy.'
                        secret_details['subtype'] = 0x0 if secret['subtype'] == '0x0' else '0x1'
                        logger.debug(f"Export_rights: Not allowed for {secret} with id {secret['id']}")
                    else:
                        logger.debug(f"Export rights allowed for {secret} with id {secret['id']}")
                        secret_details = self.controller.retrieve_details_about_secret_selected(secret['id'])
                        secret_details['id'] = secret['id']
                        logger.debug(f"secret id details: {secret_details} for id: {secret_details['id']}")
                    logger.log(SUCCESS, f"Secret details retrieved: {secret_details}")

                    logger.debug("Creating and placing header for Secret détails frame")
                    self.header = self._create_an_header("Secret details", "secrets_icon_popup.png")
                    self.header.place(relx=0.03, rely=0.08, anchor="nw")

                    # Calling the main menu for seedkeeper
                    self.show_seedkeeper_menu()

                    logger.debug("Starting to control the secret type to choose the corresponding frame to dsplay")
                    if secret['type'] == 'Password':
                        logger.debug(f"Secret: {secret}, with id {secret['id']} is a couple login password")
                        self._create_password_secret_frame(secret_details)
                        logger.debug(f"Frame corresponding to {secret['type']} details called")
                    elif secret['type'] == 'Masterseed':
                        if secret_details['subtype'] > 0 or secret_details['subtype'] == '0x1':
                            logger.info(f"this is mnemonic, subtype: {secret['subtype']}")
                            logger.debug(f"Frame corresponding to {secret['type']} details called for subtype: {secret['subtype']}")
                            self._create_mnemonic_secret_frame(secret_details)
                        else:
                            logger.info(f"this is masterseed, subtype: {secret['subtype']}")
                            self._create_masterseed_secret_frame(secret_details)
                            logger.debug(f"Frame corresponding to {secret['type']} details called for subtype: {secret['subtype']}")
                    elif secret['type'] == "BIP39 mnemonic":
                        logger.debug(f"Secret: {secret}, with id {secret['id']} is a {secret['type']}")
                        self._create_mnemonic_secret_frame(secret_details)
                        logger.debug(f"Frame corresponding to {secret['type']}{secret['type']} details called")
                    elif secret['type'] == 'Electrum mnemonic':
                        logger.debug(f"Secret: {secret}, with id {secret['id']} is a {secret['type']}")
                        self._create_mnemonic_secret_frame(secret_details)
                        logger.debug(f"Frame corresponding to {secret['type']} details called")
                    elif secret['type'] == '2FA secret':
                        logger.debug(f"Secret: {secret}, with id {secret['id']} is a {secret['type']}")
                        self._create_2FA_secret_frame(secret_details)
                        logger.debug(f"Frame corresponding to {secret['type']} details called")
                    elif secret['type'] == 'Free text':
                        logger.info(f"this is mnemonic, subtype: {secret['subtype']}")
                        logger.debug(f"Frame corresponding to {secret['type']} details called for subtype: {secret['subtype']}")
                        self._create_free_text_secret_frame(secret_details)
                    elif secret['type'] == 'Wallet descriptor':
                        logger.info(f"this is wallet descriptor, subtype: {secret['subtype']}")
                        logger.debug(f"Frame corresponding to {secret['type']} details called for subtype: {secret['subtype']}")
                        self._create_wallet_descriptor_secret_frame(secret_details)
                    else:
                        logger.warning(f"Unsupported secret type: {secret['type']}")
                        self.show("WARNING", f"Unsupported type:\n{secret['type']}", "Ok", None, "./pictures_db/secrets_icon_popup.png")

                    back_button = self.create_button(text="Back", command=self.show_view_my_secrets)
                    back_button.place(relx=0.95, rely=0.98, anchor="se")

                    logger.log(SUCCESS, f"012 Secret details displayed for ID: {secret['id']}")
                except Exception as e:
                    logger.error(f"013 Error displaying secret details: {e}", exc_info=True)
                    raise SecretFrameCreationError("Error displaying secret details") from e

            try:
                logger.info("Creating secrets table")

                subtype_dict = {
                    '0x0': 'masterseed',
                    '0x1': 'Mnemonic seedphrase',
                }

                # Introduce table
                label_text = self.create_label(text="Click on a secret to manage it:")
                label_text.place(relx=0.05, rely=0.25, anchor="w")

                # Define headers
                headers = ["Id", "Type of secret", "Label"]
                rely = 0.3

                # Create header labels
                header_frame = customtkinter.CTkFrame(
                    self.current_frame, width=750, bg_color=DEFAULT_BG_COLOR,
                    corner_radius=0, fg_color=DEFAULT_BG_COLOR)
                header_frame.place(relx=0.05, rely=rely, relwidth=0.9, anchor="w")

                header_widths = [100, 250, 350]  # Define specific widths for each header
                for col, width in zip(headers, header_widths):
                    header_button = customtkinter.CTkButton(
                        header_frame, text=col,
                        font=customtkinter.CTkFont(size=14, family='Outfit', weight="bold"),
                        corner_radius=0, state='disabled', text_color='white',
                        fg_color=BG_MAIN_MENU, width=width
                    )
                    header_button.pack(side="left", expand=True, fill="both")

                logger.debug("015 Table headers created")

                table_frame = self._create_scrollable_frame(
                    self.current_frame, width=700, height=400, x=33.5, y=200)

                # Create rows of labels with alternating colors
                for i, secret in enumerate(secrets_data['headers']):
                    try:
                        rely += 0.06
                        row_frame = customtkinter.CTkFrame(
                            table_frame, width=750,
                            bg_color=DEFAULT_BG_COLOR,
                            fg_color=DEFAULT_BG_COLOR
                        )
                        row_frame.pack(pady=2, fill="x")

                        fg_color = DEFAULT_BG_COLOR if i % 2 == 0 else BG_HOVER_BUTTON
                        text_color = TEXT_COLOR if i % 2 == 0 else BUTTON_TEXT_COLOR

                        buttons = []
                        secret_type = None
                        if secret['type'] == "Masterseed" and secret['subtype'] == '0x1':
                            secret_type = "Mnemonic seedphrase"
                        values = [secret['id'], secret['type'] if not secret_type else secret_type, secret['label']]
                        for value, width in zip(values, header_widths):
                            cell_button = customtkinter.CTkButton(
                                row_frame, text=value,
                                text_color=text_color, fg_color=fg_color,
                                font=customtkinter.CTkFont(size=14, family='Outfit'),
                                hover_color=HIGHLIGHT_COLOR, corner_radius=0, width=width
                            )
                            cell_button.default_color = fg_color  # Store the default color
                            cell_button.pack(side='left', expand=True, fill="both")
                            buttons.append(cell_button)

                        # Bind hover events to change color for all buttons in the row
                        for button in buttons:
                            button.bind("<Enter>", lambda event, btns=buttons: _on_mouse_on_secret(event, btns))
                            button.bind("<Leave>", lambda event, btns=buttons: _on_mouse_out_secret(event, btns))
                            button.configure(command=lambda s=secret: _show_secret_details(s))

                        logger.debug(f"016 Row created for secret ID: {secret['id']}")
                    except Exception as e:
                        logger.error(f"017 Error creating row for secret {secret['id']}: {str(e)}")
                        raise UIElementError(f"018 Failed to create row for secret {secret['id']}") from e

                logger.log(SUCCESS, "019 Secrets table created successfully")
            except Exception as e:
                logger.error(f"020 Error in _create_secrets_table: {e}", exc_info=True)
                raise UIElementError(f"021 Failed to create secrets table: {e}") from e

        try:
            #_load_view_my_secrets()
            logger.info("view_my_secrets start")
            _create_secrets_frame()
            _create_secrets_header()
            _create_secrets_table(secrets_data)
            self.show_seedkeeper_menu()
            logger.log(SUCCESS, "Secrets frame created successfully")
        except Exception as e:
            error_msg = f"Failed to create secrets frame: {e}"
            logger.error(error_msg, exc_info=True)
            raise SecretFrameCreationError(error_msg) from e

    @log_method
    def _create_password_secret_frame(self, secret_details):
        try:
            logger.info("_create_password_secret_frame start")

            # Create field for label login, url and password
            try:
                label_label = self.create_label("Label:")
                label_label.place(relx=0.045, rely=0.2)
                self.label_entry = self._create_entry()
                self.label_entry.insert(0, secret_details['label'])
                self.label_entry.place(relx=0.045, rely=0.27)
                logger.debug("002 label fields created")

                login_label = self.create_label("Login:")
                login_label.place(relx=0.045, rely=0.34)
                self.login_entry = self._create_entry(show_option="*")
                self.login_entry.place(relx=0.045, rely=0.41)
                logger.debug("003 login fields created")

                url_label = self.create_label("Url:")
                url_label.place(relx=0.045, rely=0.48)
                self.url_entry = self._create_entry(show_option="*")
                self.url_entry.place(relx=0.045, rely=0.55)
                logger.debug("004 url fields created")

                password_label = self.create_label("Password:")
                password_label.place(relx=0.045, rely=0.7, anchor="w")
                self.password_entry = self._create_entry(show_option="*")
                self.password_entry.configure(width=500)
                self.password_entry.place(relx=0.04, rely=0.77, anchor="w")
                logger.debug("005 password fields created")

                # Decode secret
                try:
                    logger.debug("006 Decoding secret to show")
                    self.decoded_login_password = self.controller.decode_password(secret_details, binascii.unhexlify(secret_details['secret']))
                    logger.log(
                        SUCCESS, f"login password secret decoded successfully: {self.decoded_login_password}"
                    )
                except ValueError as e:
                    self.show("ERROR", f"Invalid secret format: {str(e)}", "Ok")
                except ControllerError as e:
                    self.show("ERROR", f"Failed to decode secret: {str(e)}", "Ok")

                self.login_entry.insert(0, self.decoded_login_password['login'])
                self.url_entry.insert(0, self.decoded_login_password['url'])
                self.password_entry.insert(0, self.decoded_login_password['password'][1:])

            except Exception as e:
                logger.error(f"008 Error creating fields: {e}", exc_info=True)
                raise UIElementError(f"009 Failed to create fields: {e}") from e

            def _toggle_password_visibility(login_entry, url_entry, password_entry):
                # todo: only hides secret, not login/url/... fields
                try:
                    # login
                    login_current_state = login_entry.cget("show")
                    login_new_state = "" if login_current_state == "*" else "*"
                    login_entry.configure(show=login_new_state)
                    # url
                    url_current_state =  url_entry.cget("show")
                    url_new_state = "" if url_current_state == "*" else "*"
                    url_entry.configure(show=url_new_state)
                    # password
                    password_current_state = password_entry.cget("show")
                    password_new_state = "" if password_current_state == "*" else "*"
                    password_entry.configure(show=password_new_state)
                except Exception as e:
                    logger.error(f"018 Error toggling password visibility: {e}", exc_info=True)
                    raise UIElementError(f"019 Failed to toggle password visibility: {e}") from e

            # Create action buttons
            try:
                show_button = self.create_button(
                    text="Show",
                    command=lambda: _toggle_password_visibility(
                        self.login_entry, self.url_entry, self.password_entry)
                )
                show_button.place(relx=0.9, rely=0.8, anchor="se")

                delete_button = self.create_button(
                    text="Delete secret",
                    command=lambda: [
                        self.show(
                            "WARNING",
                            "Are you sure to delete this secret ?!\n Click Yes for delete the secret or close popup",
                            "Yes",
                            lambda: [self.controller.cc.seedkeeper_reset_secret(secret_details['id']),
                                     self.show_view_my_secrets()],
                            './pictures_db/secrets_icon_popup.png'),
                        self.show_view_my_secrets()
                    ]
                )
                delete_button.place(relx=0.75, rely=0.98, anchor="se")
                logger.debug("010 Action buttons created")
            except Exception as e:
                logger.error(f"011 Error creating action buttons: {e}", exc_info=True)
                raise UIElementError(f"012 Failed to create action buttons: {e}") from e

            logger.log(SUCCESS, "013 Password secret frame created successfully")
        except Exception as e:
            logger.error(f"014 Unexpected error in _create_password_secret_frame: {e}", exc_info=True)
            raise ViewError(f"015 Failed to create password secret frame: {e}") from e

    @log_method
    def _create_masterseed_secret_frame(self, secret_details):
        try:
            logger.debug(f"masterseed_secret_details: {secret_details}")
            logger.info("001 Creating mnemonic secret frame")
            # Create labels and entry fields
            labels = ['Label:', 'Mnemonic type:']
            entries = {}

            for i, label_text in enumerate(labels):
                try:
                    label = self.create_label(label_text)
                    label.place(relx=0.045, rely=0.2 + i * 0.15, anchor="w")
                    logger.debug(f"Created label: {label_text}")

                    entry = self._create_entry()
                    entry.place(relx=0.04, rely=0.27 + i * 0.15, anchor="w")
                    entries[label_text.lower()[:-1]] = entry
                    logger.debug(f"Created entry for: {label_text}")
                except Exception as e:
                    logger.error(f"Error creating label or entry for {label_text}: {e}", exc_info=True)
                    raise UIElementError(f"Failed to create label or entry for {label_text}: {e}") from e

            # Set values to label and mnemonic type
            entries['label'].insert(0, secret_details['label'])
            entries['mnemonic type'].insert(0, secret_details['type'])

            # lock possibilities to wright into entries
            entries['label'].configure(state='disabled')
            entries['mnemonic type'].configure(state='disabled')
            logger.debug("Entry values set")

            if secret_details['secret'] != "Export failed: export not allowed by SeedKeeper policy.":
                # Decode seed to mnemonic
                try:
                    logger.debug("Decoding seed to mnemonic words")
                    secret = self.controller.decode_masterseed(secret_details)
                    mnemonic = secret['mnemonic']
                    passphrase = secret['passphrase']
                except Exception as e:
                    logger.error(f"Error decoding Masterseed: {e}", exc_info=True)
                    raise ControllerError(f"015 Failed to decode Masterseed: {e}") from e
            else:
                mnemonic = secret_details['secret']
                passphrase = secret_details['secret']

            # Create mnemonic field
            try:
                mnemonic_label = self.create_label("Mnemonic:")
                mnemonic_label.place(relx=0.045, rely=0.65, anchor="w")

                mnemonic_textbox = self._create_textbox()
                mnemonic_textbox.place(relx=0.04, rely=0.8, relheight=0.23, anchor="w")
                mnemonic_textbox.insert("1.0", '*' * len(mnemonic))
                logger.debug("013 Mnemonic field created")
            except Exception as e:
                logger.error(f"014 Error creating mnemonic field: {e}", exc_info=True)
                raise UIElementError(f"015 Failed to create mnemonic field: {e}") from e

            # Function to toggle visibility of mnemonic
            @log_method
            def _toggle_mnemonic_visibility(textbox, original_text):
                try:
                    logger.info("016 Toggling mnemonic visibility")
                    textbox.configure(state='normal')
                    # Obtenir le contenu actuel de la textbox
                    current_text = textbox.get("1.0", "end-1c")

                    if current_text == '*' * len(original_text):
                        # Si la textbox contient uniquement des étoiles, afficher le texte original
                        textbox.delete("1.0", "end")
                        textbox.insert("1.0", original_text)
                        textbox.configure(state='disabled')
                        logger.log(SUCCESS, "017 Mnemonic visibility toggled to visible")
                    else:
                        # Sinon, masquer le texte avec des étoiles
                        textbox.delete("1.0", "end")
                        textbox.insert("1.0", '*' * len(original_text))
                        textbox.configure(state='disabled')
                        logger.log(SUCCESS, "017 Mnemonic visibility toggled to hidden")

                except Exception as e:
                    logger.error(f"018 Error toggling mnemonic visibility: {e}", exc_info=True)
                    raise UIElementError(f"019 Failed to toggle mnemonic visibility: {e}") from e

            # Create action buttons
            try:
                delete_button = self.create_button(
                    text="Delete secret",
                    command=lambda: [
                        self.show(
                            "WARNING",
                            "Are you sure to delete this secret ?!\n Click Yes for delete the secret or close popup",
                            "Yes",
                            lambda: [self.controller.cc.seedkeeper_reset_secret(secret_details['id']),
                                     self.show_view_my_secrets()],
                            './pictures_db/secrets_icon_popup.png'),
                        self.show_view_my_secrets()
                    ]
                )
                delete_button.place(relx=0.75, rely=0.98, anchor="se")

                show_button = self.create_button(text="Show",
                                                  command=lambda: [_toggle_mnemonic_visibility(mnemonic_textbox, mnemonic)])
                show_button.place(relx=0.95, rely=0.8, anchor="e")
                logger.debug("020 Action buttons created")
            except Exception as e:
                logger.error(f"021 Error creating action buttons: {e}", exc_info=True)
                raise UIElementError(f"022 Failed to create action buttons: {e}") from e

            logger.log(SUCCESS, "023 Mnemonic secret frame created successfully")
        except Exception as e:
            logger.error(f"024 Unexpected error in _create_mnemonic_secret_frame: {e}", exc_info=True)
            raise ViewError(f"025 Failed to create mnemonic secret frame: {e}") from e

    @log_method
    def _create_mnemonic_secret_frame(self, secret_details):
        try:

            logger.debug(f"masterseed_secret_details: {secret_details}")
            logger.info("001 Creating mnemonic secret frame")
            # Create labels and entry fields
            labels = ['Label:', 'Mnemonic type:']
            entries = {}

            for i, label_text in enumerate(labels):
                try:
                    label = self.create_label(label_text)
                    label.place(relx=0.045, rely=0.2 + i * 0.15, anchor="w")
                    logger.debug(f"Created label: {label_text}")

                    entry = self._create_entry()
                    entry.place(relx=0.04, rely=0.255 + i * 0.15, anchor="w")
                    entries[label_text.lower()[:-1]] = entry
                    logger.debug(f"Created entry for: {label_text}")
                except Exception as e:
                    logger.error(f"Error creating label or entry for {label_text}: {e}", exc_info=True)
                    raise UIElementError(f"Failed to create label or entry for {label_text}: {e}") from e

            # Set values to label and mnemonic type
            entries['label'].insert(0, secret_details['label'])
            entries['mnemonic type'].insert(0, 'Mnemonic seedphrase')


            # lock possibilities to wright into entries
            entries['label'].configure(state='disabled')
            entries['mnemonic type'].configure(state='disabled')
            logger.debug("Entry values set")

            def show_seed_qr_code():
                import pyqrcode
                # Fonction pour générer et afficher le QR code
                qr_data = f'{mnemonic} {passphrase if passphrase else ""}'
                qr = pyqrcode.create(qr_data, error='L')
                qr_xbm = qr.xbm(scale=3) if len(mnemonic.split()) <=12 else qr.xbm(scale=2)
                # Convertir le code XBM en image Tkinter
                qr_bmp = tkinter.BitmapImage(data=qr_xbm)
                label = self.create_label("")
                label.place(relx=0.8, rely=0.4)
                label.configure(image=qr_bmp)
                label.image = qr_bmp  # Prévenir le garbage collection

            # seed_qr button
            try:
                seedqr_button = self.create_button(text="SeedQR",
                                                    command=lambda: show_seed_qr_code())
                seedqr_button.place(relx=0.78, rely=0.51, anchor="se")
                logger.debug("SeedQR buttons created")
            except Exception as e:
                logger.error(f"Error creating Xpub and SeedQR buttons: {e}", exc_info=True)
                raise UIElementError(f"Failed to create Xpub and SeedQR buttons: {e}") from e

            if secret_details['secret'] != "Export failed: export not allowed by SeedKeeper policy.":
                # Decode seed to mnemonic
                try:
                    logger.debug("Decoding seed to mnemonic words")
                    secret = self.controller.decode_masterseed(secret_details)
                    mnemonic = secret['mnemonic']
                    passphrase = secret['passphrase']
                    print(passphrase)
                except Exception as e:
                    logger.error(f"Error decoding Masterseed: {e}", exc_info=True)
                    raise ControllerError(f"015 Failed to decode Masterseed: {e}") from e
            else:
                mnemonic = secret_details['secret']
                passphrase = secret_details['secret']

            # Create passphrase field
            try:
                passphrase_label = self.create_label("Passphrase:")
                passphrase_label.place(relx=0.045, rely=0.56, anchor="w")

                passphrase_entry = self._create_entry()
                passphrase_entry.place(relx=0.2, rely=0.56, anchor="w", relwidth=0.585)
                passphrase_entry.insert(0, '*' * len(
                    passphrase) if passphrase != '' else 'None')  # Masque la passphrase
                logger.debug("010 Passphrase field created")
            except Exception as e:
                logger.error(f"011 Error creating passphrase field: {e}", exc_info=True)
                raise UIElementError(f"012 Failed to create passphrase field: {e}") from e

            # Create mnemonic field
            try:
                mnemonic_label = self.create_label("Mnemonic:")
                mnemonic_label.place(relx=0.045, rely=0.63, anchor="w")

                self.seed_mnemonic_textbox = self._create_textbox()
                self.seed_mnemonic_textbox.place(relx=0.04, rely=0.77, relheight=0.23, anchor="w")
                self.seed_mnemonic_textbox.insert("1.0", '*' * len(mnemonic))
                logger.debug("013 Mnemonic field created")
            except Exception as e:
                logger.error(f"014 Error creating mnemonic field: {e}", exc_info=True)
                raise UIElementError(f"015 Failed to create mnemonic field: {e}") from e

            # Function to toggle visibility of passphrase
            @log_method
            def _toggle_passphrase_visibility(entry, original_text):
                try:
                    entry.configure(state='normal')
                    logger.info("020 Toggling passphrase visibility")
                    # retrieve the content from actual entry
                    current_text = entry.get()

                    if current_text == '*' * len(original_text):
                        # if entry contains only stars, logger.debug origina text
                        entry.delete(0, "end")
                        entry.insert(0, original_text)
                        logger.log(SUCCESS, "021 Passphrase visibility toggled to visible")
                        entry.configure(state='disabled')
                    else:
                        entry.delete(0, "end")
                        entry.insert(0, '*' * len(original_text))
                        entry.configure(state='disabled')
                        logger.log(SUCCESS, "021 Passphrase visibility toggled to hidden")

                except Exception as e:
                    logger.error(f"022 Error toggling passphrase visibility: {e}", exc_info=True)
                    raise UIElementError(f"023 Failed to toggle passphrase visibility: {e}") from e

            # Function to toggle visibility of mnemonic
            @log_method
            def _toggle_mnemonic_visibility(textbox, original_text):
                try:
                    logger.info("016 Toggling mnemonic visibility")
                    textbox.configure(state='normal')
                    # Obtenir le contenu actuel de la textbox
                    current_text = textbox.get("1.0", "end-1c")

                    if current_text == '*' * len(original_text):
                        # Si la textbox contient uniquement des étoiles, afficher le texte original
                        textbox.delete("1.0", "end")
                        textbox.insert("1.0", original_text)
                        textbox.configure(state='disabled')
                        logger.log(SUCCESS, "017 Mnemonic visibility toggled to visible")
                    else:
                        # Sinon, masquer le texte avec des étoiles
                        textbox.delete("1.0", "end")
                        textbox.insert("1.0", '*' * len(original_text))
                        textbox.configure(state='disabled')
                        logger.log(SUCCESS, "017 Mnemonic visibility toggled to hidden")

                except Exception as e:
                    logger.error(f"018 Error toggling mnemonic visibility: {e}", exc_info=True)
                    raise UIElementError(f"019 Failed to toggle mnemonic visibility: {e}") from e

            # Create action buttons
            try:
                delete_button = self.create_button(
                    text="Delete secret",
                    command=lambda: [
                        self.show(
                            "WARNING",
                            "Are you sure to delete this secret ?!\n Click Yes for delete the secret or close popup",
                            "Yes",
                            lambda: [self.controller.cc.seedkeeper_reset_secret(secret_details['id']), self.show_view_my_secrets()],
                            './pictures_db/secrets_icon_popup.png'),
                        self.show_view_my_secrets()
                    ]
                )
                delete_button.place(relx=0.75, rely=0.95, anchor="e")

                show_button = self.create_button(text="Show",
                                                  command=lambda: [_toggle_mnemonic_visibility(self.seed_mnemonic_textbox, mnemonic), _toggle_passphrase_visibility(passphrase_entry, passphrase)])
                show_button.place(relx=0.95, rely=0.8, anchor="e")
                logger.debug("020 Action buttons created")
            except Exception as e:
                logger.error(f"021 Error creating action buttons: {e}", exc_info=True)
                raise UIElementError(f"022 Failed to create action buttons: {e}") from e

            logger.log(SUCCESS, "023 Mnemonic secret frame created successfully")
        except Exception as e:
            logger.error(f"024 Unexpected error in _create_mnemonic_secret_frame: {e}", exc_info=True)
            raise ViewError(f"025 Failed to create mnemonic secret frame: {e}") from e

    @log_method
    def _create_2FA_secret_frame(self, secret_details):
        try:
            logger.debug(f"2FA secret details: {secret_details}")
            self.label_2FA = self.create_label('Label:')
            self.label_2FA.place(relx=0.045, rely=0.2)
            self.label_2FA_entry = self._create_entry()
            self.label_2FA_entry.place(relx=0.045, rely=0.25)
            self.label_2FA_entry.insert(0, secret_details['label'])

            self.secret_2FA_label = self.create_label('Secret:')
            self.secret_2FA_label.place(relx=0.045, rely=0.32)
            self.secret_2FA_entry = self._create_entry(show_option="*")
            self.secret_2FA_entry.place(relx=0.045, rely=0.37)
            self.secret_2FA_entry.configure(width=450)
            self.secret_2FA_entry.insert(0, secret_details['secret'][2:])

            def _toggle_2FA_visibility(secret_2FA_entry):
                try:
                    # secret 2FA
                    secret_2FA_current_state = secret_2FA_entry.cget("show")
                    secret_2FA_new_state = "" if secret_2FA_current_state == "*" else "*"
                    secret_2FA_entry.configure(show=secret_2FA_new_state)

                    logger.log(
                        SUCCESS,
                        f"{'hidden' if (secret_2FA_new_state) == '*' else 'visible'}"
                    )
                except Exception as e:
                    logger.error(f"Error toggling password visibility: {e}", exc_info=True)
                    raise UIElementError(f"Failed to toggle password visibility: {e}") from e

            # Create action buttons
            try:
                show_button = self.create_button(
                    text="Show",
                    command=lambda: _toggle_2FA_visibility(self.secret_2FA_entry))
                show_button.place(relx=0.9, rely=0.433, anchor="se")

                delete_button = self.create_button(
                    text="Delete secret",
                    command=lambda: [
                        self.show(
                            "WARNING",
                            "Are you sure to delete this secret ?!\n Click Yes for delete the secret or close popup",
                            "Yes",
                            lambda: [self.controller.cc.seedkeeper_reset_secret(secret_details['id']),
                                     self.show_view_my_secrets()],
                            './pictures_db/secrets_icon_popup.png'),
                        self.show_view_my_secrets()
                    ]
                )
                delete_button.place(relx=0.75, rely=0.95, anchor="e")
                logger.debug("Action buttons created")
            except Exception as e:
                logger.error(f"Error creating action buttons: {e}", exc_info=True)
                raise UIElementError(f"Failed to create action buttons: {e}") from e
            logger.log(SUCCESS, "Generic secret frame created")
        except Exception as e:
            logger.error(f"Error creating generic secret frame: {e}", exc_info=True)
            raise UIElementError(f"Failed to create generic secret frame: {e}")

    @log_method
    def _create_generic_secret_frame(self, secret_details):
        try:
            for key, value in secret_details.items():
                label = self.create_label(f"{key}:")
                label.place(relx=0.1, rely=0.2 + len(secret_details) * 0.05, anchor="w")

                entry = self._create_entry(show_option="*" if key.lower() == "value" else None)
                entry.insert(0, value)
                entry.configure(state="readonly")
                entry.place(relx=0.3, rely=0.2 + len(secret_details) * 0.05, anchor="w")

            logger.log(SUCCESS, "Generic secret frame created")
        except Exception as e:
            logger.error(f"Error creating generic secret frame: {e}", exc_info=True)
            raise UIElementError(f"Failed to create generic secret frame: {e}")

    @log_method
    def _create_free_text_secret_frame(self, secret_details):
        try:
            logger.info("Creating free text secret frame to display secret details")

            # Create field for label
            label_label = self.create_label("Label:")
            label_label.place(relx=0.045, rely=0.2)
            self.label_entry = self._create_entry()
            self.label_entry.insert(0, secret_details['label'])
            self.label_entry.place(relx=0.045, rely=0.27)
            self.label_entry.configure(state='disabled')
            logger.debug("Label field created")

            # Create field for free text content
            free_text_label = self.create_label("Free Text Content:")
            free_text_label.place(relx=0.045, rely=0.34)
            self.free_text_textbox = self._create_textbox()
            self.free_text_textbox.place(relx=0.045, rely=0.41, relheight=0.4, relwidth=0.7)
            logger.debug("Free text content field created")

            # Decode secret
            try:
                logger.debug("Decoding free text to show")
                self.decoded_text = self.controller.decode_free_text(secret_details)
                free_text = self.decoded_text['text']
                logger.log(SUCCESS, f"Free text secret decoded successfully")
            except ValueError as e:
                self.show("ERROR", f"Invalid secret format: {str(e)}", "Ok")
            except ControllerError as e:
                self.show("ERROR", f"Failed to decode secret: {str(e)}", "Ok")

            # Insert decoded text into textbox
            self.free_text_textbox.insert("1.0", '*' * len(self.decoded_text['text']))
            self.free_text_textbox.configure(state='disabled')

            # Function to toggle visibility of free text
            @log_method
            def _toggle_free_text_visibility(free_text_textbox, original_text):
                try:
                    logger.info("Toggling Free text visibility")
                    free_text_textbox.configure(state='normal')
                    # Obtenir le contenu actuel de la textbox
                    current_text = free_text_textbox.get("1.0", "end-1c")

                    if current_text == '*' * len(original_text):
                        # Si la textbox contient uniquement des étoiles, afficher le texte original
                        free_text_textbox.delete("1.0", "end")
                        free_text_textbox.insert("1.0", original_text)
                        free_text_textbox.configure(state='disabled')
                        logger.log(SUCCESS, "Free text visibility toggled to visible")
                    else:
                        # Sinon, masquer le texte avec des étoiles
                        free_text_textbox.delete("1.0", "end")
                        free_text_textbox.insert("1.0", '*' * len(original_text))
                        free_text_textbox.configure(state='disabled')
                        logger.log(SUCCESS, "Free text visibility toggled to hidden")

                except Exception as e:
                    logger.error(f"Error toggling Free text visibility: {e}", exc_info=True)
                    raise UIElementError(f"Failed to toggle Free text visibility: {e}") from e

            # Create action buttons
            try:
                show_button = self.create_button(
                    text="Show",
                    command=lambda: _toggle_free_text_visibility(self.free_text_textbox, free_text)
                )
                show_button.place(relx=0.95, rely=0.65, anchor="se")

                delete_button = self.create_button(
                    text="Delete secret",
                    command=lambda: [
                        self.show(
                            "WARNING",
                            "Are you sure to delete this secret ?!\n Click Yes for delete the secret or close popup",
                            "Yes",
                            lambda: [self.controller.cc.seedkeeper_reset_secret(secret_details['id']),
                                     self.show_view_my_secrets()],
                            './pictures_db/secrets_icon_popup.png'),
                        self.show_view_my_secrets()
                    ]
                )
                delete_button.place(relx=0.75, rely=0.98, anchor="se")
                logger.debug("Action buttons created")
            except Exception as e:
                logger.error(f"Error creating action buttons: {e}", exc_info=True)
                raise UIElementError(f"Failed to create action buttons: {e}") from e

            logger.log(SUCCESS, "Free text secret frame created successfully")
        except Exception as e:
            logger.error(f"Unexpected error in _create_free_text_secret_frame: {e}", exc_info=True)
            raise ViewError(f"Failed to create free text secret frame: {e}") from e

    @log_method
    def _create_wallet_descriptor_secret_frame(self, secret_details):
        try:
            logger.info("Creating wallet descriptor secret frame to display secret details")

            # Create field for label
            label_label = self.create_label("Label:")
            label_label.place(relx=0.045, rely=0.2)
            self.label_entry = self._create_entry()
            self.label_entry.insert(0, secret_details['label'])
            self.label_entry.place(relx=0.045, rely=0.27)
            self.label_entry.configure(state='disabled')
            logger.debug("Label field created")

            # Create field for wallet descriptor content
            wallet_descriptor_label = self.create_label("Wallet Descriptor Content:")
            wallet_descriptor_label.place(relx=0.045, rely=0.34)
            self.wallet_descriptor_textbox = self._create_textbox()
            self.wallet_descriptor_textbox.place(relx=0.045, rely=0.41, relheight=0.4, relwidth=0.7)
            logger.debug("Wallet descriptor content field created")

            # Decode secret
            try:
                logger.debug("Decoding wallet descriptor to show")
                self.decoded_text = self.controller.decode_wallet_descriptor(secret_details)
                wallet_descriptor = self.decoded_text['descriptor']
                logger.log(SUCCESS, f"Wallet descriptor secret decoded successfully")
            except ValueError as e:
                self.show("ERROR", f"Invalid secret format: {str(e)}", "Ok")
            except ControllerError as e:
                self.show("ERROR", f"Failed to decode secret: {str(e)}", "Ok")

            # Insert decoded text into textbox
            self.wallet_descriptor_textbox.insert("1.0", '*' * len(self.decoded_text['descriptor']))
            self.wallet_descriptor_textbox.configure(state='disabled')

            # Function to toggle visibility of wallet descriptor
            @log_method
            def _toggle_wallet_descriptor_visibility(wallet_descriptor_textbox, original_text):
                try:
                    logger.info("Toggling Wallet descriptor visibility")
                    wallet_descriptor_textbox.configure(state='normal')
                    # Obtenir le contenu actuel de la textbox
                    current_text = wallet_descriptor_textbox.get("1.0", "end-1c")

                    if current_text == '*' * len(original_text):
                        # Si la textbox contient uniquement des étoiles, afficher le texte original
                        wallet_descriptor_textbox.delete("1.0", "end")
                        wallet_descriptor_textbox.insert("1.0", original_text)
                        wallet_descriptor_textbox.configure(state='disabled')
                        logger.log(SUCCESS, "Wallet descriptor visibility toggled to visible")
                    else:
                        # Sinon, masquer le texte avec des étoiles
                        wallet_descriptor_textbox.delete("1.0", "end")
                        wallet_descriptor_textbox.insert("1.0", '*' * len(original_text))
                        wallet_descriptor_textbox.configure(state='disabled')
                        logger.log(SUCCESS, "Wallet descriptor visibility toggled to hidden")

                except Exception as e:
                    logger.error(f"Error toggling Wallet descriptor visibility: {e}", exc_info=True)
                    raise UIElementError(f"Failed to toggle Wallet descriptor visibility: {e}") from e

            # Create action buttons
            try:
                show_button = self.create_button(text="Show",
                                                  command=lambda: _toggle_wallet_descriptor_visibility(
                                                      self.wallet_descriptor_textbox, wallet_descriptor))
                show_button.place(relx=0.95, rely=0.65, anchor="se")

                delete_button = self.create_button(
                    text="Delete secret",
                    command=lambda: [
                        self.show(
                            "WARNING",
                            "Are you sure to delete this secret ?!\n Click Yes for delete the secret or close popup",
                            "Yes",
                            lambda: [self.controller.cc.seedkeeper_reset_secret(secret_details['id']),
                                     self.show_view_my_secrets()],
                            './pictures_db/secrets_icon_popup.png'),
                        self.show_view_my_secrets()
                    ]
                )
                delete_button.place(relx=0.75, rely=0.98, anchor="se")
                logger.debug("Action buttons created")
            except Exception as e:
                logger.error(f"Error creating action buttons: {e}", exc_info=True)
                raise UIElementError(f"Failed to create action buttons: {e}") from e

            logger.log(SUCCESS, "Wallet descriptor secret frame created successfully")
        except Exception as e:
            logger.error(f"Unexpected error in _create_wallet_descriptor_secret_frame: {e}", exc_info=True)
            raise ViewError(f"Failed to create wallet descriptor secret frame: {e}") from e




