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
from frameCardEditLabel import FrameCardEditLabel
from frameMenuNoCard import FrameMenuNoCard
from frameMenuSeedkeeper import FrameMenuSeedkeeper
from frameMenuSettings import FrameMenuSettings
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
            self.setup_card_frame = self.create_setup_card_frame()
        self.setup_card_frame.tkraise()

    def create_setup_card_frame(self):
        logger.info(f"IN View.create_setup_card_frame()")
        try:
            # Creating new frame
            setup_frame = self.create_frame(width=750, height=600, frame=self.main_frame)
            setup_frame.place(relx=1, rely=0.5, anchor="e")

            # Creating main menu
            #self.show_settings_menu()# todo update setup status

            # Creating header
            header = self.create_an_header(f"Setup my card",
                                                "change_pin_popup.jpg", frame=setup_frame)
            header.place(relx=0.05, rely=0.05, anchor="nw")

            # setup paragraph
            text = self.create_label("Create your card PIN code.", frame=setup_frame)
            text.place(relx=0.05, rely=0.2, anchor="w")
            text = View.create_label(self, "A PIN code must be between 4 and 16 characters.", frame = setup_frame)
            text.place(relx=0.05, rely=0.25, anchor="w")
            text = View.create_label(self, "You can use symbols, lower and upper cases, letters and numbers.", frame = setup_frame)
            text.place(relx=0.05, rely=0.3, anchor="w")

            # edit PIN
            edit_pin_label = View.create_label(self, "New PIN code :", frame=setup_frame)
            edit_pin_label.configure(font=self.make_text_size_at(18))
            edit_pin_label.place(relx=0.05, rely=0.45, anchor="w")
            edit_pin_entry = View.create_entry(self, "*", frame=setup_frame)
            self.after(100, edit_pin_entry.focus_force)
            if self.controller.cc.card_type == "Satodime":
                edit_pin_entry.configure(state='disabled')
            edit_pin_entry.place(relx=0.05, rely=0.52, anchor="w")

            # confirm PIN edition
            edit_confirm_pin_label = View.create_label(self, "Repeat new PIN code :", frame=setup_frame)
            edit_confirm_pin_label.configure(font=self.make_text_size_at(18))
            edit_confirm_pin_label.place(relx=0.05, rely=0.65, anchor="w")
            edit_confirm_pin_entry = View.create_entry(self, "*", frame=setup_frame)
            if self.controller.cc.card_type == "Satodime":
                edit_confirm_pin_entry.configure(state='disabled')
            edit_confirm_pin_entry.place(relx=0.05, rely=0.72, anchor="w")

            # Creating cancel and finish buttons
            cancel_button = View.create_button(
                self, "Cancel",
                lambda: self.show_start_frame(),
                frame=setup_frame
            )
            cancel_button.place(relx=0.6, rely=0.9, anchor="w")

            # todo: check pin & pin_confirm match
            finish_button = View.create_button(
                self, "Save PIN",
                lambda: self.controller.setup_card_pin(edit_pin_entry.get(), edit_confirm_pin_entry.get()),
                frame = setup_frame
            )
            finish_button.place(relx=0.8, rely=0.9, anchor="w")
            self.bind('<Return>', lambda event: self.controller.setup_card_pin(edit_pin_entry.get(), edit_confirm_pin_entry.get()))

            return setup_frame
        except Exception as e:
            logger.error(f"An unexpected error occurred in setup_my_card_pin: {e}", exc_info=True)

    def show_seed_import_frame(self):
        if self.seed_import_frame is None:
            self.seed_import_frame = self.create_seed_import_frame()
        else:
            self.seed_import_frame.place()
            self.seed_import_frame.tkraise()

    def create_seed_import_frame(self):
        try:
            # Creating new frame
            seed_import_frame = View.create_frame(self, width=750, height=600, frame=self.main_frame)
            seed_import_frame.place(relx=1.0, rely=0.5, anchor="e")

            # Creating main menu # todo remove?
            #self.show_settings_menu()

            # Creating header
            header = View.create_an_header(
                self, "Seed My Card", "seed_popup.jpg",
                frame=seed_import_frame
            )
            header.place(relx=0.05, rely=0.05, anchor="nw")

            # setup paragraph
            text = View.create_label(
                self,
                "Set up your Satochip hardware wallet as a new device to get started.",
                frame=seed_import_frame
            )
            text.place(relx=0.05, rely=0.17, anchor="w")
            text = View.create_label(
                self,
                "Import or generate a new mnemonic seedphrase and generate new",
                frame=seed_import_frame
            )
            text.place(relx=0.05, rely=0.22, anchor="w")
            text = View.create_label(
                self,
                "private keys that will be stored within the chip memory.",
                frame=seed_import_frame
            )
            text.place(relx=0.05, rely=0.27, anchor="w")

            radio_value = customtkinter.StringVar(value="")
            value_checkbox_passphrase = customtkinter.StringVar(value="off")
            radio_value_mnemonic = customtkinter.StringVar(value="")
            generate_with_passphrase = False  # use a passphrase?
            logger.debug(
                f"Settings radio_value: {radio_value}, generate_with_passphrase: {generate_with_passphrase}")

            def on_text_box_click(event):
                if text_box.get("1.0", "end-1c") == "Type your existing seedphrase here":
                    text_box.delete("1.0", "end")

            def update_radio_mnemonic_length():
                if radio_value_mnemonic.get() == "generate_12":
                    mnemonic_length = 12
                elif radio_value_mnemonic.get() == "generate_24":
                    mnemonic_length = 24

                mnemonic = self.controller.generate_random_seed(mnemonic_length)
                self.update_textbox(text_box, mnemonic)
                #self.update_textbox_old(mnemonic)

            def update_radio_selection():
                nonlocal generate_with_passphrase
                self.import_seed = False # todo

                if radio_value.get() == "import":
                    self.import_seed = True
                    logger.debug("Import seed")
                    #self.cancel_button.place_forget()
                    finish_button.place(relx=0.8, rely=0.9, anchor="w")
                    cancel_button.place(relx=0.6, rely=0.9, anchor="w")
                    radio_button_generate_seed.place_forget()
                    radio_button_import_seed.place_forget()
                    radio_button_generate_12_words.place_forget()
                    radio_button_generate_24_words.place_forget()
                    passphrase_entry.place_forget()
                    text_box.place_forget()
                    warning_label.place_forget()
                    radio_button_import_seed.place(relx=0.05, rely=0.35, anchor="w")
                    text_box.delete(1.0, "end")
                    text_box.configure(width=550, height=80)
                    text_box.insert(text="Type your existing seedphrase here", index=1.0)
                    text_box.bind("<FocusIn>", on_text_box_click)
                    text_box.place(relx=0.13, rely=0.45, anchor="w")
                    checkbox_passphrase.place(relx=0.13, rely=0.58, anchor="w")
                    radio_button_generate_seed.place(relx=0.05, rely=0.75, anchor="w")

                elif radio_value.get() == "generate":
                    self.import_seed = False
                    logger.debug("Generate seed")
                    cancel_button.place_forget()
                    finish_button.place(relx=0.8, rely=0.9, anchor="w")
                    cancel_button.place(relx=0.6, rely=0.9, anchor="w")
                    radio_button_import_seed.place_forget()
                    radio_button_generate_seed.place_forget()
                    checkbox_passphrase.place_forget()
                    passphrase_entry.place_forget()
                    text_box.delete(1.0, "end")
                    text_box.place_forget()
                    warning_label.place_forget()
                    radio_button_import_seed.place(relx=0.05, rely=0.35, anchor="w")
                    radio_button_generate_seed.place(relx=0.05, rely=0.41, anchor="w")
                    radio_button_generate_12_words.place(relx=0.17, rely=0.47, anchor="w")
                    radio_button_generate_24_words.place(relx=0.37, rely=0.47, anchor="w")
                    text_box.configure(width=550, height=80)
                    text_box.place(relx=0.16, rely=0.56, anchor="w")
                    warning_label.place(relx=0.36, rely=0.64, anchor="w")
                    checkbox_passphrase.place(relx=0.17, rely=0.70, anchor="w")

            def update_checkbox_passphrase():
                nonlocal generate_with_passphrase
                if radio_value.get() == "import":
                    if value_checkbox_passphrase.get() == "on":
                        logger.debug("Generate seed with passphrase")
                        generate_with_passphrase = True
                        passphrase_entry.place_forget()
                        passphrase_entry.place(relx=0.13, rely=0.65, anchor="w")
                        passphrase_entry.configure(placeholder_text="Type your passphrase here")
                    else:
                        generate_with_passphrase = False
                        passphrase_entry.place_forget()

                elif radio_value.get() == "generate":
                    if value_checkbox_passphrase.get() == "on":
                        logger.debug("Generate seed with passphrase")
                        generate_with_passphrase = True
                        passphrase_entry.place_forget()
                        passphrase_entry.place(relx=0.16, rely=0.76, anchor="w")
                        passphrase_entry.configure(placeholder_text="Type your passphrase here")
                    else:
                        generate_with_passphrase = False
                        passphrase_entry.place_forget()

            # def update_verify_pin(): # todo move one level up
            #     if self.controller.cc.is_pin_set():
            #         self.controller.cc.card_verify_PIN_simple()
            #     else:
            #         self.controller.PIN_dialog(f'Unlock your {self.controller.cc.card_type}')

            # Setting up radio buttons and entry fields
            radio_button_import_seed = customtkinter.CTkRadioButton(
                seed_import_frame,
                text="I already have a seedphrase",
                variable=radio_value, value="import",
                font=customtkinter.CTkFont(family="Outfit", size=14, weight="normal"),
                bg_color="whitesmoke", fg_color="green", hover_color="green",
                command=update_radio_selection
            )
            radio_button_import_seed.place(relx=0.05, rely=0.35, anchor="w")

            radio_button_generate_seed = customtkinter.CTkRadioButton(
                seed_import_frame,
                text="I want to generate a new seedphrase",
                variable=radio_value, value="generate",
                font=customtkinter.CTkFont(family="Outfit", size=14, weight="normal"),
                bg_color="whitesmoke", fg_color="green",
                hover_color="green",
                command=update_radio_selection,
            )
            radio_button_generate_seed.place(relx=0.05, rely=0.42, anchor="w")

            radio_button_generate_12_words = customtkinter.CTkRadioButton(
                seed_import_frame,
                text="12 words",
                variable=radio_value_mnemonic,
                value="generate_12",
                font=customtkinter.CTkFont(family="Outfit", size=14, weight="normal"),
                bg_color="whitesmoke", fg_color="green",
                hover_color="green",
                command=update_radio_mnemonic_length
            )
            radio_button_generate_24_words = customtkinter.CTkRadioButton(
                seed_import_frame,
                text="24 words",
                variable=radio_value_mnemonic,
                value="generate_24",
                font=customtkinter.CTkFont(family="Outfit", size=14, weight="normal"),
                bg_color="whitesmoke", fg_color="green",
                hover_color="green",
                command=update_radio_mnemonic_length
            )

            checkbox_passphrase = customtkinter.CTkCheckBox(
                seed_import_frame,
                text="Use a passphrase (optional)",
                command=update_checkbox_passphrase,
                variable=value_checkbox_passphrase,
                onvalue="on",
                offvalue="off")

            passphrase_entry = View.create_entry(self, frame=seed_import_frame)

            text_box = customtkinter.CTkTextbox(
                seed_import_frame, corner_radius=20,
                bg_color="whitesmoke", fg_color=BUTTON_COLOR,
                border_color=BUTTON_COLOR, border_width=1,
                width=557, height=83,
                text_color="grey",
                font=customtkinter.CTkFont(family="Outfit", size=13,weight="normal")
            )

            warning_label = customtkinter.CTkLabel(
                seed_import_frame,
                text="Your mnemonic is important, be sure to save it in a safe place!",
                text_color="red",
                font=customtkinter.CTkFont(family="Outfit", size=12, weight="normal")
            )

            cancel_button = View.create_button(
                self, "Back",
                command=lambda: self.show_start_frame(),
                frame=seed_import_frame
            )
            cancel_button.place(relx=0.8, rely=0.9, anchor="w")

            finish_button = View.create_button(  # will be placed after mnemonic is generated
                self, "Import",
                command=lambda: [
                    self.update_verify_pin(),
                    self.controller.import_seed(
                        text_box.get(1.0, "end-1c"),
                        passphrase_entry.get() if generate_with_passphrase else None,
                    )
                ],
                frame=seed_import_frame
            )

            return seed_import_frame

        except Exception as e:
            logger.error(f"An unexpected error occurred in create_seed_import_frame: {e}", exc_info=True)

    def show_change_pin_frame(self):
        if self.change_pin_frame is None:
            self.change_pin_frame = self.create_change_pin_frame()
        self.change_pin_frame.place()
        self.change_pin_frame.tkraise()

    def create_change_pin_frame(self):
        try:
            logger.info("IN View.create_change_pin_frame() start")

            # Creating new frame
            change_pin_frame = View.create_frame(self, width=750, height=600, frame=self.main_frame)
            change_pin_frame.place(relx=1.0, rely=0.5, anchor="e")

            # Creating header
            self.header = View.create_an_header(
                self, "Change PIN ", "change_pin_popup.jpg",
                frame=change_pin_frame
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            #setup paragraph
            text = View.create_label(
                self,
                "Change your personal PIN code. ",
                frame=change_pin_frame
            )
            text.place(relx=0.05, rely=0.17, anchor="w")
            text = View.create_label(
                self,
                "A PIN code must be between 4 and 16 characters.",
                frame=change_pin_frame
            )
            text.place(relx=0.05, rely=0.22, anchor="w")
            text = View.create_label(
                self,
                "You can use symbols, lower and upper cases, letters and numbers.",
                frame=change_pin_frame
            )
            text.place(relx=0.05, rely=0.27, anchor="w")

            # Setting up PIN entry fields
            # input current PIN
            current_pin_label = View.create_label(self, "Current PIN:", frame=change_pin_frame)
            current_pin_label.configure(font=self.make_text_size_at(18))
            current_pin_label.place(relx=0.05, rely=0.40, anchor="w")
            current_pin_entry = View.create_entry(self, "*", frame=change_pin_frame)
            self.after(100, current_pin_entry.focus_force)
            current_pin_entry.place(relx=0.05, rely=0.45, anchor="w")

            # input new PIN
            new_pin_label = View.create_label(self, "New PIN code:", frame=change_pin_frame)
            new_pin_label.configure(font=self.make_text_size_at(18))
            new_pin_label.place(relx=0.05, rely=0.55, anchor="w")
            new_pin_entry = View.create_entry(self, "*", frame=change_pin_frame)
            new_pin_entry.place(relx=0.05, rely=0.60, anchor="w")

            # confirm new PIN
            confirm_new_pin_label = View.create_label(self, "Repeat new PIN code:", frame=change_pin_frame)
            confirm_new_pin_label.configure(font=self.make_text_size_at(18))
            confirm_new_pin_label.place(relx=0.05, rely=0.70, anchor="w")
            confirm_new_pin_entry = View.create_entry(self, "*", frame=change_pin_frame)
            confirm_new_pin_entry.place(relx=0.05, rely=0.75, anchor="w")

            # Creating cancel and finish buttons
            cancel_button = View.create_button(
                self, "Cancel",
                lambda: self.show_start_frame(),
                frame=change_pin_frame
            )
            cancel_button.place(relx=0.6, rely=0.9, anchor="w")

            # todo: check PIN format, show error msg
            finish_button = View.create_button(
                self, "Change it",
                lambda: self.controller.change_card_pin(
                    current_pin_entry.get(), new_pin_entry.get(), confirm_new_pin_entry.get()
                ),
                frame=change_pin_frame
            )
            finish_button.place(relx=0.8, rely=0.9, anchor="w")
            self.bind('<Return>', lambda event: self.controller.change_card_pin(
                current_pin_entry.get(),
                new_pin_entry.get(),
                confirm_new_pin_entry.get())
            )

            return change_pin_frame

        except Exception as e:
            logger.error(f"An unexpected error occurred in change_pin: {e}", exc_info=True)

    def show_edit_label_frame(self):
        if self.edit_label_frame is None:
            self.edit_label_frame = FrameCardEditLabel(self)  #self.create_edit_label_frame()
        self.edit_label_frame.tkraise()

    def create_edit_label_frame(self): #todo remove
        try:
            logger.info("View.create_edit_label_frame() start")

            # Creating new frame
            edit_label_frame = View.create_frame(self, width=750, height=600, frame=self.main_frame)
            edit_label_frame.place(relx=1.0, rely=0.5, anchor="e")

            # Creating main menu # todo?
            #self.show_settings_menu()

            # Creating header
            header = View.create_an_header(
                self,
                "Edit Label",
                "edit_label_popup.jpg",
                frame=edit_label_frame
            )
            header.place(relx=0.05, rely=0.05, anchor="nw")

            # setup paragraph
            text = View.create_label(
                self,
                f"Edit the label of your {self.controller.cc.card_type}.",
                frame=edit_label_frame
            )
            text.place(relx=0.05, rely=0.17, anchor="w")
            text = View.create_label(
                self,
                "The label is a tag that identifies your card. It can be used to distinguish ",
                frame=edit_label_frame
            )
            text.place(relx=0.05, rely=0.22, anchor="w")
            text = View.create_label(
                self,
                "several cards, or to associate it with a person, a name or a story.",
                frame=edit_label_frame
            )
            text.place(relx=0.05, rely=0.27, anchor="w")

            # Setting up label entry fields
            edit_card_label = View.create_label(self, "Label :", frame=edit_label_frame)
            edit_card_label.place(relx=0.05, rely=0.4, anchor="w")
            edit_card_entry = View.create_entry(self, frame=edit_label_frame)
            self.after(100, edit_card_entry.focus_force)
            edit_card_entry.place(relx=0.05, rely=0.45, anchor="w")

            # Creating cancel and finish buttons
            cancel_button = View.create_button(
                self, "Cancel",
                lambda: self.show_start_frame(),
                frame=edit_label_frame
            )
            cancel_button.place(relx=0.6, rely=0.9, anchor="w")

            finish_button = View.create_button(
                self, "Change it",
                lambda: self.controller.edit_label(edit_card_entry.get()),
                frame=edit_label_frame
            )
            finish_button.place(relx=0.8, rely=0.9, anchor="w")
            self.bind('<Return>', lambda event: self.controller.edit_label(edit_card_entry.get()))

            return edit_label_frame

        except Exception as e:
            logger.error(f"An unexpected error occurred in edit_label: {e}", exc_info=True)

    def show_check_authenticity_frame(self):
        # verify PIN
        self.update_verify_pin()

        if self.authenticity_frame is None:
            self.authenticity_frame = FrameCardAuthenticity(self)
            #self.authenticity_frame = self.create_check_authenticity_frame()
        self.authenticity_frame.place()
        self.authenticity_frame.tkraise()

    def create_check_authenticity_frame(self): #todo remove deprecated
        if self.controller.cc.card_present: #todo move in show...
            logger.info("Card detected: checking authenticity")
            is_authentic, txt_ca, txt_subca, txt_device, txt_error = self.controller.cc.card_verify_authenticity()
            if txt_error != "":
                txt_device = txt_error + "\n------------------\n" + txt_device

        try:
            logger.info("View.check_authenticity start")

            # Creating new frame
            authenticity_frame = View.create_frame(self, width=750, height=600, frame=self.main_frame)
            authenticity_frame.place(relx=1.0, rely=0.5, anchor="e")

            header = self.create_an_header(
                "Check authenticity",
                "check_authenticity_popup.jpg",
                frame=authenticity_frame
            )
            header.place(relx=0.05, rely=0.05, anchor="nw")

            certificate_radio_value = customtkinter.StringVar(value="")

            def update_radio_selection():
                logger.info(f"Button clicked: {certificate_radio_value.get()}")
                if certificate_radio_value.get() == 'root_ca_certificate':
                    self.update_textbox(text_box, txt_ca)
                    text_box.place(relx=0.05, rely=0.4, anchor="nw")
                if certificate_radio_value.get() == 'sub_ca_certificate':
                    self.update_textbox(text_box, txt_subca)
                    text_box.place(relx=0.05, rely=0.4, anchor="nw")
                if certificate_radio_value.get() == 'device_certificate':
                    self.update_textbox(text_box, txt_device)
                    text_box.place(relx=0.05, rely=0.4, anchor="nw")

            #
            text = self.create_label(
                f"Check whether or not you have a genuine Satochip card.",
                frame=authenticity_frame
            )
            text.place(relx=0.05, rely=0.17, anchor="w")

            text = self.create_label(
                f"Status:",
                frame=authenticity_frame
            )
            text.configure(font=self.make_text_bold())
            text.place(relx=0.05, rely=0.27, anchor="w")
            if self.controller.cc.card_present:
                if is_authentic:
                    icon_image = Image.open("./pictures_db/genuine_card.jpg")
                    icon = customtkinter.CTkImage(light_image=icon_image, size=(30, 30))
                    icon_label = customtkinter.CTkLabel(
                        authenticity_frame, image=icon,
                        text=f"Your card is authentic. ",
                        compound='right', bg_color="whitesmoke", fg_color="whitesmoke",
                        font=customtkinter.CTkFont(family="Outfit", size=18, weight="normal"),
                        frame=authenticity_frame
                    )
                    icon_label.place(relx=0.2, rely=0.267, anchor="w")
                else:
                    icon_image = Image.open("./pictures_db/not_genuine_card.jpg")
                    icon = customtkinter.CTkImage(light_image=icon_image, size=(30, 30))
                    icon_label = customtkinter.CTkLabel( # todo: use create_label?
                        authenticity_frame, image=icon,
                        text=f"Your card is not authentic. ",
                        compound='right', bg_color="whitesmoke", fg_color="whitesmoke",
                        font=customtkinter.CTkFont(family="Outfit", size=18, weight="normal"),
                    )
                    icon_label.place(relx=0.2, rely=0.267, anchor="w")

                    text = View.create_label(self, f"Warning!", frame=authenticity_frame)
                    text.configure(font=self.make_text_bold())
                    text.place(relx=0.05, rely=0.7, anchor="w")
                    text = View.create_label(
                        self, f"We could not authenticate the issuer of this card.",
                        frame=authenticity_frame
                    )
                    text.place(relx=0.05, rely=0.75, anchor="w")
                    text = View.create_label(
                        self,
                        f"If you did not load the card applet by yourself, be extremely careful!",
                        frame=authenticity_frame
                    )
                    text.place(relx=0.05, rely=0.8, anchor="w")
                    text = View.create_label(
                        self,
                        f"Contact support@satochip.io to report any suspicious device.",
                        frame= authenticity_frame
                    )
                    text.place(relx=0.05, rely=0.85, anchor="w")

            # Setting up radio buttons
            root_ca_certificate = customtkinter.CTkRadioButton(
                authenticity_frame,
                text="Root CA certificate",
                variable=certificate_radio_value,
                value="root_ca_certificate",
                font=customtkinter.CTkFont(family="Outfit", size=14, weight="normal"),
                bg_color="whitesmoke", fg_color="green", hover_color="green",
                command=update_radio_selection
            )
            root_ca_certificate.place(relx=0.05, rely=0.35, anchor="w")

            sub_ca_certificate = customtkinter.CTkRadioButton(
                authenticity_frame,
                text="Sub CA certificate",
                variable=certificate_radio_value,
                value="sub_ca_certificate",
                font=customtkinter.CTkFont(family="Outfit", size=14, weight="normal"),
                bg_color="whitesmoke", fg_color="green", hover_color="green",
                command=update_radio_selection
            )
            sub_ca_certificate.place(relx=0.33, rely=0.35, anchor="w")

            device_certificate = customtkinter.CTkRadioButton(
                authenticity_frame,
                text="Device certificate",
                variable=certificate_radio_value,
                value="device_certificate",
                font=customtkinter.CTkFont(family="Outfit", size=14, weight="normal"),
                bg_color="whitesmoke", fg_color="green", hover_color="green",
                command=update_radio_selection
            )
            device_certificate.place(relx=0.56, rely=0.35, anchor="w")

            # Setting up text box
            text_box = customtkinter.CTkTextbox(
                authenticity_frame, corner_radius=10,
                bg_color='whitesmoke', fg_color=BUTTON_COLOR, border_color=BUTTON_COLOR,
                border_width=0, width=581, text_color="grey",
                height=228 if is_authentic else 150,
                font=customtkinter.CTkFont(family="Outfit", size=13, weight="normal")
            )

            cancel_button = View.create_button(
                self, "Back", lambda: self.show_start_frame(), frame=authenticity_frame)
            cancel_button.place(relx=0.8, rely=0.9, anchor="w")
            # if self.controller.cc.card_type != "Satodime":
            #     try:
            #         self.controller.cc.card_verify_PIN_simple()
            #     except Exception as e:
            #         self.show_start_frame()

            # Creating and placing main menu
            #self.show_settings_menu()

            return authenticity_frame

        except Exception as e:
            logger.error(f"An unexpected error occurred in check_authenticity: {e}", exc_info=True)

    def click_reset_button(self): # todo implement reset factory v1 & v2
        try:
            logger.info("click_reset_button attempting to reset the card.")

            (response, sw1, sw2) = self.controller.cc.card_reset_factory_signal()
            logger.info(f"card_reset_factory response: {hex(256 * sw1 + sw2)}")
            if sw1 == 0xFF and sw2 == 0x00:
                logger.info("Factory reset successful. Disconnecting the card.")
                self.controller.cc.set_mode_factory_reset(False)
                self.controller.cc.card_disconnect()
                msg = 'The card has been reset to factory\nRemaining counter: 0'
                self.show('SUCCESS', msg, "Ok", lambda: self.restart_app(),
                          "./pictures_db/reset_popup.jpg")
                logger.info("Card has been reset to factory. Counter set to 0.")
            elif sw1 == 0xFF and sw2 == 0xFF:
                logger.info("Factory reset aborted. The card must be removed after each reset.")
                msg = 'RESET ABORTED!\n Remaining counter: MAX.'
                self.show('ABORTED', msg, "Ok",
                          lambda: [self.controller.cc.set_mode_factory_reset(False), self.show_start_frame()],
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
            logger.error(f"An unexpected error occurred during the factory reset process: {e}", exc_info=True)

    def show_factory_reset_frame(self):
        if self.factory_reset_frame is None:
            self.factory_reset_frame = self.create_factory_reset_frame()
        else:
            self.factory_reset_frame.place()
            self.factory_reset_frame.tkraise()

    def create_factory_reset_frame(self):

        self.controller.cc.set_mode_factory_reset(True)

        try:

            # Creating new frame for reset card window
            factory_reset_frame = View.create_frame(self, width=750, height=600, frame=self.main_frame)
            factory_reset_frame.place(relx=1.0, rely=0.5, anchor="e")

            # Load background photo
            background_photo = View.create_background_photo("./pictures_db/reset_my_card.png")
            canvas = View.create_canvas(self, frame=factory_reset_frame)
            canvas.place(relx=0.0, rely=0.5, anchor="w")
            canvas.create_image(0, 0, image=self.background_photo, anchor="nw")

            # Creating header
            header = View.create_an_header(
                self,
                f"Reset Your {self.controller.cc.card_type}",
                "reset_popup.jpg",
                frame=factory_reset_frame
            )
            header.place(relx=0.05, rely=0.05, anchor="nw")

            # setup paragraph
            text = View.create_label(
                self,
                f"Resetting your card to factory settings removes all private keys, saved ",
                frame=factory_reset_frame
            )
            text.place(relx=0.05, rely=0.17, anchor="w")
            text = View.create_label(
                self,
                "information, and settings (PIN code) from your device.",
                frame=factory_reset_frame
            )
            text.place(relx=0.05, rely=0.22, anchor="w")

            text = View.create_label(
                self,
                "Before your start: be sure to have a backup of its content; either the",
                frame=factory_reset_frame
            )
            text.place(relx=0.05, rely=0.32, anchor="w")
            text = View.create_label(
                self,
                f"seedphrase or any other passwords stored in it.",
                frame=factory_reset_frame
            )
            text.place(relx=0.05, rely=0.37, anchor="w")

            text = View.create_label(
                self,
                "The reset process is simple: click on “Reset”, follow the pop-up wizard and",
                frame=factory_reset_frame
            )
            text.place(relx=0.05, rely=0.47, anchor="w")
            text = View.create_label(
                self,
                "remove your card from the chip card reader, insert it again. And do that",
                frame=factory_reset_frame
            )
            text.place(relx=0.05, rely=0.52, anchor="w")
            text = View.create_label(
                self,
                "several times.",
                frame=factory_reset_frame
            )
            text.place(relx=0.05, rely=0.57, anchor="w")

            # Creating counter label
            # self.counter_label = customtkinter.CTkLabel(
            #     factory_reset_frame,
            #     text="Card isn't reset actually",
            #     bg_color='white', fg_color='white',
            #     font=customtkinter.CTkFont(family="Outfit", size=30, weight="bold")
            # )
            # self.counter_label.place(relx=0.25, rely=0.53, anchor='w')

            # Creating quit & start button
            def click_cancel_button():
                logger.info("Executing quit button action")
                self.controller.cc.set_mode_factory_reset(False)
                time.sleep(0.5)  # todo remove?
                self.show_start_frame()

            def click_start_button():
                self.show(
                    'IN PROGRESS',
                    f"Please follow the instruction bellow.",
                    "Remove card",
                    lambda: self.click_reset_button(),
                    "./pictures_db/reset_popup.jpg"
                )
                self.show_button.configure(state='disabled')

            cancel_button = View.create_button(
                self,
                'Cancel',
                lambda: click_cancel_button(),
                frame=factory_reset_frame
            )
            cancel_button.place(relx=0.6, rely=0.9, anchor="w")

            reset_button = View.create_button(
                self,
                'Start',
                lambda: click_start_button(),
                frame=factory_reset_frame
            )
            reset_button.place(relx=0.8, rely=0.9, anchor="w")

            #self.show_settings_menu()

            return factory_reset_frame

        except Exception as e:
            logger.error(f"An unexpected error occurred in reset_my_card_window: {e}", exc_info=True)

    def reset_my_card_window(self): # todo remove
        self.controller.cc.set_mode_factory_reset(True)

        try:
            if self.current_frame is not None:
                self.clear_current_frame()

            # Creating new frame for reset card window
            self.current_frame = View.create_frame(self)
            self.current_frame.place(relx=0.5, rely=0.5, anchor="center")

            # Load background photo
            self.background_photo = View.create_background_photo("./pictures_db/reset_my_card.png")
            self.canvas = View.create_canvas(self)
            self.canvas.place(relx=0.250, rely=0.501, anchor="w")
            self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")

            # Creating header
            self.header = View.create_an_header(self, f"Reset Your {self.controller.cc.card_type}", "reset_popup.jpg")
            self.header.place(relx=0.32, rely=0.05, anchor="nw")

            # setup paragraph
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

            # Creating counter label
            self.counter_label = customtkinter.CTkLabel(
                self, text="Card isn't reset actually",
                bg_color='white', fg_color='white',
                font=customtkinter.CTkFont(family="Outfit", size=30, weight="bold")
            )
            # self.counter_label.place(relx=0.25, rely=0.53, anchor='w')

            # Creating quit & start button
            def click_cancel_button():
                logger.info("Executing quit button action")
                self.controller.cc.set_mode_factory_reset(False)
                time.sleep(0.5) # todo remove?
                self.show_start_frame()

            def click_start_button():
                msg = f"Please follow the instruction bellow."
                self.show('IN PROGRESS', msg, "Remove card", lambda: self.click_reset_button(),
                          "./pictures_db/reset_popup.jpg")
                self.show_button.configure(state='disabled')

            self.cancel_button = View.create_button(self, 'Cancel', lambda: click_cancel_button())
            self.cancel_button.place(relx=0.7, rely=0.9, anchor="w")
            self.reset_button = View.create_button(self,'Start',lambda: click_start_button())
            self.reset_button.place(relx=0.85, rely=0.9, anchor="w")

        except Exception as e:
            logger.error(f"An unexpected error occurred in reset_my_card_window: {e}", exc_info=True)

    def show_about_frame(self):
        logger.info("show_about_frame start")
        if self.about_frame is None:
            logger.info("show_about_frame self.about_frame is None")
            self.about_frame = FrameCardAbout(self)
        self.about_frame.update()
        self.about_frame.tkraise()

    def create_about_frame(self): #todo remove
        # TODO: add reset seed button (for satochip only)
        # TODO: implement nfc enable/disable (depending on card & version)
        # TODO: implement 2FA disable/enable (only satochip)

        try:
            logger.info("IN View.create_about_frame() start")

            # get card data
            response, sw1, sw2, card_status = self.controller.cc.card_get_status()

            # Creating new frame
            about_frame = View.create_frame(self, width=750, height=600, frame=self.main_frame)
            about_frame.place(relx=1, rely=0.5, anchor="e")

            # show settings menu on the left
            #self.show_settings_menu()

            self.background_photo = View.create_background_photo("./pictures_db/about_background.png")
            self.canvas = View.create_canvas(self, frame=about_frame)
            self.canvas.place(relx=0.0, rely=0.501, anchor="w")
            self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")

            def unlock():
                # if self.controller.cc.card_type != "Satodime":
                #     if self.controller.cc.is_pin_set():
                #         self.controller.cc.card_verify_PIN_simple()
                #     else:
                #         try:
                #             self.controller.PIN_dialog(f'Unlock your {self.controller.cc.card_type}')
                #         except Exception as e:
                #             self.show_start_frame()
                self.update_verify_pin()
                self.update_status()
                self.show_about_frame()

            # Creating header
            header = View.create_an_header(
                self, "About", "about_popup.jpg", frame=about_frame
            )
            header.place(relx=0.05, rely=0.05, anchor="nw")

            # card infos
            card_information = self.create_label("Card information", frame=about_frame)
            card_information.place(relx=0.05, rely=0.25, anchor="w")
            card_information.configure(font=self.make_text_bold())

            applet_version = self.create_label(
                f"Applet version: {self.controller.card_status['applet_full_version_string']}",
                frame=about_frame
            )
            if self.controller.cc.card_type == "Satodime" or self.controller.cc.is_pin_set():
                if self.controller.cc.card_type != "Satodime":
                    self.controller.cc.card_verify_PIN_simple()
                card_label_named = self.create_label(
                    f"Label: [{self.controller.get_card_label_infos()}]",
                    frame=about_frame
                )
                is_authentic, txt_ca, txt_subca, txt_device, txt_error = self.controller.cc.card_verify_authenticity()
                card_genuine = self.create_label(
                    f"Genuine: YES" if is_authentic else "Genuine: NO",
                    frame=about_frame
                )
            elif not self.controller.cc.setup_done:
                watch_all = self.create_label("Card requires setup", frame=about_frame)
                watch_all.place(relx=0.05, rely=0.17)
                unlock_button = self.create_button(
                    "Setup card",
                    lambda: self.show_setup_card_frame(),
                    frame=about_frame
                )
                unlock_button.configure(font=self.make_text_size_at(15))
                unlock_button.place(relx= 0.55, rely=0.17)
                card_label_named = self.create_label(f"Label: [UNKNOWN]", frame=about_frame)
                card_genuine = self.create_label(f"Genuine: [UNKNOWN]", frame=about_frame)
            else:
                watch_all = self.create_label("PIN required to look at complete information", frame=about_frame)
                watch_all.place(relx=0.05, rely=0.17)
                unlock_button = self.create_button("Unlock", lambda: [unlock()], frame=about_frame)
                unlock_button.configure(font=self.make_text_size_at(15))
                unlock_button.place(relx=0.66, rely=0.17)
                card_label_named = self.create_label(f"Label: [UNKNOWN]", frame=about_frame)
                card_genuine = self.create_label(f"Genuine: [UNKNOWN]", frame=about_frame)

            card_label_named.place(relx=0.05, rely=0.28)
            applet_version.place(relx=0.05, rely=0.33)
            card_genuine.place(relx=0.05, rely=0.38)

            # card configuration
            card_configuration = self.create_label("Card configuration", frame=about_frame)
            card_configuration.place(relx=0.05, rely=0.48, anchor="w")
            card_configuration.configure(font=self.make_text_bold())
            if self.controller.cc.card_type != "Satodime":
                pin_information = self.create_label(
                    f"PIN counter:[{self.controller.card_status['PIN0_remaining_tries']}] tries remaining",
                    frame = about_frame
                )
                pin_information.place(relx=0.05, rely=0.52)
            else:
                pin_information = self.create_label("No PIN required", frame=about_frame)
                pin_information.place(relx=0.05, rely=0.52)

            # for a next implementation of 2FA functionality you have the code below
            if self.controller.cc.card_type == "Satochip":
                two_FA = self.create_label(
                    f"2FA enabled" if self.controller.cc.needs_2FA else f"2FA disabled",
                    frame = about_frame
                )
                two_FA.place(relx=0.05, rely=0.58)
                # if self.controller.cc.needs_2FA:
                #     self.button_2FA = self.create_button("Disable 2FA", None)
                # else:
                #     self.button_2FA = self.create_button("Enable 2FA")
                # self.button_2FA.configure(font=self.make_text_size_at(15), state='disabled')
                # self.button_2FA.place(relx=0.5, rely=0.58)

            # card connectivity
            card_connectivity = self.create_label("Card connectivity", frame=about_frame)
            card_connectivity.place(relx=0.05, rely=0.68, anchor="w")
            card_connectivity.configure(font=self.make_text_bold())

            if self.controller.cc.nfc_policy == 0:
                nfc = self.create_label(f"NFC enabled", frame=about_frame)
                #self.button_nfc = self.create_button("Disable NFC")
            elif self.controller.cc.nfc_policy == 1:
                nfc = self.create_label(f"NFC disabled:", frame=about_frame)
                #self.button_nfc = self.create_button("Enable NFC")
            else:
                nfc = self.create_label(f"NFC: [BLOCKED]", frame=about_frame)
            nfc.place(relx=0.05, rely=0.715)
            #self.button_nfc.configure(font=self.make_text_size_at(15), state='disabled')
            #self.button_nfc.place(relx=0.5, rely=0.71)

            # software information
            software_information = self.create_label("Software information", frame=about_frame)
            software_information.place(relx=0.05, rely=0.81, anchor="w")
            software_information.configure(font=self.make_text_bold())
            app_version = self.create_label(f"Satochip-utils version: {VERSION}", frame=about_frame)
            app_version.place(relx=0.05, rely=0.83)
            pysatochip_version = self.create_label(f"Pysatochip version: {PYSATOCHIP_VERSION}", frame=about_frame)
            pysatochip_version.place(relx=0.05, rely=0.88)
            back_button = View.create_button(
                self,
                'Back',
                lambda: self.show_start_frame(),
                frame = about_frame
            )
            back_button.place(relx=0.8, rely=0.9, anchor="w")

            return about_frame
        except Exception as e:
            logger.error(f"An error occurred while creating header: {e}", exc_info=True)

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
    @log_method
    def show_view_my_secrets(self):
        try:
            logger.debug("show_view_my_secrets start")
            self.in_backup_process = False
            self.welcome_in_display = False
            self._clear_welcome_frame()
            self._clear_current_frame()

            # verify PIN
            self.update_verify_pin()
            # if self.controller.cc.is_pin_set():
            #     self.controller.cc.card_verify_PIN_simple()
            # else:
            #     self.controller.PIN_dialog(f'Unlock your {self.controller.cc.card_type}')

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

    ##########################
    '''SEEDKEEPER OPTIONS'''

    @log_method
    def view_my_secrets(
            self,
            secrets_data: Dict[str, Any]
    ):
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




