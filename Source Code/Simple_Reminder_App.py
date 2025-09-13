import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import threading
import json
import os
import winsound
import time

# main
class Simple_Reminder_App:
    """Main reminder application GUI and logic."""

    def __init__(self, root):
        self.root = root
        self.root.title("Simple Reminder App")
        
        menubar = tk.Menu(self.root)
        self.root.config(menu = menubar)

        exitMenu = tk.Menu(menubar, tearoff = 0)
        exitMenu.add_command(label = "Return", command = self.return_to_main)
        exitMenu.add_command(label = "Quit", command = self.root.destroy)
        menubar.add_cascade(label = "Exit", menu = exitMenu)

        # Center the application window
        app_width = 800
        app_height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (app_width // 2)
        y = (screen_height // 2) - (app_height // 2)
        self.root.geometry(f"{app_width}x{app_height}+{x}+{y}")

        # Create manager to handle reminders
        self.manager = ReminderManager()
        self.manager.load_reminders()

        self.edit_index = None  # Tracks which reminder is being edited

        # style for table
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background="#ffffff",
            foreground="#000000",
            rowheight=25,
            fieldbackground="#ffffff",
            borderwidth=1,
            relief="solid"
        )
        style.configure(
            "Treeview.Heading",
            font=("Helvetica", 10, "bold"),
            borderwidth=1,
            relief="solid"
        )
        style.map(
            "Treeview",
            background=[("selected", "#3498db")],
            foreground=[("selected", "white")]
        )

        # tabel for title
        tk.Label(root, text="Simple Reminder App", font=("Helvetica", 18, "bold")).pack(pady=10)

        # reminder form
        form_frame = tk.LabelFrame(root, text="Add / Edit Reminder", padx=10, pady=10)
        form_frame.pack(fill="x", padx=10, pady=10)

        # Reminder Type
        tk.Label(form_frame, text="Type:").grid(row=0, column=0, sticky="w")
        self.reminder_types = ["Class", "Task", "Meeting", "Doctor Appointment", "Other"]
        self.type_combo = ttk.Combobox(form_frame, values=self.reminder_types, state="readonly")
        self.type_combo.grid(row=0, column=1, padx=5)
        self.type_combo.bind("<<ComboboxSelected>>", self.toggle_custom_title)

        # Custom Title (only visible when "Other" is selected)
        self.custom_title_label = tk.Label(form_frame, text="Custom Title:")
        self.title_entry = tk.Entry(form_frame)

        # Date Picker
        self.date_label = tk.Label(form_frame, text="Date:")
        self.date_label.grid(row=0, column=2, sticky="w", padx=(20, 0))
        self.date_entry = DateEntry(form_frame, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=0, column=3, padx=5)

        # Time Picker
        tk.Label(form_frame, text="Time:").grid(row=0, column=4, sticky="w", padx=(20, 0))
        current_time = datetime.now()
        current_hour = current_time.strftime("%I")
        current_minute = current_time.strftime("%M")
        current_ampm = current_time.strftime("%p")

        self.hour_spin = tk.Spinbox(form_frame, from_=1, to=12, width=5, format="%02.0f")
        self.hour_spin.grid(row=0, column=5, sticky="w")
        self.hour_spin.delete(0, tk.END)
        self.hour_spin.insert(0, current_hour)

        self.min_spin = tk.Spinbox(form_frame, from_=0, to=59, width=5, format="%02.0f")
        self.min_spin.grid(row=0, column=6, sticky="w", padx=(5, 0))
        self.min_spin.delete(0, tk.END)
        self.min_spin.insert(0, current_minute)

        self.ampm_combo = ttk.Combobox(form_frame, values=["AM", "PM"], state="readonly", width=5)
        self.ampm_combo.grid(row=0, column=7, padx=5)
        self.ampm_combo.set(current_ampm)

        # Repeat Options
        tk.Label(form_frame, text="Repeat:").grid(row=1, column=0, sticky="w", pady=5)
        self.repeat_combo = ttk.Combobox(form_frame, values=["Once", "Repeat"], state="readonly")
        self.repeat_combo.grid(row=1, column=1, padx=5, pady=5)
        self.repeat_combo.set("Once")
        self.repeat_combo.bind("<<ComboboxSelected>>", self.update_repeat_options)

        # Days of the week checkboxes
        self.days_frame = tk.Frame(form_frame)
        self.days_vars = {}
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for idx, day in enumerate(days):
            var = tk.BooleanVar()
            self.days_vars[day] = var
            tk.Checkbutton(self.days_frame, text=day, variable=var).grid(row=0, column=idx, padx=2)
        self.days_frame.grid(row=1, column=2, columnspan=5, pady=5)
        self.days_frame.grid_remove()

        # Buttons for Save & Reset reminders
        self.save_btn = tk.Button(form_frame, text="Save Reminder", bg="#27ae60", fg="white",
                                  command=self.save_reminder)
        self.save_btn.grid(row=2, column=0, padx=5, pady=10)

        tk.Button(form_frame, text="Reset", bg="#95a5a6", fg="white",
                  command=self.clear_form).grid(row=2, column=1, padx=5, pady=10)

        # reminder table
        columns = ("Title", "Date", "Time", "Repeat", "Days")
        self.tree = ttk.Treeview(root, columns=columns, show="headings", height=12, style="Treeview")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center", stretch=True)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Row styling
        self.tree.tag_configure("oddrow", background="#f2f2f2")
        self.tree.tag_configure("evenrow", background="#ffffff")
        self.tree.tag_configure("overdue", background="#ffcccc", foreground="red")

        # Table action buttons
        table_btn_frame = tk.Frame(root)
        table_btn_frame.pack(pady=5)
        tk.Button(table_btn_frame, text="Edit", bg="#f39c12", fg="white", width=15,
                  command=self.edit_reminder).grid(row=0, column=0, padx=5)
        tk.Button(table_btn_frame, text="Delete", bg="#e74c3c", fg="white", width=15,
                  command=self.delete_reminder).grid(row=0, column=1, padx=5)
        tk.Button(table_btn_frame, text="Clear All", bg="#95a5a6", fg="white", width=15,
                  command=self.clear_all).grid(row=0, column=2, padx=5)

        # Load saved reminders into table
        self.refresh_list()

        # Start background thread to check reminders
        threading.Thread(target=self.check_reminders, daemon=True).start()

    # helpers for form toggles and resets
    def toggle_custom_title(self, event=None):
        """Show or hide custom title entry if 'Other' is selected."""
        if self.type_combo.get() == "Other":
            self.custom_title_label.grid(row=0, column=8, padx=(20, 0))
            self.title_entry.grid(row=0, column=9, padx=5)
        else:
            self.custom_title_label.grid_remove()
            self.title_entry.grid_remove()

    def update_repeat_options(self, event=None):
        """Show or hide repeat day checkboxes."""
        if self.repeat_combo.get() == "Repeat":
            self.days_frame.grid()
        else:
            self.days_frame.grid_remove()

    def clear_form(self):
        """Reset form fields to default."""
        self.type_combo.set("")
        self.custom_title_label.grid_remove()
        self.title_entry.grid_remove()
        self.date_entry.set_date(datetime.now().date())
        self.hour_spin.delete(0, tk.END)
        self.hour_spin.insert(0, datetime.now().strftime("%I"))
        self.min_spin.delete(0, tk.END)
        self.min_spin.insert(0, datetime.now().strftime("%M"))
        self.ampm_combo.set(datetime.now().strftime("%p"))
        self.repeat_combo.set("Once")
        for var in self.days_vars.values():
            var.set(False)
        self.update_repeat_options()
        self.edit_index = None
        self.save_btn.config(text="Save Reminder")

    # save or update reminder method
    def save_reminder(self):
        """Save a new reminder or update an existing one."""
        if not self.type_combo.get():
            messagebox.showwarning("Input Error", "Please select a reminder type!")
            return

        title = self.type_combo.get()
        if title == "Other":
            title = self.title_entry.get().strip()
            if not title:
                messagebox.showwarning("Input Error", "Please enter a custom title!")
                return

        # Get date and time
        date_str = self.date_entry.get_date().strftime("%Y-%m-%d")
        hour = int(self.hour_spin.get())
        minute = int(self.min_spin.get())
        ampm = self.ampm_combo.get()
        if ampm == "PM" and hour != 12:
            hour += 12
        if ampm == "AM" and hour == 12:
            hour = 0

        reminder_datetime = datetime.strptime(f"{date_str} {hour:02d}:{minute:02d}", "%Y-%m-%d %H:%M")

        repeat_type = self.repeat_combo.get().lower()
        days_selected = [day for day, var in self.days_vars.items() if var.get()]

        # validation for repeat reminders
        if repeat_type == "repeat":
            if reminder_datetime < datetime.now():
                messagebox.showwarning(
                    "Input Error",
                    "For repeating reminders, please choose a future time today (or a valid day)."
                )
                return
            if not days_selected:
                messagebox.showwarning("Input Error", "Please select at least one day for repeating reminder!")
                return

        # validation for once reminders
        if repeat_type == "once" and reminder_datetime < datetime.now():
            messagebox.showwarning("Input Error", "The date and time must be in the future!")
            return

        reminder = {
            "title": title,
            "datetime": reminder_datetime.strftime("%Y-%m-%d %H:%M"),
            "repeat_type": repeat_type,
            "days_of_week": days_selected,
            "triggered": False
        }

        if self.edit_index is None:
            self.manager.add_reminder(reminder)
            messagebox.showinfo("Success", "Reminder saved successfully!")
        else:
            self.manager.update_reminder(self.edit_index, reminder)
            messagebox.showinfo("Success", "Reminder updated successfully!")

        self.refresh_list()
        self.clear_form()

    # refresh the reminder list in the table
    def refresh_list(self):
        """Refresh the reminder list in the table."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        now = datetime.now()

        for index, r in enumerate(self.manager.reminders):
            date_str, time_str = r['datetime'].split(" ")
            days = ", ".join(r.get('days_of_week', [])) if r.get('days_of_week') else "-"

            tag = "evenrow" if index % 2 == 0 else "oddrow"

            reminder_time = datetime.strptime(r["datetime"], "%Y-%m-%d %H:%M")
            if r["repeat_type"] == "once" and reminder_time < now:
                tag = "overdue"
            elif r["repeat_type"] == "repeat":
                current_day = now.strftime("%a")
                if current_day in r.get("days_of_week", []) and reminder_time.time() < now.time():
                    tag = "overdue"

            self.tree.insert("", "end",
                             values=(r['title'], date_str, time_str, r['repeat_type'].capitalize(), days),
                             tags=(tag,))

    # reminder checker to check where reminders are due
    def check_reminders(self):
        """Background thread to check for due reminders."""
        while True:
            now = datetime.now()
            for reminder in self.manager.reminders:
                try:
                    reminder_time = datetime.strptime(reminder["datetime"], "%Y-%m-%d %H:%M")
                except ValueError:
                    continue  # skip invalid reminder format

                if reminder["repeat_type"] == "once":
                    if not reminder["triggered"] and now >= reminder_time:
                        self.trigger_alert(reminder)
                        reminder["triggered"] = True
                        self.manager.save_reminders()
                else:
                    current_day = now.strftime("%a")
                    if current_day in reminder["days_of_week"] and now.strftime("%H:%M") == reminder_time.strftime("%H:%M"):
                        self.trigger_alert(reminder)
            time.sleep(30)

    # reminder popup functions
    def trigger_alert(self, reminder):
        """Show popup alert and play sound when reminder is due."""
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)

        popup = tk.Toplevel(self.root)
        popup.title("Reminder Alert!")
        popup.geometry("300x200")
        popup.attributes('-topmost', True)

        tk.Label(popup, text="REMINDER!", font=("Helvetica", 14, "bold"), fg="red").pack(pady=10)
        tk.Label(popup, text=f"Title: {reminder['title']}", font=("Helvetica", 12)).pack(pady=5)
        tk.Label(popup, text=f"Date: {reminder['datetime'].split(' ')[0]}", font=("Helvetica", 10)).pack()
        tk.Label(popup, text=f"Time: {reminder['datetime'].split(' ')[1]}", font=("Helvetica", 10)).pack()
        tk.Label(popup, text=f"Repeat: {reminder['repeat_type'].capitalize()}", font=("Helvetica", 10)).pack()
        tk.Label(popup, text=f"Days: {', '.join(reminder['days_of_week']) if reminder.get('days_of_week') else '-'}",
                 font=("Helvetica", 10)).pack(pady=5)

        tk.Button(popup, text="OK", bg="#27ae60", fg="white", width=10,
                  command=popup.destroy).pack(pady=10)

    # edit , delete, clear  reminder methods
    def edit_reminder(self):
        """Load a reminder into the form for editing."""
        try:
            selected_item = self.tree.selection()[0]
            index = self.tree.index(selected_item)
            reminder = self.manager.reminders[index]

            # Populate form fields
            if reminder['title'] in self.reminder_types:
                self.type_combo.set(reminder['title'])
            else:
                self.type_combo.set("Other")
                self.custom_title_label.grid(row=0, column=8, padx=(20, 0))
                self.title_entry.grid(row=0, column=9, padx=5)
                self.title_entry.delete(0, tk.END)
                self.title_entry.insert(0, reminder['title'])

            reminder_datetime = datetime.strptime(reminder['datetime'], "%Y-%m-%d %H:%M")
            self.date_entry.set_date(reminder_datetime.date())
            self.hour_spin.delete(0, tk.END)
            self.hour_spin.insert(0, reminder_datetime.strftime("%I"))
            self.min_spin.delete(0, tk.END)
            self.min_spin.insert(0, reminder_datetime.strftime("%M"))
            self.ampm_combo.set(reminder_datetime.strftime("%p"))

            self.repeat_combo.set(reminder['repeat_type'].capitalize())
            self.update_repeat_options()
            for day, var in self.days_vars.items():
                var.set(day in reminder.get('days_of_week', []))

            self.edit_index = index
            self.save_btn.config(text="Update Reminder")

        except IndexError:
            messagebox.showwarning("Selection Error", "No reminder selected!")

    def delete_reminder(self):
        """Delete a single reminder after confirmation."""
        try:
            selected_item = self.tree.selection()[0]
            index = self.tree.index(selected_item)

            if messagebox.askyesno("Confirm", "Are you sure you want to delete this reminder?"):
                self.manager.remove_reminder(index)
                self.refresh_list()
        except IndexError:
            messagebox.showwarning("Selection Error", "No reminder selected!")

    def clear_all(self):
        """Delete all reminders after confirmation."""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all reminders?"):
            self.manager.clear_reminders()
            self.refresh_list()
            
    def return_to_main(self):
        self.hasEnded = True
        for widget in self.root.winfo_children():
            widget.destroy()

        # rebuild main menu
        from Main_Menu import Main_Menu
        Main_Menu(self.root)


# Base storage manager class (for inheritance)
class StorageManager:
    """Base class for storage managers."""

    def __init__(self, filename="data.json"):
        self.filename = filename


# reminder manager to handle saving and loading reminders
class ReminderManager(StorageManager):
    """Handles saving, loading, and managing reminders."""

    def __init__(self, filename="reminders.json"):
        super().__init__(filename)  # inherit from StorageManager
        self.reminders = []

    def load_reminders(self):
        """Load reminders from a JSON file if it exists."""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, "r") as file:
                    self.reminders = json.load(file)
            else:
                self.reminders = []
        except (json.JSONDecodeError, OSError) as e:
            messagebox.showerror("File Error", f"Failed to load reminders: {e}")
            self.reminders = []

    def save_reminders(self):
        """Save reminders to a JSON file."""
        try:
            with open(self.filename, "w") as file:
                json.dump(self.reminders, file, indent=4)
        except OSError as e:
            messagebox.showerror("File Error", f"Failed to save reminders: {e}")

    def add_reminder(self, reminder):
        """Add a new reminder and save it."""
        self.reminders.append(reminder)
        self.save_reminders()

    def update_reminder(self, index, reminder):
        """Update an existing reminder and save changes."""
        self.reminders[index] = reminder
        self.save_reminders()

    def remove_reminder(self, index):
        """Remove a reminder by index."""
        del self.reminders[index]
        self.save_reminders()

    def clear_reminders(self):
        """Clear all reminders."""
        self.reminders = []
        self.save_reminders()
        
  