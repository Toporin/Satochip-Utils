import gc
import logging
import sys
import os
import tkinter
from typing import Optional, Dict, Callable, Any, Tuple

import customtkinter
from PIL import Image, ImageTk
from customtkinter import CTkOptionMenu

from FrameSeedkeeperGenerateSecretSelectType import FrameSeedkeeperGenerateSecretSelectType
from applicationMode import ApplicationMode
from controller import Controller
from exceptions import ViewError, FrameClearingError, FrameCreationError
from frameCardAbout import FrameCardAbout
from frameCardAuthenticity import FrameCardAuthenticity
from frameCardChangePin import FrameCardChangePin
from frameCardEditLabel import FrameCardEditLabel
from frameCardFactoryReset import FrameCardFactoryReset
from frameCardImportSeed import FrameCardImportSeed
from frameCardSetupPin import FrameCardSetupPin
from frameMenuNoCard import FrameMenuNoCard
from frameMenuSeedkeeper import FrameMenuSeedkeeper
from frameMenuSeedkeeperBackup import FrameMenuSeedkeeperBackup
from frameMenuSettings import FrameMenuSettings
from frameSeedkeeperBackupCard import FrameSeedkeeperBackupCard
from frameSeedkeeperBackupResult import FrameSeedkeeperBackupResult
from frameSeedkeeperCardLogs import FrameSeedkeeperCardLogs
from frameSeedkeeperGenerateMnemonic import FrameSeedkeeperGenerateMnemonic
from frameSeedkeeperGeneratePassword import FrameSeedkeeperGeneratePassword
from frameSeedkeeperImportMnemonic import FrameSeedkeeperImportMnemonic
from frameSeedkeeperImportPassword import FrameSeedkeeperImportPassword
from frameSeedkeeperImportSecret import FrameSeedkeeperImportSecret
from frameSeedkeeperImportSimpleSecret import FrameSeedkeeperImportSimpleSecret
from frameSeedkeeperListSecrets import FrameSeedkeeperListSecrets
from frameSeedkeeperShowMnemonic import FrameSeedkeeperShowMnemonic
from frameSeedkeeperShowPassword import FrameSeedkeeperShowPasswordSecret
from frameSeedkeeperShowSimpleSecret import FrameSeedkeeperShowSecret
from frameStart import FrameStart
from frameWelcome import FrameWelcome
from log_config import SUCCESS, log_method

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

            # frame declaration
            # these frames will be created when needed using show_* methods
            self.welcome_frame = None
            self.start_frame = None
            # menu frames
            self.settings_menu_frame = None
            self.seedkeeper_menu_frame = None
            self.seedkeeper_backup_menu_frame = None
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
            self.seedkeeper_show_mnemonic_frame = None
            # self.seedkeeper_show_descriptor_frame = None
            # self.seedkeeper_show_data_frame = None
            # self.seedkeeper_show_masterseed_frame = None
            # self.seedkeeper_show_2fa_frame = None
            # self.seedkeeper_show_pubkey_frame = None
            self.seedkeeper_show_simple_secret_frame = None
            # seedkeeper generate secret
            self.seedkeeper_generate_secret_frame = None
            self.seedkeeper_generate_mnemonic_frame = None
            self.seedkeeper_generate_password_frame = None
            # seedkeeper import secret
            self.seedkeeper_import_secret_frame = None
            self.seedkeeper_import_mnemonic_frame = None
            self.seedkeeper_import_password_frame = None
            self.seedkeeper_import_descriptor_frame = None
            self.seedkeeper_import_data_frame = None
            # seedkeeper logs
            self.seedkeeper_card_logs_frame = None
            # seedkeeper backup card
            self.seedkeeper_backup_card_frame = None
            self.seedkeeper_backup_result_frame = None

            # state
            # store seedkeeper secret headers
            self.secret_headers = None
            # should we update the list of headers?
            self.seedkeeper_secret_headers_need_update = True
            # app is in seedbackup mode (inserting/removing card should not trigger start screen!)
            self.appMode = ApplicationMode.Normal

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

            # A bug related to copy-paste is patched in tcl/tk v8.6.11:
            # https://arbitrary-but-fixed.net/2021/11/21/tk-disabled-text-copy-paste.html
            logger.debug(f"Tcl/Tk version {self.tk.call('info', 'patchlevel')}")

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

    def convert_name_to_photo_image(self, filename):
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
            #scrollbar.configure(fg_color=DEFAULT_BG_COLOR, button_color=DEFAULT_BG_COLOR,
            #                    button_hover_color=BG_HOVER_BUTTON)
            scrollbar.configure(fg_color=DEFAULT_BG_COLOR, button_color=BG_HOVER_BUTTON,
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

    def create_entry(self, show_option: str = "", width=555, height=37, frame=None)-> customtkinter.CTkEntry:
        logger.debug("create_entry start")
        if frame is None:
            frame = self.current_frame # todo
        entry = customtkinter.CTkEntry(
            frame, width=width, height=height, corner_radius=10,
            bg_color='white', fg_color=BUTTON_COLOR, border_color=BUTTON_COLOR,
            show=show_option, text_color='grey'
        )
        return entry

    # def _create_entry(self, show_option: str = "")-> customtkinter.CTkEntry: # todo merge with create_entry
    #     logger.debug("create_entry start")
    #     entry = customtkinter.CTkEntry(
    #         self.current_frame, width=555, height=37, corner_radius=10,
    #         bg_color='white', fg_color=BUTTON_COLOR, border_color=BUTTON_COLOR,
    #         show=show_option, text_color='grey'
    #     )
    #     return entry

    def create_textbox(self, frame, width=555, height=37) -> customtkinter.CTkTextbox:
        # Créer la textbox avec les mêmes dimensions et styles que l'entrée
        textbox = customtkinter.CTkTextbox(
            frame,
            width=width, height=height, corner_radius=10,
            bg_color='white', fg_color=BG_BUTTON, border_color=BG_BUTTON,
            text_color='grey', wrap='word'
        )
        # Ajouter du padding pour centrer verticalement le texte
        #textbox.configure(pady=40)  # Ajustez le nombre pour mieux centrer
        return textbox

    def update_textbox(self, text_box, text):
        try:
            logger.debug("update_textbox start")
            # Efface le contenu actuel
            text_box.delete(1.0, "end")
            # Inserting new text into the textbox
            text_box.insert("end", text)
        except Exception as e:
            logger.error(f"An unexpected error occurred in update_textbox: {e}", exc_info=True)

    def create_option_list(
            self,
            frame,
            options,
            default_value: Optional[str] = None,
            width: int = 300,

    ) -> Tuple[tkinter.StringVar, CTkOptionMenu]:
        logger.info(f"Creating option list with options: {options}")
        variable = customtkinter.StringVar(value=default_value if default_value else options[0])
        option_menu = customtkinter.CTkOptionMenu(
            master=frame,
            variable=variable,
            values=options,
            width=width,
            fg_color=BG_BUTTON,  # Utilisez la même couleur que pour les entrées
            button_color=BG_BUTTON,  # Couleur du bouton déroulant
            button_hover_color=BG_HOVER_BUTTON,  # Couleur au survol du bouton
            dropdown_fg_color=BG_MAIN_MENU,  # Couleur de fond du menu déroulant
            dropdown_hover_color=BG_HOVER_BUTTON,  # Couleur au survol des options
            dropdown_text_color="white",  # Couleur du texte des options
            text_color="grey",  # Couleur du texte sélectionné
            font=customtkinter.CTkFont(family="Outfit", size=13, weight="normal"),
            dropdown_font=customtkinter.CTkFont(family="Outfit", size=13, weight="normal"),
            corner_radius=10,  # Même rayon de coin que les entrées
        )
        return variable, option_menu

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

            # closing the popup through the upper right 'x' does not execute command
            popup.protocol("WM_DELETE_WINDOW", lambda: close_no_execute())
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

            def close_and_execute():
                if cmd:
                    popup.destroy()
                    cmd()
                else:
                    popup.destroy()

            def close_no_execute():
                popup.destroy()

            # Ajout d'un bouton pour fermer le popup
            self.show_button = customtkinter.CTkButton(
                popup, text=button_txt, fg_color=MAIN_MENU_COLOR,
                hover_color=HOVER_COLOR, bg_color='whitesmoke',
                width=120, height=35, corner_radius=34,
                font=customtkinter.CTkFont(family="Outfit", size=18, weight="normal"),
                command=lambda: close_and_execute()
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
            if self.controller.cc.card_type == "SeedKeeper" and self.controller.cc.setup_done:
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

    def show_seedkeeper_menu(self, state=None, frame=None):
        logger.info("show_seedkeeper_menu start")
        if self.seedkeeper_menu_frame is None:
            self.seedkeeper_menu_frame = FrameMenuSeedkeeper(self)
        else:
            logger.info("show_seedkeeper_menu seedkeeper_menu_frame is not None, show it")
            #self.settings_menu_frame.place_forget()
            #self.seedkeeper_menu_frame.place()
            self.seedkeeper_menu_frame.tkraise()

    def show_seedkeeper_backup_menu(self):
        logger.info("show_seedkeeper_backup_menu start")
        if self.seedkeeper_backup_menu_frame is None:
            self.seedkeeper_backup_menu_frame = FrameMenuSeedkeeperBackup(self)
        self.seedkeeper_backup_menu_frame.tkraise()


    ################################
    """ UTILS FOR CARD CONNECTOR """

    def update_status(self, isConnected=None):
        try:
            if (self.appMode == ApplicationMode.FactoryResetV1 or
                    self.appMode == ApplicationMode.FactoryResetV2):
                # we are in factory reset mode
                if isConnected is True:
                    logger.info(f"Card inserted for Reset Factory!")
                    try:
                        self.show_button.configure(text='Click to reset', state='normal')
                    except Exception as e:
                        logger.error(f"An error occurred while updating labels and button for card insertion: {e}",
                                     exc_info=True)
                elif isConnected is False:
                    logger.info(f"Card removed for Reset Factory!")
                    try:
                        self.show_button.configure(text='Insert card', state='disabled')
                    except Exception as e:
                        logger.error(f"An error occurred while updating labels and button for card removal: {e}",
                                     exc_info=True)
                else:  # None
                    pass

            elif self.appMode == ApplicationMode.SeedkeeperBackup:
                logger.debug("View.update_status start (seedkeeper backup mode)")
                # nothing to do here

            else:
                # normal mode
                logger.info("View.update_status start (normal mode)")
                if isConnected is True:
                    try:
                        if self.start_frame is not None: # do not create frame now as it is not main thread
                            self.show_start_frame()
                    except Exception as e:
                        logger.error(f"An error occurred while getting card status: {e}", exc_info=True)

                elif isConnected is False:
                    try:
                        # update state
                        # Seedkeeper: reset secret_headers to force update on reconnection
                        self.secret_headers = None
                        self.seedkeeper_secret_headers_need_update = True

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
                self.controller.PIN_dialog(f'Enter the PIN of your {self.controller.cc.card_type}')

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
                popup, image=icon, text= msg,  # f"\nEnter the PIN code of your card.",
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

        # show menu
        self.show_menu_frame()

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

        # show reset menu on the left
        # This menu force the user to cancel if he wants to leave reset process
        # By cancelling, the app is notified to leave ApplicationMode.SeedkeeperBackup back to normal mode
        # todo we reuse show_seedkeeper_backup_menu() since functionalities are the same
        self.show_seedkeeper_backup_menu()


    def show_about_frame(self):
        logger.info("show_about_frame start")
        if self.about_frame is None:
            logger.info("show_about_frame self.about_frame is None")
            self.about_frame = FrameCardAbout(self)
        self.about_frame.update()
        self.about_frame.tkraise()

    ####################################################################################################################
    """ METHODS TO DISPLAY A VIEW FROM SEEDKEEPER MENU SELECTION """

    # SEEDKEEPER MENU SELECTION
    #@log_method
    def show_view_my_secrets(self):  #todo rename show_seedkeeper_list_secrets
        try:
            logger.debug("show_view_my_secrets start")

            if self.secret_headers is None:
                # verify PIN
                self.update_verify_pin()
                # get list of secret headers
                self.secret_headers = self.controller.retrieve_secrets_stored_into_the_card()
                self.seedkeeper_secret_headers_need_update = True
                logger.debug(f"Fetched {len(self.secret_headers)} headers from card")

            if self.list_secrets_frame is None:
                self.list_secrets_frame = FrameSeedkeeperListSecrets(self)
            if self.seedkeeper_secret_headers_need_update is True:
                self.list_secrets_frame.update(self.secret_headers)
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
            self.show_password_secret(secret_details)
        elif secret_header['type'] == 'Masterseed':
            if secret_details['subtype'] > 0 or secret_details['subtype'] == '0x1':
                self.show_mnemonic_secret(secret_details)
            else:
                self.show_simple_secret(secret_details)
        elif secret_header['type'] == "BIP39 mnemonic":
            self.show_mnemonic_secret(secret_details)
        elif secret_header['type'] == 'Electrum mnemonic':
            self.show_mnemonic_secret(secret_details)
        elif (secret_header['type'] == 'Wallet descriptor' or
              secret_header['type'] == 'Free text' or
              secret_header['type'] == '2FA secret' or
              secret_header['type'] == 'Public Key'
        ):
            self.show_simple_secret(secret_details)
        else:
            # default for unsupported type is to show raw secret in hex
            self.show_simple_secret(secret_details)

    def show_password_secret(self, secret):
        if self.seedkeeper_show_password_frame is None:
            self.seedkeeper_show_password_frame = FrameSeedkeeperShowPasswordSecret(self)
        self.seedkeeper_show_password_frame.update(secret)
        self.seedkeeper_show_password_frame.tkraise()

    def show_mnemonic_secret(self, secret):
        if self.seedkeeper_show_mnemonic_frame is None:
            self.seedkeeper_show_mnemonic_frame = FrameSeedkeeperShowMnemonic(self)
        self.seedkeeper_show_mnemonic_frame.update_frame(secret)
        self.seedkeeper_show_mnemonic_frame.tkraise()

    def show_simple_secret(self, secret):
        if self.seedkeeper_show_simple_secret_frame is None:
            self.seedkeeper_show_simple_secret_frame = FrameSeedkeeperShowSecret(self)
        self.seedkeeper_show_simple_secret_frame.update(secret)
        self.seedkeeper_show_simple_secret_frame.tkraise()

    """ Generate Secret"""

    def show_generate_secret(self):
        if self.seedkeeper_generate_secret_frame is None:
            self.seedkeeper_generate_secret_frame = FrameSeedkeeperGenerateSecretSelectType(self)
        self.seedkeeper_generate_secret_frame.tkraise()

    def show_generate_mnemonic(self):
        if self.seedkeeper_generate_mnemonic_frame is None:
            self.seedkeeper_generate_mnemonic_frame = FrameSeedkeeperGenerateMnemonic(self)
        self.seedkeeper_generate_mnemonic_frame.tkraise()

    def show_generate_password(self):
        if self.seedkeeper_generate_password_frame is None:
            self.seedkeeper_generate_password_frame = FrameSeedkeeperGeneratePassword(self)
        self.seedkeeper_generate_password_frame.tkraise()

    """ Import Secret"""

    def show_import_secret(self):
        if self.seedkeeper_import_secret_frame is None:
            self.seedkeeper_import_secret_frame = FrameSeedkeeperImportSecret(self)
        self.seedkeeper_import_secret_frame.tkraise()

    def show_import_mnemonic(self):
        if self.seedkeeper_import_mnemonic_frame is None:
            self.seedkeeper_import_mnemonic_frame = FrameSeedkeeperImportMnemonic(self)
        self.seedkeeper_import_mnemonic_frame.tkraise()

    def show_import_password(self):
        if self.seedkeeper_import_password_frame is None:
            self.seedkeeper_import_password_frame = FrameSeedkeeperImportPassword(self)
        self.seedkeeper_import_password_frame.tkraise()

    def show_import_descriptor(self):
        if self.seedkeeper_import_descriptor_frame is None:
            self.seedkeeper_import_descriptor_frame = FrameSeedkeeperImportSimpleSecret(self, "descriptor")
        self.seedkeeper_import_descriptor_frame.tkraise()

    def show_import_data(self):
        if self.seedkeeper_import_data_frame is None:
            self.seedkeeper_import_data_frame = FrameSeedkeeperImportSimpleSecret(self, "data")
        self.seedkeeper_import_data_frame.tkraise()

    """ BACKUP CARD"""

    def show_backup_card(self):
        # set application mode to seedkeeper backup (avoid interruption on card insertion/removal)
        self.appMode = ApplicationMode.SeedkeeperBackup
        if self.seedkeeper_backup_card_frame is None:
            self.seedkeeper_backup_card_frame = FrameSeedkeeperBackupCard(self)
        self.seedkeeper_backup_card_frame.backup_start()
        self.seedkeeper_backup_card_frame.tkraise()

        # show backup menu on the left
        # This menu force the user to cancel if he wants to leave backup process
        # By cancelling, the app is notified to leave ApplicationMode.SeedkeeperBackup back to normal mode
        self.show_seedkeeper_backup_menu()

    def show_backup_result(self, is_backup_error, backup_logs):
        if self.seedkeeper_backup_result_frame is None:
            self.seedkeeper_backup_result_frame = FrameSeedkeeperBackupResult(self)
        self.seedkeeper_backup_result_frame.update_frame(is_backup_error, backup_logs)
        self.seedkeeper_backup_result_frame.tkraise()

    """ CARD LOGS"""

    def show_card_logs(self):

        # verify PIN
        self.update_verify_pin()
        # get logs from card
        total_number_of_logs, total_number_available_logs, logs = self.controller.get_card_logs()

        if self.seedkeeper_card_logs_frame is None:
            self.seedkeeper_card_logs_frame = FrameSeedkeeperCardLogs(self)
        self.seedkeeper_card_logs_frame.update_frame(logs)
        self.seedkeeper_card_logs_frame.tkraise()


