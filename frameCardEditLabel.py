import customtkinter
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameCardEditLabel(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameStart init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Creating header
            self.header = master.create_an_header(
                "Edit Label",
                "edit_label_popup.jpg",
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            # setup paragraph
            self.text1 = master.create_label(
                f"Edit the label of your {master.controller.cc.card_type}.",
                frame=self
            )
            self.text1.place(relx=0.05, rely=0.17, anchor="w")

            self.text2 = master.create_label(
                "The label is a tag that identifies your card. It can be used to distinguish ",
                frame=self
            )
            self.text2.place(relx=0.05, rely=0.22, anchor="w")

            self.text3 = master.create_label(
                "several cards, or to associate it with a person, a name or a story.",
                frame=self
            )
            self.text3.place(relx=0.05, rely=0.27, anchor="w")

            # Setting up label entry fields
            self.edit_card_label = master.create_label("Label :", frame=self)
            self.edit_card_label.place(relx=0.05, rely=0.4, anchor="w")
            self.edit_card_entry = master.create_entry(frame=self)
            self.after(100, self.edit_card_entry.focus_force)
            self.edit_card_entry.place(relx=0.05, rely=0.45, anchor="w")

            # Creating cancel and finish buttons
            self.cancel_button = master.create_button(
                "Cancel",
                lambda: master.show_start_frame(),
                frame=self
            )
            self.cancel_button.place(relx=0.6, rely=0.9, anchor="w")

            self.finish_button = master.create_button(
                "Change it",
                lambda: self.change_label(self.edit_card_entry.get()),
                frame=self
            )
            self.finish_button.place(relx=0.8, rely=0.9, anchor="w")
            self.bind(
                '<Return>',
                lambda: self.change_label(self.edit_card_entry.get())
            )

            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"An unexpected error occurred in FrameCardEditLabel init: {e}", exc_info=True)

    def change_label(self, new_label):
        self.master.update_verify_pin()
        self.master.controller.edit_label(new_label)