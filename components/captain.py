from tkinter import (
    Tk,
    Label,
    Button,
    Entry,
    W,
    E,
    N,
    S,
    messagebox,
    Toplevel,
)
from utils.settings import save_settings, check_settings
from utils.utils import position_screen
from components.bot import CaptainApp
from utils import constants


class CaptainGUI:
    def __init__(self, master):
        self.master = master

        # check if settings exist, if it does, skip everything here and load the bot screen
        if check_settings():
            # self.master.withdraw()
            CaptainApp(self.master)
            return

        # Add label, an entry text for the token and a button for confirmation
        self.label = Label(
            master,
            text=constants.main_screen_label,
        )
        self.label.grid(row=0, column=1, columnspan=1, pady=10, sticky=W + E + N + S)

        # Entry field for the token
        self.entry = Entry(master, width=100)
        self.entry.grid(row=2, column=0, columnspan=3, pady=10, sticky=W + E + N + S)

        # When the button is clicked call _on_button_click
        self.button = Button(master, text="Start", command=self.on_button_click)
        self.button.grid(row=3, column=1, columnspan=1, pady=10, sticky=W + E + N + S)

        position_screen(self, 3, 2)

    # Get the access token, if it's not empty save to the settings and load bot
    def on_button_click(self):
        # Get the text from the entry widget
        ACCESS_INFO = self.entry.get()

        if ACCESS_INFO == "":
            messagebox.showinfo(
                "Alert",
                "Without the access info token the tool can't login to Stream Raiders",
            )
            return
        else:
            # settings exist, remove current window and load bot window
            save_settings(ACCESS_INFO)
            self.master.withdraw()
            bot_root = Toplevel()
            CaptainApp(bot_root)


if __name__ == "__main__":
    master = Tk()
    app = CaptainGUI(master)
    master.mainloop()