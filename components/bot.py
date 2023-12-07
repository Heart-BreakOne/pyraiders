from tkinter import (
    Tk,
    Label,
    Button,
    W,
    E,
    N,
    S,
    messagebox,
    PhotoImage,
    Frame,
    Canvas,
    Scrollbar,
    Entry,
)
from utils.settings import get_user, delete_settings, open_file
from utils.game_requests import get_display_data, get_units_data
from utils.bot_settings import update_settings
from utils.utils import position_screen
from utils import constants
import sys, os, json


def restart():
    delete_settings()
    messagebox.showinfo(
        "Alert", "Something went wrong while trying to log in.\nCheck your access token"
    )
    python = sys.executable
    os.execl(python, python, *sys.argv)


def display_chests(master):
    # Create a list to store PhotoImage objects
    img_list = []

    for i, icon_path in enumerate(constants.icon_paths[:9]):
        img = PhotoImage(file=icon_path)
        img = img.subsample(2, 2)
        img_list.append(img)

        # Set of labels and entries
        label = Label(
            master,
            text=f"P1: \nP2: ",
            compound="left",
            image=img,
        )

        entry_id = constants.array_of_chest_Ids[i]
        chest_p1 = f"{entry_id}_P1"
        chest_p2 = f"{entry_id}_P2"

        settings_data = open_file()

        # Retrieve values for chest_p1 and chest_p2, defaulting to None if the keys are not present
        value_p1 = settings_data.get(chest_p1, "")
        value_p2 = settings_data.get(chest_p2, "")

        entry_p1 = Entry(master, width=5, name=chest_p1)
        entry_p2 = Entry(master, width=5, name=chest_p2)

        entry_p1.insert(0, value_p1)
        entry_p2.insert(0, value_p2)

        x_coordinate = 20 + (i % 3) * 150
        y_coordinate = 520 + (i // 3) * 70

        label.place(x=x_coordinate, y=y_coordinate)
        entry_p1.place(x=x_coordinate + 60, y=y_coordinate)
        entry_p2.place(x=x_coordinate + 60, y=y_coordinate + 25)

        label.img_ref = img
        label.configure(image=img)


def display_units(self, master):
    settings_data = open_file()
        
    userUnits = settings_data.get("userUnits", {})
    # Canvas for scrollable grid
    self.canvas = Canvas(master, height=500, width=500)
    self.canvas.grid(row=1, column=3, rowspan=5, columnspan=3, sticky=N + S + E + W)

    # Add a scrollbar to the canvas
    scrollbar = Scrollbar(master, command=self.canvas.yview)
    scrollbar.grid(row=1, rowspan=5, column=6, sticky=N + S)

    # Configure the canvas to scroll with the scrollbar
    self.canvas.configure(yscrollcommand=scrollbar.set)

    # Create a frame inside the canvas to hold the scrollable grid
    self.frame = Frame(self.canvas)
    self.canvas.create_window((0, 0), window=self.frame, anchor=N + W)

    for i, unit in enumerate(userUnits):
        unitId = unit["unitId"]
        unitName = unit["unitType"]
        icon_path = f"assets/units/{unitName}.gif"
        img = PhotoImage(file=icon_path)
        img = img.subsample(2, 2)
        unitLevel = unit["level"]
        unitSoul = unit["soulType"]
        unitSpec = unit["specializationUid"]
        unitPriority = unit["priority"]
        label = Label(
            self.frame,
            borderwidth=2,
            relief="solid",
            text=f"{unitName}\nLevel: {unitLevel}\nSpecialization: {unitSpec}\nSoul: {unitSoul}",
            compound="top",
            image=img,
        )
        label.grid(row=i // 3, column=i % 3, padx=5, pady=5, sticky=W)
        label.img_ref = img  # Keep a reference to the PhotoImage object
        label.configure(image=img)

        entry = Entry(self.frame, width=10, name=str(unitId))
        entry.insert(0, unitPriority)
        entry.grid(row=i // 3, column=i % 3, padx=5, pady=10, sticky=N)

    # Update the canvas to configure the scroll region
    self.frame.update_idletasks()
    self.canvas.config(scrollregion=self.canvas.bbox("all"))


def update_data(self):
    entry_chest = {}
    entry_unit = {}
    queue = [self.master]

    while queue:
        current_widget = queue.pop(0)

        if isinstance(current_widget, Entry):
            entry_id = current_widget.winfo_name()
            value = current_widget.get()
            if "chest" in entry_id:
                entry_chest[entry_id] = value
            else:
                entry_unit[entry_id] = value

        elif isinstance(current_widget, Canvas):
            # Add Canvas children to the queue
            queue.extend(current_widget.winfo_children())

        else:
            # Add other widget's children to the queue
            queue.extend(current_widget.winfo_children())
    update_settings(entry_chest, entry_unit)


class BotApp:
    def __init__(self, master):
        self.master = master

        # make_grid(self, master)

        # Check token, get updated game version
        try:
            tokenIsValid = get_user()
        except Exception as e:
            tokenIsValid = False
            restart()
            return
        if tokenIsValid:
            pass
        else:
            restart()
            return

        displayData = get_display_data().get("data", [])
        get_units_data()

        currencies_to_display = [
            "gold",
            # "keys",
            # "bones",
            # "commonspelltome",
            # "retrytoken",
        ]
        icon_path = [
            "assets/currencies/gold.png",
            # "assets/currencies/keys.png",
            # "assets/currencies/bones.png",
            # "assets/currencies/commonspelltome.png",
            # "assets/currencies/retrytoken.png",
        ]

        self.photo_images = []
        self.currency_images = []

        for currency_info in displayData:
            currency_id = currency_info.get("currencyId", "")
            quantity = currency_info.get("quantity", "Not found")
            if currency_id in currencies_to_display:
                column_index = currencies_to_display.index(currency_id)

                # Load the image for the specific currency
                currency_img = PhotoImage(file=icon_path[column_index])
                currency_img = currency_img.subsample(3, 3)
                self.currency_images.append(currency_img)

                label = Label(
                    master,
                    text=f"{quantity}",
                    compound="left",
                    image=currency_img,
                )
                label.place(x=600, y=1 + column_index * 100)

        # Assuming display_units is a function that places widgets using place method
        display_units(self, master)

        display_chests(master)

        self.button = Button(master, text="UPDATE", command=lambda: update_data(self))
        self.button.place(x=500, y=600)

        # When the bot screen is closed, show the main screen again
        master.protocol("WM_DELETE_WINDOW", self.show_main_screen)

        # Set the minimum size (width, height)
        master.minsize(700, 720)

        # Center the window on the screen
        position_screen(self, 4, 4)

    def show_main_screen(self):
        # Show the main screen
        self.master.destroy()


if __name__ == "__main__":
    bot_root = Tk()
    bot_app = BotApp(bot_root)
    bot_root.mainloop()
