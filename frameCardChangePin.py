import customtkinter
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameCardChangePin(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameCardChangePin init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Creating header
            self.header = master.create_an_header(
                "Change PIN ",
                "change_pin_popup.jpg",
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            #setup paragraph
            self.text1 = master.create_label(
                "Change your personal PIN code. ",
                frame=self
            )
            self.text1.place(relx=0.05, rely=0.17, anchor="w")

            self.text2 = master.create_label(
                "A PIN code must be between 4 and 16 characters.",
                frame=self
            )
            self.text2.place(relx=0.05, rely=0.22, anchor="w")

            self.text3 = master.create_label(
                "You can use symbols, lower and upper cases, letters and numbers.",
                frame=self
            )
            self.text3.place(relx=0.05, rely=0.27, anchor="w")

            # Setting up PIN entry fields
            # input current PIN
            self.current_pin_label = master.create_label("Current PIN:", frame=self)
            self.current_pin_label.configure(font=master.make_text_size_at(18))
            self.current_pin_label.place(relx=0.05, rely=0.40, anchor="w")

            self.current_pin_entry = master.create_entry("*", frame=self)
            self.after(100, self.current_pin_entry.focus_force)
            self.current_pin_entry.place(relx=0.05, rely=0.45, anchor="w")

            # input new PIN
            self.new_pin_label = master.create_label("New PIN code:", frame=self)
            self.new_pin_label.configure(font=master.make_text_size_at(18))
            self.new_pin_label.place(relx=0.05, rely=0.55, anchor="w")

            self.new_pin_entry = master.create_entry("*", frame=self)
            self.new_pin_entry.place(relx=0.05, rely=0.60, anchor="w")

            # confirm new PIN
            self.confirm_new_pin_label = master.create_label("Repeat new PIN code:", frame=self)
            self.confirm_new_pin_label.configure(font=master.make_text_size_at(18))
            self.confirm_new_pin_label.place(relx=0.05, rely=0.70, anchor="w")
            self.confirm_new_pin_entry = master.create_entry("*", frame=self)
            self.confirm_new_pin_entry.place(relx=0.05, rely=0.75, anchor="w")

            # Creating cancel and finish buttons
            self.cancel_button = master.create_button(
                "Cancel",
                lambda: master.show_start_frame(),
                frame=self
            )
            self.cancel_button.place(relx=0.6, rely=0.9, anchor="w")

            # todo: check PIN format, show error msg
            self.finish_button = master.create_button(
                "Change PIN",
                lambda: master.controller.change_card_pin(
                    self.current_pin_entry.get(), self.new_pin_entry.get(), self.confirm_new_pin_entry.get()
                ),
                frame=self
            )
            self.finish_button.place(relx=0.8, rely=0.9, anchor="w")
            self.bind('<Return>', lambda event: master.controller.change_card_pin(
                self.current_pin_entry.get(),
                self.new_pin_entry.get(),
                self.confirm_new_pin_entry.get())
            )

            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"An unexpected error occurred in FrameCardChangePin init: {e}", exc_info=True)