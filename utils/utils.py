#Positions window to the "center" of the screen
def position_screen(self, x, y):
         # Get the screen width and height
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        # Calculate the position of the window
        x_position = (screen_width - self.master.winfo_reqwidth()) // x
        y_position = (screen_height - self.master.winfo_reqheight()) // y

        # Set the window position
        self.master.geometry("+{}+{}".format(x_position, y_position))