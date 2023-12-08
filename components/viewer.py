import random
import tkinter as tk
from utils import constants
from utils.utils import position_screen
from utils.settings import write_file

class ViewerGUI:
    def __init__(self, master):
        self.master = master

        # Canvas for scrollable grid
        canvas = tk.Canvas(master, height=700, width=1000)
        canvas.grid(
            row=1, column=3, rowspan=5, columnspan=3, sticky=tk.N + tk.S + tk.E + tk.W
        )

        # Add a scrollbar to the canvas
        scrollbar = tk.Scrollbar(master, command=canvas.yview)
        scrollbar.grid(row=1, rowspan=5, column=6, sticky=tk.N + tk.S)

        # Configure the canvas to scroll with the scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the canvas to hold the scrollable grid
        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor=tk.N + tk.W)

        button = tk.Button(master, text="START", command=lambda: save_accounts(frame))
        button.grid(row=0, column=4, padx=10, pady=10)

        for i in range(100):
            label = tk.Label(
                frame,
                text=f"Unique name",
            )
            label.grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            entry = tk.Entry(frame, width=20, name=str(f"name_{i}"))
            entry.grid(row=i, column=1, padx=5, pady=10, sticky=tk.N)
            label = tk.Label(
                frame,
                text=f"Access token",
            )
            label.grid(row=i, column=2, padx=5, pady=5, sticky=tk.W)
            entry = tk.Entry(frame, width=60, name=str(f"token_{i}"))
            entry.grid(row=i, column=3, padx=5, pady=10, sticky=tk.N)

        # Update the canvas to configure the scroll region
        frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        position_screen(self, 2, 2)

def save_accounts(frame):
    entry_dict = {}
    children = frame.winfo_children()
    children = [child for child in children if not isinstance(child, tk.Label)]
    for i in range(0, len(children), 2):
        # Ensure we have a pair of consecutive widgets (Entry and Label/Entry)
        if i + 1 < len(children):
            widget_class_1 = children[i].winfo_class()
            widget_class_2 = children[i + 1].winfo_class()
            if "Entry" in widget_class_1 and "Entry" in widget_class_2:
                # Get the values from the Entry widgets and store as a pair
                entry_name = children[i].get()
                entry_token = children[i + 1].get()
                user_agent = random.choice(constants.user_agents)
                proxy = random.choice(constants.proxies)
                
                entry_dict[entry_name] = {"name": entry_name, "token": entry_token, "user_agent": user_agent, "proxy": proxy}

    filtered_entries = {}
    seen_names = set()
    seen_tokens = set()
    for entry_name, entry_data in entry_dict.items():
        name = entry_data["name"]
        token = entry_data["token"]

        # Skip entries with empty strings
        if not name or not token:
            continue

        # Remove entries with duplicate names
        if name in seen_names:
            continue

        # Remove entries with duplicate tokens
        if token in seen_tokens:
            continue

        # Add the entry to the filtered dictionary
        filtered_entries[entry_name] = entry_data

        # Update the sets to keep track of seen names and tokens
        seen_names.add(name)
        seen_tokens.add(token)
        
    write_file(constants.py_accounts, filtered_entries)

if __name__ == "__main__":
    root = tk.Tk()
    app = ViewerGUI(root)
    root.mainloop()
