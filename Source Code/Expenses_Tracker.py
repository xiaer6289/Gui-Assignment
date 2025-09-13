import tkinter as tk
import tkinter.messagebox
# from tkinter import *
from tkinter import ttk
import matplotlib.pyplot as plt
import numpy as np
# to import a pie chart
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg 
# to calculate percentage of the pie chart
from matplotlib.figure import Figure
#for the file operation
import os 
# Get the current time and date
from datetime import datetime

class ExpenseBase:
    #this class hold the variable getter and setter 
    def __init__(self):
        self._entry_no = 1 # to keep track of entry number (private)
        self._total_expense = 0.0   # running total (private)
        self._category_totals = {"Food": 0, "Transport": 0, "Shopping": 0, "Bills": 0, "Others": 0} #Initialize category totals
        
    # Getter and setter  (proctected fields)  
    def get_total_expense(self):
        return self._total_expense
    
    def set_total_expense(self,amount):
        if amount >= 0:
            self._total_expense = amount
        else:
            raise ValueError("Total expense cannot be negative.") #error message for negative value
         
    def get_category_totals(self):
        return self._category_totals
    

class Expenses_Tracker(ExpenseBase):
    def __init__(self, root): #constructor
        super().__init__() # Initialize base class
        self.root = root #Saves the root window in an instance variable called self.root.
        self.root.title("Expense Tracker")
        
        # rebuild main menu

        menubar = tk.Menu(self.root)
        self.root.config(menu = menubar)


        exitMenu = tk.Menu(menubar, tearoff = 0)
        exitMenu.add_command(label = "Return", command = self.return_to_main)
        exitMenu.add_command(label = "Quit", command = self.root.destroy)

        menubar.add_cascade(label = "Exit", menu = exitMenu)
        
        #Top   label
        top_frame = tk.Frame(root, bg="gold", height=30)  #bg means the background color
        top_frame.pack(fill="x") #fill all the x axis
        top_frame.pack_propagate(False)  # keep the height
        
        # Month and Year selection
        self.months = [ "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"]
        self.years = [2024, 2025, 2026]  # example range of years
        
        #Get the current year and month
        current_month = datetime.now().month   
        current_year = datetime.now().year     
        
        # Combobox for month
        self.month_combo = ttk.Combobox(top_frame, values=self.months, state="readonly", width=10)
        self.month_combo.set(self.months[current_month - 1])  # default
        self.month_combo.pack(side="left", padx=5)

        # Combobox for year
        self.year_combo = ttk.Combobox(top_frame, values=self.years, state="readonly", width=6)
        self.year_combo.set(str(current_year))  # default
        self.year_combo.pack(side="left", padx=5)

        # Bind selection change to update view
        self.month_combo.bind("<<ComboboxSelected>>", self.change_month)
        self.year_combo.bind("<<ComboboxSelected>>", self.change_month)
                
        self.expense_var = tk.StringVar()
        self.expense_var.set("Expense: RM0.00")

        self.expense_label = tk.Label(top_frame, textvariable=self.expense_var, bg="gold", font=("Arial", 12))
        self.expense_label.pack(side="right", padx=15)
        
        # Main frame
        frame = tk.Frame(root) # put the frame in the middle of the window
        frame.pack(fill="both", expand=True, padx=10, pady=10)  #make the frame expand with the window
        app_width = 600
        app_height = 600
        
        #------The graph part----------------------
        # Store the total amount for each category
       
        # Create a figure for pie chart
        self.fig = Figure(figsize=(3.2, 2.2), dpi=100) #size of the figure (inch) dpi is the size of the pie chart
        self.ax = self.fig.add_subplot(111) # the graph area(1 row, 1 column, first plot)
        self.ax.set_title("Expenses by Category") #title of the graph

        # Embed the figure inside Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=7, column=0, columnspan=1, pady=10) #place it in the row 7 
        
        # Create a frame for category totals (beside pie chart)
        self.totals_frame = tk.Frame(frame)
        self.totals_frame.grid(row=7, column=1, sticky="nw", padx=20, pady=10)

        # Create labels for each category
        self.category_labels = {}
        for category in self._category_totals.keys():
            lbl = tk.Label(self.totals_frame, text=f"{category}: RM0.00", font=("Arial", 10))
            lbl.pack(anchor="w")  # left-align inside the frame
            self.category_labels[category] = lbl
        #--------------------------------------------
        
        # Get screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate position x, y
        x = (screen_width // 2) - (app_width // 2)
        y = (screen_height // 2) - (app_height // 2)

        # Place the window at the center when running the program
        self.root.geometry(f"{app_width}x{app_height}+{x}+{y}")

        self.expenses = []  # A list to store all expenses
       
        #category selection
        categories = ["Food", "Transport", "Shopping", "Bills", "Others"]
        # Input fields
        tk.Label(frame, text="Amount (RM):", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = tk.Entry(frame, width=25)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)
        
        #entry for date and  it will default as current date
        tk.Label(frame, text="Date (YYYY-MM-DD):", font=("Arial", 10, "bold")).grid(row=3, column=0, padx=5, pady=5)
        self.date_entry = tk.Entry(frame, width=25)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))  # default today
        self.date_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # a pull-down list for category (combobox)
        tk.Label(frame, text="Category:", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=5, pady=5)
        self.category_combo = ttk.Combobox(frame, values=categories, state="readonly", width=22)    #pull-down list
        self.category_combo.set("Select Category")  
        self.category_combo.grid(row=1, column=1)
        self.category_combo.bind("<<ComboboxSelected>>", self.check_others)
        
        tk.Label(frame, text="Remarks:", font=("Arial", 10, "bold")).grid(row=2, column=0, padx=5, pady=5)
        self.remarks_entry = tk.Entry(frame, width=25)
        self.remarks_entry.grid(row=2, column=1, padx=5, pady=5)

        # Buttons frame (centered in row 4, spanning 2 columns)
        buttons_frame = tk.Frame(frame)
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=10)

        # Add Expense button
        tk.Button(buttons_frame, text="Add Expense", command=self.add_expense, bg="blue", fg="white",  font=("Arial", 10, "bold")).pack(side="left", padx=20)

        # Delete Expense button
        tk.Button(buttons_frame, text="Delete Expense", command=self.delete_expense, bg="red", fg="white",  font=("Arial", 10, "bold")).pack(side="left", padx=0)

        # Output area
        columns = ("no.", "date", "category", "remarks", "amount")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=6) #Create a table
        #table headings
        self.tree.heading("no.", text="No.") 
        self.tree.heading("date", text="Date") 
        self.tree.heading("category", text="Category")
        self.tree.heading("remarks", text="Remarks")
        self.tree.heading("amount", text="Amount (RM)")
        self.tree.grid(row=6, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")
      
        #adjust the size/length of the  columns
        self.tree.column("no.", width=50, anchor="center")
        self.tree.column("date", width=100, anchor="center")
        self.tree.column("category", width=120, anchor="center")
        self.tree.column("remarks", width=200, anchor="w")   # left align text(w)
        self.tree.column("amount", width=100, anchor="w")    # right align numbers(e)
        self.tree.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.load_expenses()  # Load the data from the txt file 
        self.update_chart()
    
        
    #Function to add an expense
    def add_expense(self):
        # Get date from entry box
        row_no = len(self.tree.get_children()) + 1
        date_text = self.date_entry.get().strip()
        try:
            # Validate date format
            datetime.strptime(date_text, "%Y-%m-%d")
        except ValueError:
            #if not match the date format , show error message
            tk.messagebox.showerror("Invalid input", "Please enter date in YYYY-MM-DD format.")
            return
        date = date_text
        
        try:
            amount = float(self.amount_entry.get().strip())   # convert to number
            if amount <= 0:
                tk.messagebox.showerror("Invalid input","Amount must be greater than 0.")
        except ValueError:
            tk.messagebox.showerror("Invalid input","Please enter a valid number for amount.")
            return
        
        category = self.category_combo.get().strip()
        #force user to select a category
        match category:
            #if user didnt select any category
            case "Select Category" | "":
                tk.messagebox.showerror("Invalid input","Please select a category.")
                return
            case _:
                pass  # continue normally
        
        #Set the first letter to uppercase
        remarks = self.remarks_entry.get().capitalize()
        
         # Row number = current table length + 1 
        row_no = len(self.tree.get_children()) + 1
        
         # Check if expense belongs to current month/year
        year, month, day = map(int, date.split("-"))
        current_year = int(self.year_combo.get())
        current_month = self.months.index(self.month_combo.get()) + 1

        if year == current_year and month == current_month:
            # Insert into current table
            self.tree.insert("", "end", values=(row_no, date, category, remarks, amount))
        
         # Update running total
        self.set_total_expense(self.get_total_expense() + amount)
        self.expense_var.set(f"Expense: RM{self.get_total_expense():.2f}")
        
        # Update category total
        year, month, day = map(int, date.split("-"))
        current_year = int(self.year_combo.get())
        current_month = self.months.index(self.month_combo.get()) + 1

        if year == current_year and month == current_month:
            # only update the current page’s chart
            if category not in self._category_totals:
                self._category_totals[category] = 0
            self._category_totals[category] += amount

        # Update the pie chart
        self.update_chart()
         
        #Add the records of expenses into a text file
        file_path = "expenses.txt"
        with open(file_path, "a") as f:   #using "with" so the file will close automatically
            f.write(f"{date},{category},{remarks},{amount:.2f}\n")
    
        """Clear the entry fields after adding
           clear the data from the start line of the entry until to the end
        """
        ##Auto-switch month view based on entered date
        year, month, _ = date.split("-")
        year = int(year) #convert the string to integer
        month = int(month) #convert the string to integer

        # Update comboboxes
        self.month_combo.set(self.months[month - 1])   #minus 1 because the month start with index 0
        self.year_combo.set(str(year))

        # Refresh correct month view
        self.change_month()
        
        #Clear all the input after adding an expense
        self.amount_entry.delete(0, tk.END)
        self.category_combo.set("Select Category")
        self.remarks_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
    #set only "Others " category to be editable
    def check_others(self, event):
        selected = self.category_combo.get()
        if selected == "Others":
            self.category_combo.configure(state="normal")  # allow typing
        else:
            self.category_combo.configure(state="readonly")  # cannot edit the selection box 

    # Function to update the pie chart
    def update_chart(self):
        # Clear the old chart
        self.ax.clear()
        # Get the current total category amount from the list
        totals = self.get_category_totals()
        # If the total amount is more that 0 ,then inlcude it in the pie chart
        if sum(self.get_category_totals().values()) > 0:
            """only take the category with data/value ,if no ignored the category
               label mean the cegory name ,eg "Food" , "Transport"
               value mean the amount of money spent in that category
            """
            labels = [cat for cat, val in self.get_category_totals().items() if val > 0]
            values = [val for val in self.get_category_totals().values() if val > 0]
            
            # Draw the pie chart starting from 90 degreee
            self.ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
            self.ax.set_title("Expenses by Category")
        else:
            # Draw an empty pie (white circle) , if there is no any data for each categpry
            self.ax.pie([1], labels=["Empty"], colors=["lightgrey"])
            self.ax.set_title("Expenses by Category")
            
        for widget in self.totals_frame.winfo_children():
            # delete all the old labels in the frame
            widget.destroy()
            
         # update the category totals labels   
        for category, amount in totals.items():
            lbl = tk.Label(self.totals_frame, text=f"{category}: RM{amount:.2f}", font=("Arial", 10))
            lbl.pack(anchor="w") #Align to the left
                
        # Redraw chart
        self.canvas.draw()
     
     #functon to load the expenses for everytime reopen the program   
    def load_expenses(self):
        if not os.path.exists("expenses.txt"):   #if the file is not exist
            return  # no file yet, skip
        
        #read the file and load data into the table
        with open("expenses.txt", "r") as f:
            line = f.readline()
            while line:  # keep looping until no more lines
                if line.strip():
                    date, category, remarks, amount = line.strip().split(",")
                    amount = float(amount)
                    self.expenses.append({
                        "date": date,
                        "category": category,
                        "remarks": remarks,
                        "amount": amount
                    })
                line = f.readline()  # move to next line


        # After loading, display the current month
        self.change_month()
            
    def change_month(self, event=None):
        #get the year and month that user selected in the combobox
        selected_month = self.month_combo.get()
        selected_year = self.year_combo.get()
            
        # Clear the current table before load a new data
        for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Reset totals
        self.set_total_expense(0)
        self._category_totals = { "Food":0, "Transport":0, "Shopping":0, "Bills":0, "Others":0 }

        # Load expenses from file filtered by month/year
        if not os.path.exists("expenses.txt"):
            return
            
        # Loop the data of each line and skip the empty line
        row_no = 1 
        with open("expenses.txt", "r") as f:
            for line in f:
                if not line.strip(): 
                    continue
                date, category, remarks, amount = line.strip().split(",")
                amount = float(amount)
                year, month, day = map(int, date.split("-"))
                    
                """ Check if this expense matches selected month/year
                    Convert the month name in the array to index number
                    eg ."September" -->  index=8 +1 = 9
                """
                if month == self.months.index(selected_month)+1 and year == int(selected_year):
                    self.tree.insert("", "end", values=(row_no, date, category, remarks, amount))
                    row_no += 1
                    self.set_total_expense(self.get_total_expense() + amount)
                    if category not in self._category_totals:
                        self._category_totals[category] = 0
                    self._category_totals[category] += amount

        self.expense_var.set(f"Expense: RM{self.get_total_expense():.2f}")
        self.update_chart()  
        
        # Delete the record formthe table 
    def delete_expense(self):
        selected_item = self.tree.selection()  # get selected row(s) from Treeview
        
        # if there is no record left in the table , show the error message
        condition = (
            "empty_table" if not self.tree.get_children()
            else "no_selection" if not selected_item
            else "ok"
    )

        match condition:
            # if the table is empty
            case "empty_table":
                tk.messagebox.showinfo("No Records", "There are no records to delete.")
                return
            # if user didnt select anythings
            case "no_selection":
                tk.messagebox.showerror("Error", "Please select a record to delete.")
                return
            # if both conditions are not occur
            case "ok":
                pass  # continue with delete logic

         # Ask user either they confirm to delete
        confirm = tk.messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this expense?")
        if not confirm:
            return

            # Get values from selected row
        values = self.tree.item(selected_item, "values")
        date, category, remarks, amount = values[1], values[2], values[3], float(values[4])

        # Remove from Treeview
        self.tree.delete(selected_item)

        # Remove from expenses.txt (rewrite file without this line)
        with open("expenses.txt", "r") as f:
            lines = f.readlines()

        with open("expenses.txt", "w") as f:
            for line in lines:
                if line.strip() != f"{date},{category},{remarks},{amount:.2f}":
                    f.write(line)

            # Update totals
        self.set_total_expense(self.get_total_expense() - amount)
        if category in self._category_totals:
            self._category_totals[category] -= amount
            if self._category_totals[category] < 0:
                self._category_totals[category] = 0

        self.expense_var.set(f"Expense: RM{self.get_total_expense():.2f}")
        self.update_chart() 
              

    def return_to_main(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # rebuild main menu
        from Main_Menu import Main_Menu
        Main_Menu(self.root)
    

