import customtkinter
import logging

from frameWidgetHeader import FrameWidgetHeader

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FrameSeedkeeperImportSecret(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        logger.debug("FrameSeedkeeperImportSecret init")

        try:
            # Creating new frame
            self.configure(
                width=750, height=600,
                bg_color="whitesmoke", fg_color="whitesmoke"
            )

            # Creating header
            self.header = FrameWidgetHeader(
                "Import secret", "import_popup.png",
                frame=self
            )
            self.header.place(relx=0.05, rely=0.05, anchor="nw")

            info_text_line_01 = "Seedkeeper allows you to import various types of secret"
            self.label1 = master.create_label(info_text_line_01, frame=self)
            self.label1.place(relx=0.05, rely=0.22, anchor="w")

            info_text_line_02 = "into the card. Select the type of secret you want to import."
            self.label2 = master.create_label(info_text_line_02, frame=self)
            self.label2.place(relx=0.05, rely=0.27, anchor="w")

            self.type_label = master.create_label("Type of secret:", frame=self)
            self.type_label.place(relx=0.05, rely=0.35, anchor="w")

            self.secret_type, self.secret_type_menu = master.create_option_list(
                self,
                ["Mnemonic seedphrase", "Password", "Wallet descriptor", "Data"],
                width=555
            )
            self.secret_type_menu.place(relx=0.05, rely=0.40, anchor="w")

            def on_next_clicked():
                selected_type = self.secret_type.get()
                if selected_type == "Mnemonic seedphrase":
                    master.show_import_mnemonic()
                elif selected_type == "Password":
                    master.show_import_password()
                elif selected_type == "Wallet descriptor":
                    master.show_import_descriptor()
                elif selected_type == "Data":
                    master.show_import_data()
                else:
                    master.show("ERROR", "Please select a secret type", "Ok")

            self.next_button = master.create_button("Next", command=on_next_clicked, frame=self)
            self.next_button.place(relx=0.95, rely=0.95, anchor="se")

            # place frame
            self.place(relx=1.0, rely=0.5, anchor="e")

        except Exception as e:
            logger.error(f"Init error: {e}", exc_info=True)
