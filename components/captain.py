import tkinter as tk
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
        self.label = tk.Label(
            master,
            text=constants.main_screen_label,
        )
        self.label.grid(row=0, column=1, columnspan=1, pady=10, sticky=tk.W + tk.E + tk.N + tk.S)

        # Entry field for the token
        self.entry = tk.Entry(master, width=100)
        self.entry.grid(row=2, column=0, columnspan=3, pady=10, sticky=tk.W + tk.E + tk.N + tk.S)

        # When the button is clicked call _on_button_click
        self.button = tk.Button(master, text="Start", command=self.on_button_click)
        self.button.grid(row=3, column=1, columnspan=1, pady=10, sticky=tk.W + tk.E + tk.N + tk.S)

        position_screen(self, 3, 2)

    # Get the access token, if it's not empty save to the settings and load bot
    def on_button_click(self):
        # Get the text from the entry widget
        ACCESS_INFO = self.entry.get()

        if ACCESS_INFO == "":
            tk.messagebox.showinfo(
                "Alert",
                "Without the access info token the tool can't login to Stream Raiders",
            )
            return
        else:
            # settings exist, remove current window and load bot window
            save_settings(ACCESS_INFO)
            self.master.withdraw()
            bot_root = tk.Toplevel()
            CaptainApp(bot_root)


if __name__ == "__main__":
    master = tk.Tk()
    app = CaptainGUI(master)
    master.mainloop()