from tkinter import *
from datetime import datetime
import winsound
from tkinter import messagebox
import json
import os


class BaseTimer:
    """A minimal base timer class holding timer state and helpers.

    This demonstrates simple inheritance. GUI classes can extend this
    to provide widgets and I/O while reusing timer state/logic.
    """
    def __init__(self, default_hours=0, default_minutes=25):
        self._timer = []  # placeholder for any timer identifiers
        # store defaults as plain integers; GUI IntVar objects are created
        # later after a Tk root exists (see Pomodoro_Timer.__init__)
        self._default_hours = default_hours
        self._default_minutes = default_minutes
        # placeholders for tkinter variables (created after root is available)
        self._hours = None
        self._minutes = None
        self._seconds = None
        self._running = False
        self._break_time = False
        self._mode = "Work Session"
        self._title = "pomodoro timer"

    def format_time(self):
        """Return formatted HH:MM:SS for current time vars."""
        return f"{self._hours.get():02d}:{self._minutes.get():02d}:{self._seconds.get():02d}"

    def is_time_zero(self):
        return self._hours.get() == 0 and self._minutes.get() == 0 and self._seconds.get() == 0


class Pomodoro_Timer(BaseTimer):
    def __init__(self, master=None, filepath='Records.txt'):
        # initialize file/records first
        self._filepath = filepath
        self._records = {}
        self._load()
        # initialize base timer state (hours/minutes/seconds, defaults)
        super().__init__()

        # use master if passed, otherwise create a new Toplevel
        if master is None:
            self.window = Tk()
        else:
            self.window = Toplevel(master)

        self.window.title("Pomodoro Timer")
        app_width = 600
        app_height = 600

    # create tkinter variable objects now that a root exists
        self._hours = IntVar(value=self._default_hours)
        self._minutes = IntVar(value=self._default_minutes)
        self._seconds = IntVar(value=0)

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width // 2) - (app_width // 2)
        y = (screen_height // 2) - (app_height // 2)
        self.window.geometry(f"{app_width}x{app_height}+{x}+{y}")

        # build UI (moved out of nested function so attributes are created on self)
        self.widgets()

        # initial display and start clock updater
        self.update_timer()
        self.date_time_display()

        self.window.mainloop()

    def handle_enter(self, event):
        """Handle Enter press on hour/minute Entry widgets.
        Validate and apply the typed integer to the appropriate IntVar.
        """
        widget = event.widget
        # string processing to remove unwanted space that can be made by user
        text = widget.get().strip()
        # basic validation: must be integer
        try:
            # string processing on converting passing value which default as string to integer
            val = int(text)
        except Exception:
            messagebox.showerror("Invalid input", "Please enter a whole number.")
            return

        # determine which entry called the handler
        if widget is self.hour_entry:
            if val < 0:
                messagebox.showerror("Invalid input", "Hours must be zero or positive.")
                return
            self._hours.set(val)
        elif widget is self.minute_entry:
            if val < 0 or val > 59:
                messagebox.showerror("Invalid input", "Minutes must be between 0 and 59.")
                return
            self._minutes.set(val)
        else:
            # unknown widget - ignore
            return

        # update visible timer immediately
        self.update_timer()

    def widgets(self):
        menubar = Menu(self.window)
        self.window.config(menu = menubar)

        exitMenu = Menu(menubar, tearoff = 0)
        exitMenu.add_command(label = "Return", command = self.return_to_main)
        exitMenu.add_command(label = "Quit", command = self.window.destroy)
        menubar.add_cascade(label = "Exit", menu = exitMenu)
    

        # Header
        header = Label(self.window, text= self._title.title(), font=("Oswald", 20, "bold"))
        header.pack(pady=20)


        self.hasEnded = False
        # date and timer labels
        self.date_label = Label(self.window, text="", font=("Oswald", 20, "bold"))
        self.date_label.pack(pady=10)

        self.timer_label = Label(self.window, text="", font=("Oswald", 50, "bold"))
        self.timer_label.pack(pady=20)

        timer_frame = Frame(self.window)
        timer_frame.pack(pady=5)
        # hours control
        self.hour_label = Label(timer_frame, text="Hours", font=("Arial", 14))
        self.hour_decrease5_btn = Button(timer_frame, text="<<", width=2, command=self.decrease_5hours, cursor="hand2")
        self.hour_decrease_btn = Button(timer_frame, text="<", width=2, command=self.decrease_hours, cursor="hand2")
        self.hour_entry = Entry(timer_frame, textvariable=self._hours, width=5, cursor="xterm")
        self.hour_increase_btn = Button(timer_frame, text=">", width=2, command=self.increase_hours, cursor="hand2")
        self.hour_increase5_btn = Button(timer_frame, text=">>", width=2, command=self.increase_5hours, cursor="hand2")
        self.hour_decrease5_btn.pack(side=LEFT, padx=1)
        self.hour_decrease_btn.pack(side=LEFT, padx=1)
        self.hour_entry.pack(side=LEFT, padx=5)
        # bind Enter to commit value for hours
        self.hour_entry.bind("<Return>", self.handle_enter)
        self.hour_increase_btn.pack(side=LEFT, padx=1)
        self.hour_increase5_btn.pack(side=LEFT, padx=1)

    # minutes control
        self.minute_label = Label(timer_frame, text="Minutes", font=("Arial", 14))
        self.minute_decrease_5btn = Button(timer_frame, text="<<", width=2, command=self.decrease_5min, cursor="hand2")
        self.minute_decrease_btn = Button(timer_frame, text="<", width=2, command=self.decrease_min, cursor="hand2")
        self.minute_entry = Entry(timer_frame, textvariable=self._minutes, width=5, cursor="xterm")
        # bind Enter to commit value for minutes
        self.minute_entry.bind("<Return>", self.handle_enter)
        self.minute_increase_btn = Button(timer_frame, text=">", width=2, command=self.increase_min, cursor="hand2")
        self.minute_increase_5btn = Button(timer_frame, text=">>", width=2, command=self.increase_5min, cursor="hand2")
        self.minute_decrease_5btn.pack(side=LEFT, padx=1)
        self.minute_decrease_btn.pack(side=LEFT, padx=1)
        self.minute_entry.pack(side=LEFT, padx=5)
        self.minute_increase_btn.pack(side=LEFT, padx=1)
        self.minute_increase_5btn.pack(side=LEFT, padx=1)
        self.minute_increase_btn.pack(side=LEFT, padx=1)
        self.minute_increase_5btn.pack(side=LEFT, padx=1)

        btn_frame = Frame(self.window)
        btn_frame.pack(pady = 10)
        self.start_btn = Button(btn_frame, text = "Start", font = ("Arial", 16, "bold"), bg="lightgreen", command=self.start_timer, cursor="hand2", width=6)
        self.start_btn.pack(side = LEFT, padx = 30)

        self.pause_btn = Button(btn_frame, text = "Pause" , font = ("Arial", 16, "bold"), bg="red", command=self.pause_timer, cursor="hand2")
        self.pause_btn.pack(side = LEFT, padx = 30)

        self.reset_btn = Button(btn_frame, text = "Reset", font = ("Arial", 16, "bold"), bg="lightblue", command=self.reset_timer, cursor="hand2")
        self.reset_btn.pack(side = LEFT, padx = 30)

        self.skip_btn = Button(btn_frame, text = "⏯️", font = (16), command = self.skip, cursor="hand2", width=3)
        self.skip_btn.pack(side = LEFT, padx = 40)

        self.text_label = Label(self.window, text=self._mode, font=("Marcellus", 11, "italic"))
        self.text_label.pack(pady = 3)

        # records table with a fixed header and a scrollable body
        table_container = Frame(self.window)
        table_container.pack(pady=20, fill=BOTH, expand=False)

        # header (stays fixed)
        header_frame = Frame(table_container)
        header_frame.pack(fill='x')
        self.table_header = header_frame

        # canvas + scrollbar for rows
        canvas_holder = Frame(table_container)
        canvas_holder.pack(fill=BOTH, expand=True)
        canvas = Canvas(canvas_holder, height=200)
        vsb = Scrollbar(canvas_holder, orient=VERTICAL, command=canvas.yview, cursor="fleur")
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side=RIGHT, fill=Y)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)

        inner = Frame(canvas)
        canvas.create_window((0, 0), window=inner, anchor='nw')

        # mouse wheel support (Windows)
        def _on_mousewheel(event, c=canvas):
            c.yview_scroll(int(-1 * (event.delta / 120)), 'units')

        # keep scrollregion update and show/hide scrollbar depending on content height
        def _on_frame_config(event, c=canvas, v=vsb, inner_f=inner):
            c.configure(scrollregion=c.bbox('all'))
            try:
                inner_h = inner_f.winfo_reqheight()
                canvas_h = c.winfo_height()
            except Exception:
                inner_h = 0
                canvas_h = 0

            # if inner content height is less than or equal to canvas height,
            # hide the scrollbar and prevent scrolling
            if inner_h <= max(1, canvas_h):
                # hide scrollbar if shown
                try:
                    v.pack_forget()
                except Exception:
                    pass
                # reset view to top
                try:
                    c.yview_moveto(0)
                except Exception:
                    pass
                # unbind global mousewheel to avoid scrolling other widgets
                try:
                    c.unbind_all('<MouseWheel>')
                except Exception:
                    pass
            else:
                # ensure scrollbar is visible
                if not v.winfo_ismapped():
                    v.pack(side=RIGHT, fill=Y)
                # bind mouse wheel for scrolling
                c.bind_all('<MouseWheel>', _on_mousewheel)

        inner.bind('<Configure>', _on_frame_config)

        self.table_canvas = canvas
        self.table_inner = inner
        self.create_table()

    
    def date_time_display(self):
        # update date/time label every second
        now = datetime.now()
        if self.hasEnded:
            return
        self.date_label.config(text=now.strftime("%A, %d %B %Y"))
        # if not self._running and self._hours.get() == 0 and self._minutes.get() == 0 and self._seconds.get() == 0:
        #     self.timer_label.config(text=now.strftime("%H:%M:%S"))
        self.window.after(1000, self.date_time_display) # update every second

    def update_timer(self):
        hours =f"{self._hours.get():02d}"
        min = f"{self._minutes.get():02d}"
        sec = f"{self._seconds.get():02d}"
        self.timer_label.config(text = f"{hours}:{min}:{sec}")

    def increase_hours(self): # incrase hour setting countdown
        if self._running == False:
            self.hour_entry.config(state=NORMAL)
            self._hours.set(self._hours.get() + 1)
        if self._timer == True:
            self._hours.set(self._hours.get() + 0)
        self.update_timer()

    def increase_5hours(self): # incrase hour setting countdown
        if self._running == False:
            self.hour_entry.config(state=NORMAL)
            self._hours.set(self._hours.get() + 5)
        if self._timer == True:
            self._hours.set(self._hours.get() + 0)
        self.update_timer()

    def decrease_hours(self):
        if self._running == False:
            if self._hours.get() > 0:
                self._hours.set(self._hours.get() - 1) # decrease hour setting countdown
                self.hour_entry.config(state=NORMAL)
            else:
                self._hours.set(0)
        if self._timer == True:
            self._hours.set(self._hours.get() - 0)
        self.update_timer()

    def decrease_5hours(self):
        if self._running == False:
            self.hour_entry.config(state=NORMAL)
            match self._hours.get():
                case h if h >= 5:
                    self._hours.set(h - 5)  # decrease hour setting countdown
                case 4:
                    self._hours.set(0)
                case 3:
                    self._hours.set(0)
                case 2:
                    self._hours.set(0)
                case 1:
                    self._hours.set(0)
                case _:
                    self._hours.set(0)
        if self._timer == True:
            self._hours.set(self._hours.get() - 0)
        self.update_timer()

    def increase_min(self):  # increase minute setting countdown
        if self._running == False:
            self.minute_entry.config(state=NORMAL)
            self._minutes.set(self._minutes.get() + 1)
        if self._minutes.get() > 59:
            self._hours.set(self._hours.get() + 1)
            self._minutes.set(0) # reset minute
        if self._timer == True:
            self._minutes.set(self._minutes.get() + 0)
        self.update_timer()

    def increase_5min(self):  # increase minute setting countdown
        if self._running == False:
            self.minute_entry.config(state=NORMAL)
            self._minutes.set(self._minutes.get() + 5)
        if self._minutes.get() > 59:
            self._hours.set(self._hours.get() + 1)
            self._minutes.set(0) # reset minute
        if self._timer == True:
            self._minutes.set(self._minutes.get() + 0)
        self.update_timer()

    def decrease_min(self): #decrease minute setting countdown
        if self._running == False:
            self.minute_entry.config(state=NORMAL)
            if self._minutes.get() > 0:
                self._minutes.set(self._minutes.get() - 1) 
            elif self._minutes.get() == 0 and self._hours.get() > 0:
                self._minutes.set(59)
                self._hours.set(self._hours.get() - 1) # decrease hour if minute larger than 1
            else:
                self._minutes.set(0)
        if self._timer == True:
            self._minutes.set(self._minutes.get() - 0)
        self.update_timer()

    def decrease_5min(self): #decrease minute setting countdown
        h = self._hours.get()
        m = self._minutes.get()
        if self._running == False:
            self.minute_entry.config(state=NORMAL)
            match m:
                case m if m >= 5:
                    self._minutes.set(m - 5)  # decrease hour setting countdown
                case 4:
                    self._minutes.set(0)
                case 3:
                    self._minutes.set(0)
                case 2:
                    self._minutes.set(0)
                case 1:
                    self._minutes.set(0)
                case _ if h > 0:
                    self._hours.set(h - 1)
                    self._minutes.set(60 + m - 5)  # rollover from hour
                case _:
                    self._minutes.set(0)

        if self._timer == True:
            self._minutes.set(self._minutes.get() - 0)
        self.update_timer()

    def countdown(self):
        if not self._running:
            return # to stop execution if it is not running

        min = self._minutes.get()
        hours = self._hours.get()
        sec = self._seconds.get()

        if hours == 0 and min == 0 and sec == 0:
            self._running = False
            self.start_btn.config(state=NORMAL)
            self.pause_btn.config(state=DISABLED)
            self.minute_entry.config(state=NORMAL)
            self.hour_entry.config(state=NORMAL)
            if self._mode == "Work Session":
                info = "Times Up!\n Working session end!\nTime to have a break!"
                messagebox.showinfo("Times Up!", info)
                try:
                    winsound.Beep()
                except Exception:
                    pass
                # record the work session as completed before switching to break
                if hasattr(self, '_countdown_time'):
                    self.add_record(self._countdown_time, True)
                    self._completed = True
                self._break()
            else:
                info2 = "Times Up! Break session end!\nTime to Work!"
                messagebox.showinfo("Times Up!", info2)
                try:
                    winsound.Beep()
                except Exception:
                    pass
                self._work()

            return # return the state of the button commands(function)
        
        # count down formula for time
        if sec > 0:
            sec -= 1
        elif min > 0:
            min -= 1
            sec = 59
        elif hours > 0:
            hours -= 1
            min = 59
            sec = 59

        self._seconds.set(sec)
        self._minutes.set(min)
        self._hours.set(hours)
        self.update_timer()
        if self._running:
            self.timer_id = self.window.after(1000, self.countdown)

    def start_timer(self):
        if not self._running:
            try:
                hours = int(self._hours.get())
                minutes = int(self._minutes.get())
            
                if hours < 0 or minutes < 0 or minutes >= 60 or (hours == 0 and minutes == 0):
                    raise ValueError
                
            #exception handling for value error
            except ValueError as e:
                errormsg = "Invalid input!\nOnly accept 1-59 for minutes\nOnly accept positive number for hours"
                messagebox.showerror("Error", errormsg)
                return
            
        # ensure any previously scheduled countdown callback is cancelled
        try:
            if hasattr(self, 'timer_id') and self.timer_id is not None:
                self.window.after_cancel(self.timer_id)
        except Exception:
            pass

        # only run if input is valid
        self._running = True
        self.start_btn.config(state=DISABLED)
        self.pause_btn.config(state=NORMAL)
        self.hour_entry.config(state=DISABLED)
        self.minute_entry.config(state=DISABLED)

        # save validated values
        self._hours.set(hours)
        self._minutes.set(minutes)
        # only store the countdown snapshot for work sessions so break start
        # doesn't overwrite it when break auto-starts
        if getattr(self, '_mode', 'Work Session') == "Work Session":
            self._countdown_time = f"{self._hours.get():02d}:{self._minutes.get():02d}:{self._seconds.get():02d}"
        else:
            # keep separate variable for break if needed
            self._break_countdown_time = f"{self._hours.get():02d}:{self._minutes.get():02d}:{self._seconds.get():02d}"
        self._completed = False
        self.countdown()

    def pause_timer(self):
        if self._running:
            self._running = False
            self.pause_btn.config(state=DISABLED)
            self.start_btn.config(state=NORMAL)
            self.hour_entry.config(state=DISABLED)
            self.minute_entry.config(state=DISABLED)
            # cancel any scheduled countdown callback to avoid multiple timers
            try:
                if hasattr(self, 'timer_id') and self.timer_id is not None:
                    self.window.after_cancel(self.timer_id)
                    self.timer_id = None
            except Exception:
                pass


    def reset_timer(self):
        # remember current mode so switching to work() here doesn't cause
        # an accidental record for a break reset
        prev_mode = self._mode
        self.pause_timer()
        self._hours.set(self._default_hours)
        self._minutes.set(self._default_minutes)
        self._seconds.set(0)
        self.update_timer()
        self.pause_btn.config(state=NORMAL)
        self.hour_entry.config(state=NORMAL)
        self.minute_entry.config(state=NORMAL)

        # if we were in a break, switch back to work but do not record the break
        if prev_mode == "Break Session":
            self._work()

        # only add an 'Incomplete' record when the session being reset was a Work Session
        if prev_mode == "Work Session":
            if hasattr(self, '_countdown_time') and not getattr(self, '_completed', False):
                self.add_record(self._countdown_time, False)
                self._completed = True

    def create_table(self): # create table to display record
        # prepare records storage and render any saved records immediately
        if not isinstance(self._records, dict):
            self._records = {}
        self._records_dict = self._records
    # draw header + rows from loaded records
        self.refresh_table()

    def refresh_table(self):
        # Clear header and inner frames
        for widget in self.table_header.winfo_children():
            widget.destroy()
        for widget in self.table_inner.winfo_children():
            widget.destroy()

        # Recreate header (fixed)
        header = ["Date", "Time", "Countdown", "Completion", ""]
        for col, text in enumerate(header):
            label = Label(self.table_header, text=text, relief="solid", width=16, bg="yellow")
            label.grid(row=0, column=col, sticky="nsew")

        # Recreate rows inside scrollable inner frame
        for row, (key, record) in enumerate(self._records_dict.items(), start=0):
            values = [record['date'], record['time'], record['countdown'],
                      "Completed" if record['complete'] else "Incomplete"]
            for col, val in enumerate(values):
                label = Label(self.table_inner, text=val, relief="solid", width=16)
                label.grid(row=row, column=col, sticky="nsew", padx=0, pady=0)

            dlt_btn = Button(self.table_inner, text="Delete", font=("Arial", 8), width=18,
                            cursor="hand2", command=lambda k=key: self.delete_record(k))
            dlt_btn.grid(row=row, column=len(values), sticky="nsew", padx=0, pady=0)
        # ensure canvas/layout updated so scrollbar visibility is recalculated
        try:
            self.table_canvas.update_idletasks()
        except Exception:
            pass

    def add_record(self, countdown_time, complete):
        # don't add records for break sessions
        if self._mode == "Break Session":
            return
        now = datetime.now()
        date_str = now.strftime("%Y/%m/%d")
        time_str = now.strftime("%H:%M")
        key = now.isoformat()
        self._records_dict[key] = {
            'date': date_str,
            'time': time_str,
            'countdown': countdown_time,
            'complete': bool(complete)
        }
        self.refresh_table()
        self._save()

    def delete_record(self, key):
        if key in self._records_dict:
            del self._records_dict[key]
        self.refresh_table()
        # persist changes to disk
        try:
            self._save()
        except Exception:
            pass

    def skip(self):
        if self._mode == "Work Session":
            # to prevent invoking start_timer twice
            # if currently running a work session, record it as incomplete
            if getattr(self, '_running', False) and hasattr(self, '_countdown_time') and not getattr(self, '_completed', False):
                self.add_record(self._countdown_time, False)
                self._completed = True
            # cancel any scheduled callback and skip to break
            try:
                if hasattr(self, 'timer_id') and self.timer_id is not None:
                    self.window.after_cancel(self.timer_id)
                    self.timer_id = None
            except Exception:
                pass
            self._break()
        else:
            # skip back to work
            self._work()

    def _break(self): # move to break session and start countdown for 5 min
        self.pause_timer()
        self._mode = "Break Session"
        self._hours.set(0)
        self._minutes.set(5)
        self._seconds.set(0)
        self.update_timer()
        self.text_label.config(text=self._mode)
        self.start_timer()

    def _work(self): # move to work session 
        self.pause_timer()
        self._mode = "Work Session"
        self._hours.set(0)
        self._minutes.set(25)
        self._seconds.set(0)
        self.text_label.config(text=self._mode)
        self.update_timer()

    def _save(self): # save dictionary into txt file
        try:
            with open(self._filepath, 'w', encoding='utf-8') as f:
                json.dump(self._records, f, indent=2, ensure_ascii=False)
        except Exception:
            print('Failed to save records')

    def _load(self): #display rhe data in txt file
        if os.path.exists(self._filepath):
            try:
                with open(self._filepath, 'r', encoding='utf-8') as f:
                    self._records = json.load(f)
            except Exception:
                print('Failed to load records')
                self._records = {}

    def return_to_main(self):
        self.hasEnded = True
        for widget in self.window.winfo_children():
            widget.destroy()

        # rebuild main menu
        from Main_Menu import Main_Menu
        Main_Menu(self.window)
    
#Pomodoro_Timer()
