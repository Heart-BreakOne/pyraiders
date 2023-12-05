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
    PhotoImage,
    TclError,
)
from utils.settings import save_settings, check_settings
from components.bot import BotApp


class MyGUIApp:
    def __init__(self, master):
        # Try windows
        try:
            root.iconbitmap(default="assets/icons/icon-128.ico")

        except TclError as e:
            try:
                # Try MacOS
                root.call(
                    "wm", "iconphoto", root._w, PhotoImage(file="assets/icons/icon-128.png")
                )
            except TclError as e:
                print("Probably linux")

        self.master = master

        if check_settings():
            # self.master.withdraw()
            BotApp(self.master)
            return

        master.title("PyCaptain")

        # check if settings exist, if it does, skip everything here and load the bot screen

        self.label = Label(
            master,
            text="""
DO NOT SHARE THIS TOKEN WITH ANYONE BE IT BY TEXT, BY SCREENSHOT OR BY SHARING YOU SETTINGS.JSON FILE
Copy and paste your ACCESS_INFO token to get started
Not URL encoded (must have % symbols)""",
        )
        self.label.grid(row=0, column=1, columnspan=1, pady=10, sticky=W + E + N + S)

        self.entry = Entry(master, width=100)
        self.entry.grid(row=2, column=0, columnspan=3, pady=10, sticky=W + E + N + S)

        self.button = Button(master, text="Start", command=self.on_button_click)
        self.button.grid(row=3, column=1, columnspan=1, pady=10, sticky=W + E + N + S)

        # Set the minimum size (width, height)
        master.minsize(600, 100)

        # Center the window on the screen
        self.center_window()

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
            save_settings(ACCESS_INFO)
            self.master.withdraw()  # Iconify (minimize) the main window
            bot_root = Toplevel()  # Create a new top-level window for BotApp
            BotApp(bot_root)

    def center_window(self):
        # Get the screen width and height
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        # Calculate the position of the window
        x_position = (screen_width - self.master.winfo_reqwidth()) // 3
        y_position = (screen_height - self.master.winfo_reqheight()) // 3

        # Set the window position
        self.master.geometry("+{}+{}".format(x_position, y_position))


if __name__ == "__main__":
    root = Tk()
    app = MyGUIApp(root)
    root.mainloop()
