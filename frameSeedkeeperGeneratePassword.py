import customtkinter
import logging
import secrets

from frameWidgetHeader import FrameWidgetHeader
from constants import BG_MAIN_MENU, BG_HOVER_BUTTON, BG_BUTTON

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameSeedkeeperGeneratePassword(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameSeedkeeperGeneratePassword init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Creating header
            self.header = FrameWidgetHeader(
                "Generate password", "password_popup.jpg",
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            # label
            self.label = master.create_label("Label*:", frame=self)
            self.label.place(relx=0.05, rely=0.20, anchor="nw")

            self.label_entry = master.create_entry(frame=self)
            self.label_entry.configure(width=400)
            self.label_entry.configure(placeholder_text="Enter label")
            self.label_entry.place(relx=0.15, rely=0.20, anchor="nw")

            # login field (opt)
            self.login_label = master.create_label("Login:", frame=self)
            self.login_label.place(relx=0.05, rely=0.32, anchor="nw")

            self.login_entry = master.create_entry(frame=self)
            self.login_entry.configure(width=400)
            self.login_entry.configure(placeholder_text="Enter login (optional)")
            self.login_entry.place(relx=0.15, rely=0.32, anchor="nw")

            # url field (opt)
            self.url_label = master.create_label("Url:", frame=self)
            self.url_label.place(relx=0.05, rely=0.44, anchor="nw")

            self.url_entry = master.create_entry(frame=self)
            self.url_entry.configure(width=400)
            self.url_entry.configure(placeholder_text="Enter url (optional)")
            self.url_entry.place(relx=0.15, rely=0.44, anchor="nw")

            # Slide bar creation

            def _length_slider_event(value):
                try:
                    int_value = int(value)
                    self.length_value_label.configure(text=f"{int_value}")
                    self.length_value_label.place(x=self.length_slider.get() * 3.5 + 250, y=324)

                    if int_value < 8:
                        self.length_slider.configure(button_color="red", progress_color="red")
                    elif int_value < 10:
                        self.length_slider.configure(button_color="orange", progress_color="orange")
                    elif int_value >= 10:
                        self.length_slider.configure(button_color="green", progress_color="green")
                except Exception as e:
                    logger.error(f"077 Error updating slider value: {e}", exc_info=True)

            self.length_slider = customtkinter.CTkSlider(
                self,
                from_=6, to=18,
                command=_length_slider_event,
                width=600,
                progress_color=BG_HOVER_BUTTON,
                button_color=BG_MAIN_MENU
            )
            self.length_slider.configure(button_color="green", progress_color="green")
            self.length_slider.set(12)  # use secure value by default
            self.length_slider.place(relx=0.15, rely=0.55)

            self.length = master.create_label("Length*: ", frame=self)
            self.length.place(relx=0.04, rely=0.535)

            self.length_value_label = master.create_label("12", frame=self)
            self.length_value_label.configure(font=master.make_text_bold(20))
            self.length_value_label.place(x=285, y=324)

            # Checkbox creation
            self.characters_used = master.create_label("Characters used: ", frame=self)
            self.characters_used.place(relx=0.04, rely=0.6)

            self.var_abc = customtkinter.StringVar()
            self.var_ABC = customtkinter.StringVar()
            self.var_numeric = customtkinter.StringVar()
            self.var_symbolic = customtkinter.StringVar()

            def checkbox_event():
                selected_values = [self.var_abc.get(), self.var_ABC.get(), self.var_numeric.get(),
                                   self.var_symbolic.get()]
                logger.debug(
                    f"Checkbox selection updated: {', '.join(filter(None, selected_values))}")

            self.minus_abc = customtkinter.CTkCheckBox(
                self, text="abc",
                variable=self.var_abc,
                onvalue="abc", offvalue="",
                command=checkbox_event,
                checkmark_color=BG_MAIN_MENU,
                fg_color=BG_HOVER_BUTTON)
            self.minus_abc.select()  # selected by default
            self.minus_abc.place(relx=0.3, rely=0.6)

            self.major_abc = customtkinter.CTkCheckBox(
                self, text="ABC", variable=self.var_ABC,
                onvalue="ABC", offvalue="", command=checkbox_event,
                checkmark_color=BG_MAIN_MENU,
                fg_color=BG_HOVER_BUTTON
            )
            self.major_abc.select()  # selected by default
            self.major_abc.place(relx=0.4, rely=0.6)

            self.numeric_value = customtkinter.CTkCheckBox(
                self,
                text="123",
                variable=self.var_numeric,
                onvalue="123", offvalue="",
                command=checkbox_event,
                checkmark_color=BG_MAIN_MENU,
                fg_color=BG_HOVER_BUTTON
            )
            self.numeric_value.select()  # selected by default
            self.numeric_value.place(relx=0.5, rely=0.6)

            self.symbolic_value = customtkinter.CTkCheckBox(
                self,
                text="#$&",
                variable=self.var_symbolic,
                onvalue="#$&", offvalue="",
                command=checkbox_event,
                checkmark_color=BG_MAIN_MENU,
                fg_color=BG_HOVER_BUTTON)
            self.symbolic_value.select()  # selected by default
            self.symbolic_value.place(relx=0.6, rely=0.6)

            # password generation
            self.password_label = master.create_label("Generated password:", frame=self)
            self.password_label.place(relx=0.04, rely=0.67, anchor="nw")

            self.password_textbox = customtkinter.CTkTextbox(
                self, corner_radius=20, bg_color="whitesmoke", fg_color=BG_BUTTON,
                border_color=BG_BUTTON, border_width=1, width=500, height=83,
                text_color="grey",
                font=customtkinter.CTkFont(family="Outfit", size=13, weight="normal")
            )
            # self.password_textbox.configure(state='disabled') # does not allow copy-paste on some linux distro
            self.password_textbox.tag_config("tag_centered", justify="center")  # for text justification
            self.password_textbox.configure(width=400)
            self.password_textbox.place(relx=0.15, rely=0.8, anchor="w")

            # action buttons
            # password generation
            def generate_password():
                try:
                    # retrieving the length selected by user
                    password_length = int(self.length_slider.get())
                    logger.debug(password_length)

                    # retrieving characters selected in checkbox
                    char_pool = ""
                    if self.var_abc.get():
                        char_pool += "abcdefghijklmnopqrstuvwxyz"
                    if self.var_ABC.get():
                        char_pool += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    if self.var_numeric.get():
                        char_pool += "0123456789"
                    if self.var_symbolic.get():
                        char_pool += "!@#$%^&*()-_=+[]{}|;:,.<>?/~"

                    if not char_pool:
                        logger.warning("No character sets selected for password generation")
                        raise ValueError(
                            "No character set selected.\nPlease select at least one character set.")

                    # password generation
                    generated_password = ''.join(secrets.choice(char_pool) for _ in range(password_length))

                    # displaying password into text box
                    self.password_textbox.configure(state='normal')
                    self.password_textbox.delete("1.0", customtkinter.END)
                    self.password_textbox.insert("1.0", generated_password, "tag_centered")
                    # self.password_textbox.configure(state='disabled')  # does not allow copy-paste on some linux distro
                except ValueError as e:
                    logger.error(f"Error generating login/password: {e}", exc_info=True)
                    master.show("ERROR", str(e), "Ok", None, "./pictures_db/generate_popup.png")
                except Exception as e:
                    logger.error(f"Error generating login/password: {e}", exc_info=True)

            self.generate_password_button = master.create_button(
                "Generate",
                command=generate_password,
                frame=self
            )
            self.generate_password_button.place(relx=0.75, rely=0.8, anchor="w")

            # password import to card
            def _save_password_to_card():
                try:
                    logger.info("Saving login/password to card")
                    label = self.label_entry.get()
                    login = self.login_entry.get()
                    url = self.url_entry.get()
                    password = self.password_textbox.get("1.0", "end").strip()

                    # import
                    sid, fingerprint = master.controller.import_password(label, password, login, url)
                    master.show("SUCCESS",
                              f"Password saved successfully with id: {sid}",
                              "Ok", master.show_seedkeeper_list_secrets, "./pictures_db/generate_popup.png")

                except Exception as e:
                    logger.error(f"Failed to save password to card: {e}", exc_info=True)
                    master.show(
                        "Error",
                        f"Failed to import secret: {e}",
                        "Ok", None,
                        "./pictures_db/about_popup.jpg"  # todo change icon
                    )

            self.save_button = master.create_button(
                "Import to card",
                command=_save_password_to_card,
                frame=self
            )
            self.save_button.place(relx=0.85, rely=0.95, anchor="center")

            # back button
            self.back_button = master.create_button(
                "Back",
                command=master.show_generate_secret,
                frame=self
            )
            self.back_button.place(relx=0.65, rely=0.95, anchor="center")

            # place frame
            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"Init error : {e}", exc_info=True)
