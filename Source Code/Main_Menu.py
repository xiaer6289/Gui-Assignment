from tkinter import *
from PIL import Image, ImageTk 
def start_timer(self):
    self.withdraw()
    from Pomodoro_Timer import Pomodoro_Timer
    app = Pomodoro_Timer()
    self.deiconify()

def Main_Menu(self):
    for widget in self.winfo_children():
        widget.destroy()
    self.title("Main Menu")
    self.geometry("600x600")
    bg_image = PhotoImage(file="../Source Code/External_Source/Main_Menu_image.png")
    bg_label = Label(self, image=bg_image)
    bg_label.image = bg_image
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    button_timer = Button(self, text="Pomodoro Timer", font=("Comic Sans Ms", 16), bg="Blanched Almond", width=40, command=lambda: start_timer(self))
    button_timer.pack(pady=20)
    button_Tracker = Button(self, text="Expenses Tracker", font=("Comic Sans Ms", 16), bg="Blanched Almond", width=40)
    button_Tracker.pack(pady=20)


if __name__ == "__main__":
    window = Tk()
    Main_Menu(window)
    window.mainloop()

# image not for entier background why