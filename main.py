import tkinter as tk
from components.captain import CaptainGUI
from components.viewer import ViewerGUI
from utils.utils import position_screen

class PyRaidersGUI:
    def __init__(self, master):
        
        #Attemps to set application icon on windows
        try:
            root.iconbitmap(default="assets/icons/icon-128.ico")
        except tk.TclError as e:
            try:
                # Try MacOS
                root.call(
                    "wm",
                    "iconphoto",
                    root._w,
                    tk.PhotoImage(file="assets/icons/icon-128.png"),
                )
            except tk.TclError as e:
                #User is probably using linux
                print("Probably linux")

        self.master = master
        master.title("PyRaiders")

        # Load the first image
        image_path1 = "assets/images/viewer.png"
        self.photo1 = tk.PhotoImage(file=image_path1)
        self.photo1 = self.photo1.subsample(2, 2)
        self.label1 = tk.Label(master, text="VIEWER", image=self.photo1, compound="top")
        self.label1.place(x=0, y=0)
        self.label1.bind("<Button-1>", self.on_viewer_click)

        # Load the second image
        image_path2 = "assets/images/captain.png"
        self.photo2 = tk.PhotoImage(file=image_path2)
        self.photo2 = self.photo2.subsample(2, 2)
        self.label2 = tk.Label(master, text="CAPTAIN", image=self.photo2, compound="top")
        self.label2.place(x=200, y=0)
        self.label2.bind("<Button-1>", self.on_captain_click)

        # Set the minimum size (width, height)
        master.minsize(375, 260)

        # Center the window on the screen
        position_screen(self, 2, 2)

    #User is viewer
    def on_viewer_click(self, event):
        self.master.withdraw()
        viewerGui = tk.Toplevel()
        ViewerGUI(viewerGui)
    #User is a captain
    def on_captain_click(self, event):
        self.master.withdraw()
        captainGui = tk.Toplevel()
        CaptainGUI(captainGui)

if __name__ == "__main__":
    root = tk.Tk()
    app = PyRaidersGUI(root)
    root.mainloop()
