import customtkinter
import logging

from constants import MAIN_MENU_COLOR

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameWelcome(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameWelcome init")

        # Creating new frame and background
        #welcome_frame = master.create_frame(width=1000, height=600, frame=master.main_frame)
        #welcome_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.configure(width=1000, height=600)
        #self.place(relx=0.5, rely=0.5, anchor="center")
        self.background_photo = master.create_background_photo("./pictures_db/welcome_in_satochip_utils.png")
        logger.debug(f"FrameWelcome background_photo {self.background_photo}")
        #canvas = master.create_canvas(frame=welcome_frame)
        self.canvas = customtkinter.CTkCanvas(self, bg="whitesmoke", width=1000, height=600)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center")
        self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")
        logger.debug(f"FrameWelcome canvas created")

        master.create_an_header_for_welcome(frame=self)

        # Setting up labels
        label1 = master.create_label(
            'Satochip-Utils\n______________',
            MAIN_MENU_COLOR,
            frame=self
        )
        label1.configure(text_color='white')
        label1.configure(font=master.make_text_size_at(18))
        label1.place(relx=0.05, rely=0.4, anchor="w")

        label2 = master.create_label(
            'Your one stop shop to manage your Satochip cards,',
            MAIN_MENU_COLOR,
            frame=self
        )
        label2.configure(text_color='white')
        label2.configure(font=master.make_text_size_at(18))
        label2.place(relx=0.05, rely=0.5, anchor="w")

        label3 = master.create_label('including Satodime and Seedkeeper.', MAIN_MENU_COLOR, frame=self)
        label3.configure(text_color='white')
        label3.configure(font=master.make_text_size_at(18))
        label3.place(relx=0.05, rely=0.55, anchor="w")

        label4 = master.create_label('Change your PIN code, reset your card, setup your', MAIN_MENU_COLOR,
                                   frame=self)
        label4.configure(text_color='white')
        label4.configure(font=master.make_text_size_at(18))
        label4.place(relx=0.05, rely=0.65, anchor="w")

        label5 = master.create_label('hardware wallet and many more...', MAIN_MENU_COLOR, frame=self)
        label5.configure(text_color='white')
        label5.configure(font=master.make_text_size_at(18))
        label5.place(relx=0.05, rely=0.7, anchor="w")

        # Creating and placing the button
        button = master.create_button(
            "Let's go!",
            command=lambda: [self.place_forget(), master.show_start_frame(), master.show_menu_frame()],
            frame=self
        )
        self.after(2500, button.place(relx=0.85, rely=0.93, anchor="center"))

        self.place(relx=0.5, rely=0.5, anchor="center")