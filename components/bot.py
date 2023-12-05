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
from utils.settings import get_user, delete_settings
from utils.game_requests import get_display_data, get_units_data
from utils.bot_settings import update_settings
import sys, os, json


def restart():
    delete_settings()
    messagebox.showinfo(
        "Alert", "Something went wrong while trying to log in.\nCheck your access token"
    )
    python = sys.executable
    os.execl(python, python, *sys.argv)


def display_chests(self, master):
    self.icon_paths = [
        "assets/chests/chestbronze.png",
        "assets/chests/chestsilver.png",
        "assets/chests/chestgold.png",
        "assets/chests/chestboostedgold.png",
        "assets/chests/chestboostedscroll.png",
        "assets/chests/chestboostedskin.png",
        "assets/chests/chestboostedtoken.png",
        "assets/chests/chestboss.png",
        "assets/chests/chestbosssuper.png",
    ]

    array_of_chest_Ids = [
        "chestbronze",
        "chestsilver",
        "chestgold",
        "chestboostedgold",
        "chestboostedscroll",
        "chestboostedskin",
        "chestboostedtoken",
        "chestboss",
        "chestbosssuper",
    ]

    # Create a list to store PhotoImage objects
    img_list = []

    for i, icon_path in enumerate(self.icon_paths[:9]):
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

        entry_id = array_of_chest_Ids[i]
        entry_p1 = Entry(master, width=5, name=f"{entry_id}_P1")
        entry_p2 = Entry(master, width=5, name=f"{entry_id}_P2")

        x_coordinate = 20 + (i % 3) * 150
        y_coordinate = 520 + (i // 3) * 70

        label.place(x=x_coordinate, y=y_coordinate)
        entry_p1.place(x=x_coordinate + 60, y=y_coordinate)
        entry_p2.place(x=x_coordinate + 60, y=y_coordinate + 25)

        label.img_ref = img
        label.configure(image=img)

def display_units(self, master):
    with open("pycaptain_settings.json", "r") as file:
        settings_data = json.load(file)
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
            img = img.subsample(3, 3)
            unitLevel = unit["level"]
            unitSoul = unit["soulType"]
            unitSpec = unit["specializationUid"]
            unitPriority = unit["priority"]
            label = Label(
                self.frame,
                borderwidth=2,
                relief="solid",
                text=f"{unitName}\nLevel: {unitLevel}\nSpecialization: {unitSpec}\nSoul: {unitSoul}\nPriority: {unitPriority}",
                compound="top",
                image=img,
            )
            label.grid(row=i // 3, column=i % 3, padx=5, pady=5, sticky=W)
            label.img_ref = img  # Keep a reference to the PhotoImage object
            label.configure(image=img)
            
            entry = Entry(self.frame, width=10, name=str(unitId))
            entry.grid(row=i // 3, column=i % 3, padx=5, pady=10, sticky=N)

        # Update the canvas to configure the scroll region
        self.frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))


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
            "keys",
            # "bones",
            "commonspelltome",
            "retrytoken",
        ]
        self.icon_paths = [
            "assets/currencies/gold.png",
            "assets/currencies/keys.png",
            # "assets/currencies/bones.png",
            "assets/currencies/commonspelltome.png",
            "assets/currencies/retrytoken.png",
        ]

        master.title("PyCaptain")

        self.photo_images = []
        self.currency_images = []

        for currency_info in displayData:
            currency_id = currency_info.get("currencyId", "")
            quantity = currency_info.get("quantity", "Not found")
            if currency_id in currencies_to_display:
                column_index = currencies_to_display.index(currency_id)

                # Load the image for the specific currency
                currency_img = PhotoImage(file=self.icon_paths[column_index])
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

        display_chests(self, master)
        
        self.button = Button(master, text="UPDATE", command=self.update_data())
        self.button.place(x=500, y=600)

        # When the bot screen is closed, show the main screen again
        master.protocol("WM_DELETE_WINDOW", self.show_main_screen)

        # Set the minimum size (width, height)
        master.minsize(750, 900)

        # Center the window on the screen
        self.center_window()
        
    def update_data(self):
        update_settings()
        
    def show_main_screen(self):
        # Show the main screen
        self.master.destroy()

    def center_window(self):
        # Get the screen width and height
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        # Calculate the position of the window
        x_position = (screen_width - self.master.winfo_reqwidth()) // 4
        y_position = (screen_height - self.master.winfo_reqheight()) // 4

        # Set the window position
        self.master.geometry("+{}+{}".format(x_position, y_position))

if __name__ == "__main__":
    bot_root = Tk()
    bot_app = BotApp(bot_root)
    bot_root.mainloop()