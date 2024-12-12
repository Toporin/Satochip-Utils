import customtkinter
import logging
from PIL import Image, ImageTk

from constants import MAIN_MENU_COLOR, HOVER_COLOR

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FramePopup(customtkinter.CTkToplevel):
    def __init__(
            self,
            parent,
            title,
            msg: str,
            button_txt="Ok",
            cmd=None,
            icon_path=None,
            button2_txt=None,
            cmd2=None,
    ):
        super().__init__()

        self.title(title)
        self.configure(fg_color='whitesmoke')

        # closing the popup through the upper right 'x' does not execute command
        self.protocol("WM_DELETE_WINDOW", lambda: close_no_execute())

        # Calcul pour centrer le popup par rapport à la fenêtre principale
        popup_width = 600
        popup_height = 200
        position_right = int(parent.winfo_screenwidth() / 2 - popup_width / 2)
        position_down = int(parent.winfo_screenheight() / 2 - popup_height / 2)
        self.geometry(f"{popup_width}x{popup_height}+{position_right}+{position_down}")
        logger.debug("Popup window centered")

        # grip positioning
        self.grid_columnconfigure((0, 1), weight=1)

        # Ajouter une icône si icon_path est défini
        if icon_path:
            icon_image = Image.open(icon_path)
            icon = customtkinter.CTkImage(light_image=icon_image, size=(30, 30))
            icon_label = customtkinter.CTkLabel(
                self,
                image=icon,
                text=f"\n{msg}",
                compound='top',
                font=customtkinter.CTkFont(family="Outfit", size=18, weight="normal")
            )
            icon_label.grid(row=0, column=0, padx=20, pady=20, sticky="ew", columnspan=2)

        else:
            # Ajout d'un label dans le popup
            label = customtkinter.CTkLabel(
                self,
                text=msg,
                font=customtkinter.CTkFont(family="Outfit", size=14, weight="bold")
            )
            label.grid(row=0, column=0, padx=20, pady=20, sticky="ew", columnspan=2)
        logger.debug("Label added to popup")

        def close_and_execute():
            if cmd:
                self.destroy()
                cmd()
            else:
                self.destroy()

        def close_and_execute2():
            if cmd2:
                self.destroy()
                cmd2()
            else:
                self.destroy()

        def close_no_execute():
            self.destroy()

        if button2_txt:  # place 2 buttons

            self.show_button = customtkinter.CTkButton(
                self,
                text=button_txt,
                fg_color=MAIN_MENU_COLOR,
                hover_color=HOVER_COLOR,
                bg_color='whitesmoke',
                width=120, height=35, corner_radius=34,
                font=customtkinter.CTkFont(family="Outfit", size=18, weight="normal"),
                command=lambda: close_and_execute()
            )
            self.show_button.grid(row=1, column=0, padx=20, pady=20, sticky="ew")

            self.show_button2 = customtkinter.CTkButton(
                self,
                text=button2_txt,
                fg_color=MAIN_MENU_COLOR,
                hover_color=HOVER_COLOR,
                bg_color='whitesmoke',
                width=120, height=35, corner_radius=34,
                font=customtkinter.CTkFont(family="Outfit", size=18, weight="normal"),
                command=lambda: close_and_execute2()
            )
            self.show_button2.grid(row=1, column=1, padx=20, pady=20, sticky="ew")

        else:  # Place only 1 button
            self.show_button = customtkinter.CTkButton(
                self,
                text=button_txt,
                fg_color=MAIN_MENU_COLOR,
                hover_color=HOVER_COLOR,
                bg_color='whitesmoke',
                width=120, height=35, corner_radius=34,
                font=customtkinter.CTkFont(family="Outfit", size=18, weight="normal"),
                command=lambda: close_and_execute()
            )
            self.show_button.grid(row=1, column=0, padx=20, pady=20, columnspan=2)

        # Rendre la fenêtre modale
        # self.transient(self)  # Set to be on top of the main window
        self.wait_visibility()  # patch _tkinter.TclError: grab failed: window not viewable
        self.grab_set()  # Grab all events