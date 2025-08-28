from tkinter import *
from PIL import Image, ImageTk 


def start_timer(self):
    for widget in self.winfo_children():
        widget.destroy()
    self.withdraw()
    from Pomodoro_Timer import Pomodoro_Timer
    app = Pomodoro_Timer()
    self.deiconify()

def start_expenses_tracker(self):
    self.withdraw()
    # from Expenses_Tracker import Expenses_Tracker
    # app = Expenses_Tracker()
    self.deiconify()

def start_note_organizer(self):
    self.withdraw()
    # from Note_Organizer import Note_Organizer
    # app = Note_Organizer()
    self.deiconify()

def start_reminder_app(self):
    self.withdraw()
    # from Simple_Reminder_App import Simple_Reminder_App
    # app = Simple_Reminder_App()
    self.deiconify()

def Main_Menu(self):
    for widget in self.winfo_children():
        widget.destroy()
    self.title("Main Menu")
    self.geometry("600x600")
    bg_image = PhotoImage(file="Source Code/External_Source/Test.png")
    bg_label = Label(self, image=bg_image)
    bg_label.image = bg_image
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    title_label = Label(self)
    title_label.pack(pady=50)
    btn_timer = Button(self, text="Pomodoro Timer", font=("Comic Sans Ms", 16), bg="Blanched Almond", width=40, command=lambda:start_timer(self))
    btn_timer.pack(pady=20)
    btn_tracker = Button(self, text="Expenses Tracker", font=("Comic Sans Ms", 16), bg="Blanched Almond", width=40, command=lambda:start_expenses_tracker(self))
    btn_tracker.pack(pady=20)
    btn_note = Button(self, text="Note Organizer", font=("Comic Sans Ms", 16), bg="Blanched Almond", width=40, command=lambda:start_note_organizer(self))
    btn_note.pack(pady=20)
    btn_reminder = Button(self, text="Simple Reminder App", font=("Comic Sans Ms", 16), bg="Blanched Almond", width=40, command=lambda:start_reminder_app(self))
    btn_reminder.pack(pady=20)


if __name__ == "__main__":
    window = Tk()
    Main_Menu(window)
    window.mainloop()

# image not for entier background why