import csv
import os
import json
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import sys
import PyQt5 # another framework that might work better once everything is functional

ROSTER_DATA_FILE = "table_data.csv"  # File to save and load table data
MANAGER_BONUS_FILE = ""
BONUS_EMPLOYEE_DATA = "bonus_employee_data.json"
HR_DATA = "hr_data.json"


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Luchetti's App")
        self.geometry("800x500")

        self.pages = {}

        # Add all pages
        main_page = MainPage(self)
        self.add_page("Main", main_page)
        self.add_page("Page1", ManagerBonus(self))
        self.add_page("Page2", EmployeeRoster(self))
        self.add_page("Page3", EmployeeBonuses(self))
        self.add_page("Page4", HR(self))
        self.add_page("Page5", FarmingBonus(self))
        self.add_page("Page6", Fund(self))
        self.add_page("Page7", LucidEats(self))
        self.add_page("Page8", Training(self))
        self.add_page("Page9", IngredientsBought(self))
        self.add_page("Page10", CheatSheet(self))

        # Show main page first
        self.show_page("Main")

    def add_page(self, name, page):
        """Add a new page to the app."""
        self.pages[name] = page
        page.grid(row=0, column=0, sticky="nsew")

    def show_page(self, name):
        """Show a specific page by name."""
        page = self.pages[name]
        page.tkraise()


class MainPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        content = tk.Frame(self)
        content.grid(row=0, column=0)

        label = tk.Label(content, text="Main Page", font=("Arial", 18))
        label.pack(pady=20)
    #management
        ttk.Button(content, text="Manager Bonuses", command=lambda: parent.show_page("Page1")).pack(pady=5)
        ttk.Button(content, text="Employee Roster", command=lambda: parent.show_page("Page2")).pack(pady=5)
        ttk.Button(content, text="Bonuses", command=lambda: parent.show_page("Page3")).pack(pady=5)
        ttk.Button(content, text="HR", command=lambda: parent.show_page("Page4")).pack(pady=5)
        ttk.Button(content, text="Farming Bonus calc.", command=lambda: parent.show_page("Page5")).pack(pady=5)
        ttk.Button(content, text="Fund", command=lambda: parent.show_page("Page6")).pack(pady=5)
    #shiftlead
        ttk.Button(content, text="Lucid Eats", command=lambda: parent.show_page("Page7")).pack(pady=5)
        ttk.Button(content, text="Training", command=lambda: parent.show_page("Page8")).pack(pady=5)
    #employee
        ttk.Button(content, text="Ingredience Bought", command=lambda: parent.show_page("Page9")).pack(pady=5)
        ttk.Button(content, text="Cheatsheet", command=lambda: parent.show_page("Page10")).pack(pady=5)


class ManagerBonus(tk.Frame):
    DATA_FILE = "bonus_data.json"
    TEMPLATE = [
        ["Myles Cherry", "", "$3,000", "", "", "61709", "", ""],
        ["Tommy Kade", "", "$3,000", "", "", "836", "", ""],
        ["Carissa SL-Cherry", "", "$3,000", "", "", "64695", "", ""],
        ["Luna Kade", "", "$2,000", "", "", "44157", "", ""],
        ["BigKing HMDollas", "", "$2,000", "", "", "98814", "", ""],
        ["Blake Cherry", "", "$2,000", "", "", "78694", "", ""],
        ["Chip Monck", "", "$2,000", "", "", "8349", "", ""],
        ["Ling Cherry", "", "$2,000", "", "", "83654", "", ""],
        ["Jack Slater", "", "$2,000", "", "", "90464", "", ""],
        ["Bart", "", "$2,000", "", "", "106531", "", ""],
        ["Tommy Longsocks", "", "$2,000", "", "", "106783", "", ""]
    ]
    
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        content = tk.Frame(self)
        content.grid(row=0, column=0, sticky="nsew")

        self.start_date = datetime.today()
        self.end_date = self.start_date + timedelta(days=6)
        self.date_label = tk.Label(content, text=self.get_date_range(), font=("Arial", 14))
        self.date_label.pack(pady=5)

        label = tk.Label(content, text="Manager Bonuses", font=("Arial", 18))
        label.pack(pady=10)

        self.COLUMN_NAMES = ["Name", "Time Clocked (Hours)", "Tick Bonus Rate", "Bonus Amount", "Paid", "PayPal", "LOA", "Paid By"]

        self.table = ttk.Treeview(content, columns=self.COLUMN_NAMES, show="headings", height=10)
        self.table.pack(expand=True, fill="both")

        for name in self.COLUMN_NAMES:
            self.table.heading(name, text=name)
            self.table.column(name, width=120)

        self.history_data = []  # Stores past weeks' data

        self.load_data()

        self.table.bind("<Double-1>", self.edit_cell)
        self.table.bind("<Delete>", self.delete_selected_rows)
        self.table.bind("<BackSpace>", self.delete_selected_rows)
        
        ttk.Button(content, text="New Week", command=self.new_week).pack(pady=5)
        ttk.Button(content, text="History", command=self.show_history).pack(pady=5)
        ttk.Button(content, text="Recalculate", command=self.recalculate).pack(pady=5)
        ttk.Button(content, text="Back to Main Page", command=lambda: parent.show_page("Main")).pack(pady=5)
    
    

    def get_date_range(self):
        return f"Week: {self.start_date.strftime('%m/%d/%Y')} - {self.end_date.strftime('%m/%d/%Y')}"

    def new_week(self):
        week_data = {
            "date_range": self.get_date_range(),
            "entries": [self.table.item(item, "values") for item in self.table.get_children()]
        }
        self.history_data.append(week_data)
        self.save_data()

        self.start_date += timedelta(weeks=1)
        self.end_date += timedelta(weeks=1)
        self.date_label.config(text=self.get_date_range())
        
        self.table.delete(*self.table.get_children())
        for row in self.TEMPLATE:
            self.table.insert("", "end", values=row)
        
        self.save_data()
    
    def show_history(self):
        history_window = tk.Toplevel(self)
        history_window.title("Bonus History")
        history_window.geometry("700x500")

        canvas = tk.Canvas(history_window)
        scrollbar = ttk.Scrollbar(history_window, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas)
        
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for week in self.history_data:
            tk.Label(frame, text=week["date_range"], font=("Arial", 14, "bold")).pack(pady=5)
            history_table = ttk.Treeview(frame, columns=self.COLUMN_NAMES, show="headings", height=5)
            history_table.pack(fill="both", padx=10, pady=5)

            for name in self.COLUMN_NAMES:
                history_table.heading(name, text=name)
                history_table.column(name, width=120)

            for row in week["entries"]:
                history_table.insert("", "end", values=row)
    
    def recalculate(self):
        for item in self.table.get_children():
            values = list(self.table.item(item, "values"))
            try:
                hours = float(values[1]) if values[1] else 0
                rate = float(values[2].replace("$", "").replace(",", "")) if values[2] else 0
                values[3] = f"${rate * 4 * hours:.2f}" if hours >= 10 else "$0.00"
            except ValueError:
                values[3] = "$0.00"
            self.table.item(item, values=values)
        self.save_data()
    
    def save_data(self):
        data = {
            "current_week": {
                "start_date": self.start_date.strftime('%Y-%m-%d'),
                "end_date": self.end_date.strftime('%Y-%m-%d'),
                "entries": [self.table.item(item, "values") for item in self.table.get_children()]
            },
            "history": self.history_data
        }
        with open(self.DATA_FILE, "w") as f:
            json.dump(data, f)
    
    def load_data(self):
        if os.path.exists(self.DATA_FILE):
            with open(self.DATA_FILE, "r") as f:
                data = json.load(f)
            
            self.start_date = datetime.strptime(data["current_week"]["start_date"], '%Y-%m-%d')
            self.end_date = datetime.strptime(data["current_week"]["end_date"], '%Y-%m-%d')
            self.date_label.config(text=self.get_date_range())
            self.history_data = data.get("history", [])
            
            for row in data["current_week"]["entries"]:
                self.table.insert("", "end", values=row)
        else:
            for row in self.TEMPLATE:
                self.table.insert("", "end", values=row)

    def edit_cell(self, event):
        selected_item = self.table.selection()
        if not selected_item:
            return

        item = selected_item[0]
        col = self.table.identify_column(event.x)  # Get the column index (e.g., "#2" for second column)
        col_index = int(col[1:]) - 1  # Convert to zero-based index

        # Get cell value
        values = list(self.table.item(item, "values"))
        old_value = values[col_index]

        # Create an entry widget at the clicked position
        entry = tk.Entry(self.table)
        entry.insert(0, old_value)
        entry.focus()

        # Get cell coordinates
        bbox = self.table.bbox(item, col_index)
        entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])

        def on_enter(event):
            values[col_index] = entry.get()
            self.table.item(item, values=values)
            entry.destroy()
            self.recalculate()  # Update bonus calculation after editing

        entry.bind("<Return>", on_enter)
        entry.bind("<FocusOut>", lambda e: entry.destroy())  # Destroy if focus is lost

    def delete_selected_rows(self, event):
        selected_items = self.table.selection()
        for item in selected_items:
            self.table.delete(item)
        self.save_data()


class EmployeeRoster(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        content = tk.Frame(self)
        content.pack(expand=True, fill="both")

        label = tk.Label(content, text="Editable Excel-Type Sheet", font=("Arial", 18))
        label.pack(pady=10)

        self.COLUMN_NAMES = [
            "Position", "Name", "UID", "Phone", "Activity",
            "Date Hired", "Hired by", "Crew", "Training", "Notes"
        ]

        self.table = ttk.Treeview(content, columns=self.COLUMN_NAMES, show="headings", height=10)
        self.table.pack(expand=True, fill="both")

        for name in self.COLUMN_NAMES:
            self.table.heading(name, text=name)
            self.table.column(name, width=100)

        self.load_data()

        # Bind actions
        self.table.bind("<Double-1>", self.edit_cell)
        self.table.bind("<Delete>", self.delete_selected_rows)
        self.table.bind("<BackSpace>", self.delete_selected_rows)

        ttk.Button(content, text="Add Employee", command=self.open_add_employee_popup).pack(pady=5)
        ttk.Button(content, text="Back to Main Page", command=lambda: parent.show_page("Main")).pack(pady=5)

    def open_add_employee_popup(self):
        """Opens a popup window for adding a new employee."""
        popup = tk.Toplevel(self)
        popup.title("Add Employee")
        popup.geometry("400x400")

        entries = {}

        for i, name in enumerate(self.COLUMN_NAMES):
            tk.Label(popup, text=name).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = tk.Entry(popup)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            entries[name] = entry

        def submit():
            new_employee = [entries[name].get() for name in self.COLUMN_NAMES]
            self.table.insert("", "end", values=new_employee)
            self.save_data()
            popup.destroy()

        ttk.Button(popup, text="Add Employee", command=submit).grid(row=len(self.COLUMN_NAMES), column=0, columnspan=2, pady=10)

    def delete_selected_rows(self, event=None):
        """Deletes selected rows from the table."""
        selected_items = self.table.selection()
        if not selected_items:
            return

        for item in selected_items:
            self.table.delete(item)

        self.save_data()

    def edit_cell(self, event):
        """Enable cell editing for all columns, with dropdowns for specific ones."""
        selected_item = self.table.focus()
        if not selected_item:
            return

        col = self.table.identify_column(event.x)
        row = self.table.identify_row(event.y)
        if not row:
            return

        column_index = int(col[1:]) - 1
        row_values = list(self.table.item(selected_item, "values"))

        while len(row_values) < 10:
            row_values.append("")

        DROPDOWN_OPTIONS = {
            0: ["Owner", "Director", "Executive", "Senior Manager", "Manager", "Assistant Manager", "Advisor", "Shift-lead", "Core", "Crew", "Probationary", "Retired", "DNH"],
            5: ["Active", "LOA"],
            8: ["Completed", "Partial"],
        }

        x, y, width, height = self.table.bbox(selected_item, col)

        if column_index in DROPDOWN_OPTIONS:
            combobox = ttk.Combobox(self, values=DROPDOWN_OPTIONS[column_index], state="readonly")
            combobox.set(row_values[column_index])
            combobox.place(x=x, y=y + height, width=width)

            def save_dropdown(event=None):
                row_values[column_index] = combobox.get()
                self.table.item(selected_item, values=row_values)
                combobox.destroy()
                self.save_data()

            combobox.bind("<<ComboboxSelected>>", save_dropdown)
            combobox.focus_set()

        else:
            entry = tk.Entry(self)
            entry.insert(0, row_values[column_index])
            entry.place(x=x, y=y + height, width=width)

            def save_edit(event=None):
                row_values[column_index] = entry.get()
                self.table.item(selected_item, values=row_values)
                entry.destroy()
                self.save_data()

            entry.bind("<Return>", save_edit)
            entry.focus_set()

    def load_data(self):
        """Load table data from a CSV file."""
        if os.path.exists(ROSTER_DATA_FILE):
            with open(ROSTER_DATA_FILE, "r", newline="") as file:
                reader = csv.reader(file)
                for row in reader:
                    while len(row) < 10:
                        row.append("")
                    self.table.insert("", "end", values=row)

    def save_data(self):
        """Save table data to a CSV file."""
        rows = []
        for item in self.table.get_children():
            row_values = list(self.table.item(item, "values"))
            while len(row_values) < 10:
                row_values.append("")
            rows.append(row_values)

        with open(ROSTER_DATA_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(rows)


class EmployeeBonuses(tk.Frame):    

    TEMPLATE = []
    BONUS_EMPLOYEE_DATA = "employee_bonus_data.json"

    def __init__(self, parent):
        super().__init__(parent)

        

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        content = tk.Frame(self)
        content.grid(row=0, column=0, sticky="nsew")

        label = tk.Label(content, text="Bonuses", font=("Arial", 18))
        label.pack(pady=10)

        self.start_date = datetime.today()
        self.end_date = self.start_date + timedelta(days=6)
        self.date_label = tk.Label(content, text=self.get_date_range(), font=("Arial", 14))
        self.date_label.pack(pady=5)
        self.COLUMN_NAMES = ["Name", "UID", "Reason", "Bonus Amount", "Paid", "Paid By"]


        self.table = ttk.Treeview(content, columns=self.COLUMN_NAMES, show="headings", height=10)
        self.table.pack(expand=True, fill="both")

        for name in self.COLUMN_NAMES:
            self.table.heading(name, text=name)
            self.table.column(name, width=120)

        self.history_data = []  # Stores past weeks' data

        self.load_data()

        self.table.bind("<Double-1>", self.edit_cell)
        self.table.bind("<Delete>", self.delete_selected_rows)
        self.table.bind("<BackSpace>", self.delete_selected_rows)

        ttk.Button(content, text="Add Bonuses", command=self.add_bonus).pack(pady=5)
        ttk.Button(content, text="New Week", command=self.new_week).pack(pady=5)
        ttk.Button(content, text="History", command=self.show_history).pack(pady=5)
        ttk.Button(content, text="Back to Main Page", command=lambda: parent.show_page("Main")).pack(pady=5)

    def get_date_range(self):
        return f"Week: {self.start_date.strftime('%m/%d/%Y')} - {self.end_date.strftime('%m/%d/%Y')}"


    def add_bonus(self):
        popup = tk.Toplevel(self)
        popup.title("Add Bonus")
        popup.geometry("400x400")

        entries = {}

        for i, name in enumerate(self.COLUMN_NAMES):
            tk.Label(popup, text=name).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = tk.Entry(popup)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            entries[name] = entry

        def submit():
            new_bonus = [entries[name].get() for name in self.COLUMN_NAMES]
            self.table.insert("", "end", values=new_bonus)
            self.save_data()
            popup.destroy()

        ttk.Button(popup, text="Add Bonus", command=submit).grid(row=len(self.COLUMN_NAMES), column=0, columnspan=2, pady=10)

    def new_week(self):
        week_data = {
            "date_range": self.get_date_range(),
            "entries": [self.table.item(item, "values") for item in self.table.get_children()]
        }
        self.history_data.append(week_data)
        self.save_data()

        self.start_date += timedelta(weeks=1)
        self.end_date += timedelta(weeks=1)
        self.date_label.config(text=self.get_date_range())
        
        self.table.delete(*self.table.get_children())
        for row in self.TEMPLATE:
            self.table.insert("", "end", values=row)
        
        self.save_data()


    def show_history(self):
        history_window = tk.Toplevel(self)
        history_window.title("Bonus History")
        history_window.geometry("700x500")

        canvas = tk.Canvas(history_window)
        scrollbar = ttk.Scrollbar(history_window, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas)
        
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for week in self.history_data:
            tk.Label(frame, text=week["date_range"], font=("Arial", 14, "bold")).pack(pady=5)
            history_table = ttk.Treeview(frame, columns=self.COLUMN_NAMES, show="headings", height=5)
            history_table.pack(fill="both", padx=10, pady=5)

            for name in self.COLUMN_NAMES:
                history_table.heading(name, text=name)
                history_table.column(name, width=120)

            for row in week["entries"]:
                history_table.insert("", "end", values=row)



    def edit_cell(self, event):
        """Enable cell editing for all columns, with dropdowns for specific ones."""
        selected_item = self.table.focus()
        if not selected_item:
            return

        col = self.table.identify_column(event.x)
        row = self.table.identify_row(event.y)
        if not row:
            return

        column_index = int(col[1:]) - 1
        row_values = list(self.table.item(selected_item, "values"))

        while len(row_values) < 10:
            row_values.append("")

        DROPDOWN_OPTIONS = {
            4: ["Yes", "No"],
            6: ["Active", "LOA"],
            7: ["Dexter Cherry", "Myles Cherry", "Tommy Kade", "Carissa SL-Cherry", "Luna Kade", "BigKing HMDollas", "Blake Cherry", "Chip Monck", "Ling Cherry", "Jack Slater", "Bart", "Tommy Longsocks"]
        }

        x, y, width, height = self.table.bbox(selected_item, col)

        if column_index in DROPDOWN_OPTIONS:
            combobox = ttk.Combobox(self, values=DROPDOWN_OPTIONS[column_index], state="readonly")
            combobox.set(row_values[column_index])
            combobox.place(x=x, y=y + height, width=width)

            def save_dropdown(event=None):
                row_values[column_index] = combobox.get()
                self.table.item(selected_item, values=row_values)
                combobox.destroy()
                self.save_data()

            combobox.bind("<<ComboboxSelected>>", save_dropdown)
            combobox.focus_set()

        else:
            entry = tk.Entry(self)
            entry.insert(0, row_values[column_index])
            entry.place(x=x, y=y + height, width=width)

            def save_edit(event=None):
                row_values[column_index] = entry.get()
                self.table.item(selected_item, values=row_values)
                entry.destroy()
                self.save_data()

            entry.bind("<Return>", save_edit)
            entry.focus_set()


    


    def recalculate(self):
        for item in self.table.get_children():
            values = list(self.table.item(item, "values"))
            try:
                hours = float(values[1]) if values[1] else 0
                rate = float(values[2].replace("$", "").replace(",", "")) if values[2] else 0
                values[3] = f"${rate * 4 * hours:.2f}" if hours >= 10 else "$0.00"
            except ValueError:
                values[3] = "$0.00"
            self.table.item(item, values=values)
        self.save_data()



    def delete_selected_rows(self, event=None):
        """Deletes selected rows from the table."""
        selected_items = self.table.selection()
        if not selected_items:
            return

        for item in selected_items:
            self.table.delete(item)

        self.save_data()


    def save_data(self):
        data = {
            "current_week": {
                "start_date": self.start_date.strftime('%Y-%m-%d'),
                "end_date": self.end_date.strftime('%Y-%m-%d'),
                "entries": [self.table.item(item, "values") for item in self.table.get_children()]
            },
            "history": self.history_data
        }
        with open(self.BONUS_EMPLOYEE_DATA, "w") as f:
            json.dump(data, f)
    
    def load_data(self):
        if os.path.exists(self.BONUS_EMPLOYEE_DATA):
            with open(self.BONUS_EMPLOYEE_DATA, "r") as f:
                data = json.load(f)
            
            self.start_date = datetime.strptime(data["current_week"]["start_date"], '%Y-%m-%d')
            self.end_date = datetime.strptime(data["current_week"]["end_date"], '%Y-%m-%d')
            self.date_label.config(text=self.get_date_range())
            self.history_data = data.get("history", [])
            
            for row in data["current_week"]["entries"]:
                self.table.insert("", "end", values=row)
        else:
            for row in self.TEMPLATE:
                self.table.insert("", "end", values=row)


class HR(tk.Frame):    

    HR_DATA = "hr_data.json"
    TEMPLATE = []

    def __init__(self, parent):
        super().__init__(parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        content = tk.Frame(self)
        content.grid(row=0, column=0, sticky="nsew")

        label = tk.Label(content, text="HR", font=("Arial", 18))
        label.pack(pady=10)

        self.start_date = datetime.today()
        self.end_date = self.start_date + timedelta(days=6)
        self.date_label = tk.Label(content, text=self.get_date_range(), font=("Arial", 14))
        self.date_label.pack(pady=5)
        self.COLUMN_NAMES = ["Action", "Name", "Shop", "Farming", "Delivery"]


        self.table = ttk.Treeview(content, columns=self.COLUMN_NAMES, show="headings", height=10)
        self.table.pack(expand=True, fill="both")

        for name in self.COLUMN_NAMES:
            self.table.heading(name, text=name)
            self.table.column(name, width=120)

        self.history_data = []  # Stores past weeks' data

        self.load_data()

        self.table.bind("<Double-1>", self.edit_cell)
        self.table.bind("<Delete>", self.delete_selected_rows)
        self.table.bind("<BackSpace>", self.delete_selected_rows)

        ttk.Button(content, text="Insert Data", command=self.add_bonus).pack(pady=5)
        ttk.Button(content, text="New Week", command=self.new_week).pack(pady=5)
        ttk.Button(content, text="History", command=self.show_history).pack(pady=5)
        ttk.Button(content, text="Back to Main Page", command=lambda: parent.show_page("Main")).pack(pady=5)

    def get_date_range(self):
        return f"Week: {self.start_date.strftime('%m/%d/%Y')} - {self.end_date.strftime('%m/%d/%Y')}"


    def add_bonus(self):
        popup = tk.Toplevel(self)
        popup.title("Add Bonus")
        popup.geometry("400x400")

        entries = {}

        for i, name in enumerate(self.COLUMN_NAMES):
            tk.Label(popup, text=name).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = tk.Entry(popup)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            entries[name] = entry

        def submit():
            new_bonus = [entries[name].get() for name in self.COLUMN_NAMES]
            self.table.insert("", "end", values=new_bonus)
            self.save_data()
            popup.destroy()

        ttk.Button(popup, text="Add Bonus", command=submit).grid(row=len(self.COLUMN_NAMES), column=0, columnspan=2, pady=10)

    def new_week(self):
        week_data = {
            "date_range": self.get_date_range(),
            "entries": [self.table.item(item, "values") for item in self.table.get_children()]
        }
        self.history_data.append(week_data)
        self.save_data()

        self.start_date += timedelta(weeks=1)
        self.end_date += timedelta(weeks=1)
        self.date_label.config(text=self.get_date_range())
        
        self.table.delete(*self.table.get_children())
        for row in self.TEMPLATE:
            self.table.insert("", "end", values=row)
        
        self.save_data()


    def show_history(self):
        history_window = tk.Toplevel(self)
        history_window.title("Bonus History")
        history_window.geometry("700x500")

        canvas = tk.Canvas(history_window)
        scrollbar = ttk.Scrollbar(history_window, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas)
        
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for week in self.history_data:
            tk.Label(frame, text=week["date_range"], font=("Arial", 14, "bold")).pack(pady=5)
            history_table = ttk.Treeview(frame, columns=self.COLUMN_NAMES, show="headings", height=5)
            history_table.pack(fill="both", padx=10, pady=5)

            for name in self.COLUMN_NAMES:
                history_table.heading(name, text=name)
                history_table.column(name, width=120)

            for row in week["entries"]:
                history_table.insert("", "end", values=row)



    def edit_cell(self, event):
        """Enable cell editing for all columns, with dropdowns for specific ones."""
        selected_item = self.table.focus()
        if not selected_item:
            return

        col = self.table.identify_column(event.x)
        row = self.table.identify_row(event.y)
        if not row:
            return

        column_index = int(col[1:]) - 1
        row_values = list(self.table.item(selected_item, "values"))

        while len(row_values) < 10:
            row_values.append("")

        DROPDOWN_OPTIONS = {
            0: ["Promote", "Demote", "Fire", "Retire", "LOA"],
        }

        x, y, width, height = self.table.bbox(selected_item, col)

        if column_index in DROPDOWN_OPTIONS:
            combobox = ttk.Combobox(self, values=DROPDOWN_OPTIONS[column_index], state="readonly")
            combobox.set(row_values[column_index])
            combobox.place(x=x, y=y + height, width=width)

            def save_dropdown(event=None):
                row_values[column_index] = combobox.get()
                self.table.item(selected_item, values=row_values)
                combobox.destroy()
                self.save_data()

            combobox.bind("<<ComboboxSelected>>", save_dropdown)
            combobox.focus_set()

        else:
            entry = tk.Entry(self)
            entry.insert(0, row_values[column_index])
            entry.place(x=x, y=y + height, width=width)

            def save_edit(event=None):
                row_values[column_index] = entry.get()
                self.table.item(selected_item, values=row_values)
                entry.destroy()
                self.save_data()

            entry.bind("<Return>", save_edit)
            entry.focus_set()



    def delete_selected_rows(self, event=None):
        """Deletes selected rows from the table."""
        selected_items = self.table.selection()
        if not selected_items:
            return

        for item in selected_items:
            self.table.delete(item)

        self.save_data()


    def save_data(self):
        data = {
            "current_week": {
                "start_date": self.start_date.strftime('%Y-%m-%d'),
                "end_date": self.end_date.strftime('%Y-%m-%d'),
                "entries": [self.table.item(item, "values") for item in self.table.get_children()]
            },
            "history": self.history_data
        }
        with open(self.HR_DATA, "w") as f:
            json.dump(data, f)

    def load_data(self):
        if os.path.exists(self.HR_DATA):
            with open(self.HR_DATA, "r") as f:
                data = json.load(f)
            
            self.start_date = datetime.strptime(data["current_week"]["start_date"], '%Y-%m-%d')
            self.end_date = datetime.strptime(data["current_week"]["end_date"], '%Y-%m-%d')
            self.date_label.config(text=self.get_date_range())
            self.history_data = data.get("history", [])
            
            for row in data["current_week"]["entries"]:
                self.table.insert("", "end", values=row)
        else:
            for row in self.TEMPLATE:
                self.table.insert("", "end", values=row)


class FarmingBonus(tk.Frame):
    TEMPLATE = []
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        content = tk.Frame(self)
        content.grid(row=0, column=0, sticky="nsew")

        label = tk.Label(content, text="Farming Bonuses", font=("Arial", 18))
        label.pack(pady=10)

        self.start_date = datetime.today()
        self.end_date = self.start_date + timedelta(days=6)
        self.date_label = tk.Label(content, text=self.get_date_range(), font=("Arial", 14))
        self.date_label.pack(pady=5)

        self.COLUMN_NAMES = ["Name", "UID", "Reason", "Bonus Amount", "Paid", "Paid By"]
        self.DATA_COLUMN_NAMES = ["Date", "Name", "UID", "tomatoes", "mushrooms", "lettuce", "meat"]

        self.table = ttk.Treeview(content, columns=self.COLUMN_NAMES, show="headings", height=10)
        self.table.pack(expand=True, fill="both")

        for name in self.COLUMN_NAMES:
            self.table.heading(name, text=name)
            self.table.column(name, width=120)

        self.history_data = []  # Stores past weeks' data

        self.load_data()

        self.table.bind("<Double-1>", self.edit_cell)
        self.table.bind("<Delete>", self.delete_selected_rows)
        self.table.bind("<BackSpace>", self.delete_selected_rows)

        ttk.Button(content, text="Insert data", command=self.insert_data).pack(pady=5)
        ttk.Button(content, text="New Week", command=self.new_week).pack(pady=5)
        ttk.Button(content, text="History", command=self.show_history).pack(pady=5)
        ttk.Button(content, text="Back to Main Page", command=lambda: parent.show_page("Main")).pack(pady=5)

    def get_date_range(self):
        return f"Week: {self.start_date.strftime('%m/%d/%Y')} - {self.end_date.strftime('%m/%d/%Y')}"
    
    def insert_data(self):
        popup = tk.Toplevel(self)
        popup.title("Insert data")
        popup.geometry("400x400")

        entries = {}
        data = entries

        for i, name in enumerate(self.DATA_COLUMN_NAMES):
            tk.Label(popup, text=name).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = tk.Entry(popup)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            entries[name] = entry

        def submit():
            new_data = [entries[name].get() for name in self.DATA_COLUMN_NAMES]
            self.table.insert("", "end", values=new_data)
            self.save_data()
            popup.destroy()

        ttk.Button(popup, text="Insert data", command=submit).grid(row=len(self.DATA_COLUMN_NAMES), column=0, columnspan=2, pady=10)

        for i, data in enumerate(self.COLUMN_NAMES):
            if name == name:
                tomatoes = tk.column(tomatoes)
                mushrooms = tk.column(mushrooms)
                lettuce = tk.column(lettuce)
                meat = tk.column(meat)
                total_veggies = tomatoes + mushrooms + lettuce
                while total_veggies or meat > 2000:
                    number_of_bonuses = total_veggies % 2000 + meat % 2000
                    total_bonus = number_of_bonuses * 10000
                    self.table.insert("", "end", values=total_bonus)
            else:
                break

                


        for i, name in enumerate(self.COLUMN_NAMES):
            tk.Label(popup, text=name).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = tk.Entry(popup)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            entries[name] = entry

        def submit():
            new_bonus = [entries[name].get() for name in self.COLUMN_NAMES]
            self.table.insert("", "end", values=new_bonus)
            self.save_data()
            popup.destroy()

        ttk.Button(popup, text="Add Bonus", command=submit).grid(row=len(self.COLUMN_NAMES), column=0, columnspan=2, pady=10)

    def new_week(self):
        week_data = {
            "date_range": self.get_date_range(),
            "entries": [self.table.item(item, "values") for item in self.table.get_children()]
        }
        self.history_data.append(week_data)
        self.save_data()

        self.start_date += timedelta(weeks=1)
        self.end_date += timedelta(weeks=1)
        self.date_label.config(text=self.get_date_range())
        
        self.table.delete(*self.table.get_children())
        for row in self.TEMPLATE:
            self.table.insert("", "end", values=row)
        
        self.save_data()

    def show_history(self):
        history_window = tk.Toplevel(self)
        history_window.title("Bonus History")
        history_window.geometry("700x500")

        canvas = tk.Canvas(history_window)
        scrollbar = ttk.Scrollbar(history_window, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas)
        
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for week in self.history_data:
            tk.Label(frame, text=week["date_range"], font=("Arial", 14, "bold")).pack(pady=5)
            history_table = ttk.Treeview(frame, columns=self.COLUMN_NAMES, show="headings", height=5)
            history_table.pack(fill="both", padx=10, pady=5)

            for name in self.COLUMN_NAMES:
                history_table.heading(name, text=name)
                history_table.column(name, width=120)

            for row in week["entries"]:
                history_table.insert("", "end", values=row)

    def edit_cell(self, event):
        selected_item = self.table.focus()
        if not selected_item:
            return

        col = self.table.identify_column(event.x)
        row = self.table.identify_row(event.y)
        if not row:
            return

        column_index = int(col[1:]) - 1
        row_values = list(self.table.item(selected_item, "values"))

        while len(row_values) < 10:
            row_values.append("")

        DROPDOWN_OPTIONS = {
            4: ["Yes", "No"],
            6: ["Active", "LOA"],
            7: ["Dexter Cherry", "Myles Cherry", "Tommy Kade", "Carissa SL-Cherry", "Luna Kade", "BigKing HMDollas", "Blake Cherry", "Chip Monck", "Ling Cherry", "Jack Slater", "Bart", "Tommy Longsocks"]
        }

        x, y, width, height = self.table.bbox(selected_item, col)

        if column_index in DROPDOWN_OPTIONS:
            combobox = ttk.Combobox(self, values=DROPDOWN_OPTIONS[column_index], state="readonly")
            combobox.set(row_values[column_index])
            combobox.place(x=x, y=y + height, width=width)

            def save_dropdown(event=None):
                row_values[column_index] = combobox.get()
                self.table.item(selected_item, values=row_values)
                combobox.destroy()
                self.save_data()

            combobox.bind("<<ComboboxSelected>>", save_dropdown)
            combobox.focus_set()

        else:
            entry = tk.Entry(self)
            entry.insert(0, row_values[column_index])
            entry.place(x=x, y=y + height, width=width)

            def save_edit(event=None):
                row_values[column_index] = entry.get()
                self.table.item(selected_item, values=row_values)
                entry.destroy()
                self.save_data()

            entry.bind("<Return>", save_edit)
            entry.focus_set()

    def delete_selected_rows(self, event=None):
        selected_items = self.table.selection()
        if not selected_items:
            return

        for item in selected_items:
            self.table.delete(item)

        self.save_data()

    def save_data(self):
        data = {
            "current_week": {
                "start_date": self.start_date.strftime('%Y-%m-%d'),
                "end_date": self.end_date.strftime('%Y-%m-%d'),
                "entries": [self.table.item(item, "values") for item in self.table.get_children()]
            },
            "history": self.history_data
        }
        with open("farming_bonus_data.json", "w") as f:
            json.dump(data, f)

    def load_data(self):
        if os.path.exists("farming_bonus_data.json"):
            with open("farming_bonus_data.json", "r") as f:
                data = json.load(f)
            
            self.start_date = datetime.strptime(data["current_week"]["start_date"], '%Y-%m-%d')
            self.end_date = datetime.strptime(data["current_week"]["end_date"], '%Y-%m-%d')
            self.date_label.config(text=self.get_date_range())
            self.history_data = data.get("history", [])
            
            for row in data["current_week"]["entries"]:
                self.table.insert("", "end", values=row)
        else:
            for row in self.TEMPLATE:
                self.table.insert("", "end", values=row)


class Fund(tk.Frame):
    TEMPLATE = []
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        content = tk.Frame(self)
        content.grid(row=0, column=0, sticky="nsew")

        label = tk.Label(content, text="Fund", font=("Arial", 18))
        label.pack(pady=10)

        self.start_date = datetime.today()
        self.end_date = self.start_date + timedelta(days=6)
        self.date_label = tk.Label(content, text=self.get_date_range(), font=("Arial", 14))
        self.date_label.pack(pady=5)

        self.COLUMN_NAMES = ["Date", "Timeframe", "Fund", "Actual Fund", "Signature"]

        self.table = ttk.Treeview(content, columns=self.COLUMN_NAMES, show="headings", height=10)
        self.table.pack(expand=True, fill="both")

        for name in self.COLUMN_NAMES:
            self.table.heading(name, text=name)
            self.table.column(name, width=120)

        self.history_data = []  # Stores past weeks' data

        self.load_data()

        self.table.bind("<Double-1>", self.edit_cell)
        self.table.bind("<Delete>", self.delete_selected_rows)
        self.table.bind("<BackSpace>", self.delete_selected_rows)

        ttk.Button(content, text="Add Bonuses", command=self.add_bonus).pack(pady=5)
        ttk.Button(content, text="New Week", command=self.new_week).pack(pady=5)
        ttk.Button(content, text="History", command=self.show_history).pack(pady=5)
        ttk.Button(content, text="Back to Main Page", command=lambda: parent.show_page("Main")).pack(pady=5)

    def get_date_range(self):
        return f"Week: {self.start_date.strftime('%m/%d/%Y')} - {self.end_date.strftime('%m/%d/%Y')}"
    
    def add_bonus(self):
        popup = tk.Toplevel(self)
        popup.title("Add Bonus")
        popup.geometry("400x400")

        entries = {}

        for i, name in enumerate(self.COLUMN_NAMES):
            tk.Label(popup, text=name).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = tk.Entry(popup)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            entries[name] = entry

        def submit():
            new_bonus = [entries[name].get() for name in self.COLUMN_NAMES]
            self.table.insert("", "end", values=new_bonus)
            self.save_data()
            popup.destroy()

        ttk.Button(popup, text="Add Bonus", command=submit).grid(row=len(self.COLUMN_NAMES), column=0, columnspan=2, pady=10)

    def new_week(self):
        week_data = {
            "date_range": self.get_date_range(),
            "entries": [self.table.item(item, "values") for item in self.table.get_children()]
        }
        self.history_data.append(week_data)
        self.save_data()

        self.start_date += timedelta(weeks=1)
        self.end_date += timedelta(weeks=1)
        self.date_label.config(text=self.get_date_range())
        
        self.table.delete(*self.table.get_children())
        for row in self.TEMPLATE:
            self.table.insert("", "end", values=row)
        
        self.save_data()

    def show_history(self):
        history_window = tk.Toplevel(self)
        history_window.title("Bonus History")
        history_window.geometry("700x500")

        canvas = tk.Canvas(history_window)
        scrollbar = ttk.Scrollbar(history_window, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas)
        
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for week in self.history_data:
            tk.Label(frame, text=week["date_range"], font=("Arial", 14, "bold")).pack(pady=5)
            history_table = ttk.Treeview(frame, columns=self.COLUMN_NAMES, show="headings", height=5)
            history_table.pack(fill="both", padx=10, pady=5)

            for name in self.COLUMN_NAMES:
                history_table.heading(name, text=name)
                history_table.column(name, width=120)

            for row in week["entries"]:
                history_table.insert("", "end", values=row)

    def edit_cell(self, event):
        selected_item = self.table.focus()
        if not selected_item:
            return

        col = self.table.identify_column(event.x)
        row = self.table.identify_row(event.y)
        if not row:
            return

        column_index = int(col[1:]) - 1
        row_values = list(self.table.item(selected_item, "values"))

        while len(row_values) < 10:
            row_values.append("")

        DROPDOWN_OPTIONS = {
            4: ["Yes", "No"],
            6: ["Active", "LOA"],
            7: ["Dexter Cherry", "Myles Cherry", "Tommy Kade", "Carissa SL-Cherry", "Luna Kade", "BigKing HMDollas", "Blake Cherry", "Chip Monck", "Ling Cherry", "Jack Slater", "Bart", "Tommy Longsocks"]
        }

        x, y, width, height = self.table.bbox(selected_item, col)

        if column_index in DROPDOWN_OPTIONS:
            combobox = ttk.Combobox(self, values=DROPDOWN_OPTIONS[column_index], state="readonly")
            combobox.set(row_values[column_index])
            combobox.place(x=x, y=y + height, width=width)

            def save_dropdown(event=None):
                row_values[column_index] = combobox.get()
                self.table.item(selected_item, values=row_values)
                combobox.destroy()
                self.save_data()

            combobox.bind("<<ComboboxSelected>>", save_dropdown)
            combobox.focus_set()

        else:
            entry = tk.Entry(self)
            entry.insert(0, row_values[column_index])
            entry.place(x=x, y=y + height, width=width)

            def save_edit(event=None):
                row_values[column_index] = entry.get()
                self.table.item(selected_item, values=row_values)
                entry.destroy()
                self.save_data()

            entry.bind("<Return>", save_edit)
            entry.focus_set()

    def delete_selected_rows(self, event=None):
        selected_items = self.table.selection()
        if not selected_items:
            return

        for item in selected_items:
            self.table.delete(item)

        self.save_data()

    def save_data(self):
        data = {
            "current_week": {
                "start_date": self.start_date.strftime('%Y-%m-%d'),
                "end_date": self.end_date.strftime('%Y-%m-%d'),
                "entries": [self.table.item(item, "values") for item in self.table.get_children()]
            },
            "history": self.history_data
        }
        with open("fund_data.json", "w") as f:
            json.dump(data, f)

    def load_data(self):
        if os.path.exists("fund_data.json"):
            with open("fund_data.json", "r") as f:
                data = json.load(f)
            
            self.start_date = datetime.strptime(data["current_week"]["start_date"], '%Y-%m-%d')
            self.end_date = datetime.strptime(data["current_week"]["end_date"], '%Y-%m-%d')
            self.date_label.config(text=self.get_date_range())
            self.history_data = data.get("history", [])
            
            for row in data["current_week"]["entries"]:
                self.table.insert("", "end", values=row)
        else:
            for row in self.TEMPLATE:
                self.table.insert("", "end", values=row)


class LucidEats(tk.Frame):
    TEMPLATE = []
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        content = tk.Frame(self)
        content.grid(row=0, column=0, sticky="nsew")

        label = tk.Label(content, text="Lucid Eats", font=("Arial", 18))
        label.pack(pady=10)

        self.start_date = datetime.today()
        self.end_date = self.start_date + timedelta(days=6)
        self.date_label = tk.Label(content, text=self.get_date_range(), font=("Arial", 14))
        self.date_label.pack(pady=5)

        self.COLUMN_NAMES = ["Date", "Ammount", "Leader", "Helpers"]

        self.table = ttk.Treeview(content, columns=self.COLUMN_NAMES, show="headings", height=10)
        self.table.pack(expand=True, fill="both")

        for name in self.COLUMN_NAMES:
            self.table.heading(name, text=name)
            self.table.column(name, width=120)

        self.history_data = []

        self.load_data()

        self.table.bind("<Double-1>", self.edit_cell)
        self.table.bind("<Delete>", self.delete_selected_rows)
        self.table.bind("<BackSpace>", self.delete_selected_rows)

        ttk.Button(content, text="Add Bonuses", command=self.add_bonus).pack(pady=5)
        ttk.Button(content, text="New Week", command=self.new_week).pack(pady=5)
        ttk.Button(content, text="History", command=self.show_history).pack(pady=5)
        ttk.Button(content, text="Back to Main Page", command=lambda: parent.show_page("Main")).pack(pady=5)

    def get_date_range(self):
        return f"Week: {self.start_date.strftime('%m/%d/%Y')} - {self.end_date.strftime('%m/%d/%Y')}"
    
    def add_bonus(self):
        popup = tk.Toplevel(self)
        popup.title("Add Bonus")
        popup.geometry("400x400")

        entries = {}

        for i, name in enumerate(self.COLUMN_NAMES):
            tk.Label(popup, text=name).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = tk.Entry(popup)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            entries[name] = entry

        def submit():
            new_bonus = [entries[name].get() for name in self.COLUMN_NAMES]
            self.table.insert("", "end", values=new_bonus)
            self.save_data()
            popup.destroy()

        ttk.Button(popup, text="Add Bonus", command=submit).grid(row=len(self.COLUMN_NAMES), column=0, columnspan=2, pady=10)

    def new_week(self):
        week_data = {
            "date_range": self.get_date_range(),
            "entries": [self.table.item(item, "values") for item in self.table.get_children()]
        }
        self.history_data.append(week_data)
        self.save_data()

        self.start_date += timedelta(weeks=1)
        self.end_date += timedelta(weeks=1)
        self.date_label.config(text=self.get_date_range())
        
        self.table.delete(*self.table.get_children())
        for row in self.TEMPLATE:
            self.table.insert("", "end", values=row)
        
        self.save_data()

    def show_history(self):
        history_window = tk.Toplevel(self)
        history_window.title("Bonus History")
        history_window.geometry("700x500")

        canvas = tk.Canvas(history_window)
        scrollbar = ttk.Scrollbar(history_window, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas)
        
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for week in self.history_data:
            tk.Label(frame, text=week["date_range"], font=("Arial", 14, "bold")).pack(pady=5)
            history_table = ttk.Treeview(frame, columns=self.COLUMN_NAMES, show="headings", height=5)
            history_table.pack(fill="both", padx=10, pady=5)

            for name in self.COLUMN_NAMES:
                history_table.heading(name, text=name)
                history_table.column(name, width=120)

            for row in week["entries"]:
                history_table.insert("", "end", values=row)

    def edit_cell(self, event):
        selected_item = self.table.focus()
        if not selected_item:
            return

        col = self.table.identify_column(event.x)
        row = self.table.identify_row(event.y)
        if not row:
            return

        column_index = int(col[1:]) - 1
        row_values = list(self.table.item(selected_item, "values"))

        while len(row_values) < 10:
            row_values.append("")

        DROPDOWN_OPTIONS = {
            4: ["Yes", "No"],
            6: ["Active", "LOA"],
            7: ["Dexter Cherry", "Myles Cherry", "Tommy Kade", "Carissa SL-Cherry", "Luna Kade", "BigKing HMDollas", "Blake Cherry", "Chip Monck", "Ling Cherry", "Jack Slater", "Bart", "Tommy Longsocks"]
        }

        x, y, width, height = self.table.bbox(selected_item, col)

        if column_index in DROPDOWN_OPTIONS:
            combobox = ttk.Combobox(self, values=DROPDOWN_OPTIONS[column_index], state="readonly")
            combobox.set(row_values[column_index])
            combobox.place(x=x, y=y + height, width=width)

            def save_dropdown(event=None):
                row_values[column_index] = combobox.get()
                self.table.item(selected_item, values=row_values)
                combobox.destroy()
                self.save_data()

            combobox.bind("<<ComboboxSelected>>", save_dropdown)
            combobox.focus_set()

        else:
            entry = tk.Entry(self)
            entry.insert(0, row_values[column_index])
            entry.place(x=x, y=y + height, width=width)

            def save_edit(event=None):
                row_values[column_index] = entry.get()
                self.table.item(selected_item, values=row_values)
                entry.destroy()
                self.save_data()

            entry.bind("<Return>", save_edit)
            entry.focus_set()

    def delete_selected_rows(self, event=None):
        selected_items = self.table.selection()
        if not selected_items:
            return

        for item in selected_items:
            self.table.delete(item)

        self.save_data()

    def save_data(self):
        data = {
            "current_week": {
                "start_date": self.start_date.strftime('%Y-%m-%d'),
                "end_date": self.end_date.strftime('%Y-%m-%d'),
                "entries": [self.table.item(item, "values") for item in self.table.get_children()]
            },
            "history": self.history_data
        }
        with open("lucid_eats_data.json", "w") as f:
            json.dump(data, f)

    def load_data(self):
        if os.path.exists("lucid_eats_data.json"):
            with open("lucid_eats_data.json", "r") as f:
                data = json.load(f)
            
            self.start_date = datetime.strptime(data["current_week"]["start_date"], '%Y-%m-%d')
            self.end_date = datetime.strptime(data["current_week"]["end_date"], '%Y-%m-%d')
            self.date_label.config(text=self.get_date_range())
            self.history_data = data.get("history", [])
            
            for row in data["current_week"]["entries"]:
                self.table.insert("", "end", values=row)
        else:
            for row in self.TEMPLATE:
                self.table.insert("", "end", values=row)


class Training(tk.Frame):
    TEMPLATE = []
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        content = tk.Frame(self)
        content.grid(row=0, column=0, sticky="nsew")

        label = tk.Label(content, text="Training", font=("Arial", 18))
        label.pack(pady=10)

        self.start_date = datetime.today()
        self.end_date = self.start_date + timedelta(days=6)
        self.date_label = tk.Label(content, text=self.get_date_range(), font=("Arial", 14))
        self.date_label.pack(pady=5)

        self.COLUMN_NAMES = ["Trainee", "Trainer", "Date", "Shop", "Farming", "Delivery", "Training complete"]

        self.table = ttk.Treeview(content, columns=self.COLUMN_NAMES, show="headings", height=10)
        self.table.pack(expand=True, fill="both")

        for name in self.COLUMN_NAMES:
            self.table.heading(name, text=name)
            self.table.column(name, width=120)

        self.history_data = []

        self.load_data()

        self.table.bind("<Double-1>", self.edit_cell)
        self.table.bind("<Delete>", self.delete_selected_rows)
        self.table.bind("<BackSpace>", self.delete_selected_rows)

        ttk.Button(content, text="Add Bonuses", command=self.add_bonus).pack(pady=5)
        ttk.Button(content, text="New Week", command=self.new_week).pack(pady=5)
        ttk.Button(content, text="History", command=self.show_history).pack(pady=5)
        ttk.Button(content, text="Back to Main Page", command=lambda: parent.show_page("Main")).pack(pady=5)

    def get_date_range(self):
        return f"Week: {self.start_date.strftime('%m/%d/%Y')} - {self.end_date.strftime('%m/%d/%Y')}"
    
    def add_bonus(self):
        popup = tk.Toplevel(self)
        popup.title("Add Bonus")
        popup.geometry("400x400")

        entries = {}

        for i, name in enumerate(self.COLUMN_NAMES):
            tk.Label(popup, text=name).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = tk.Entry(popup)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            entries[name] = entry

        def submit():
            new_bonus = [entries[name].get() for name in self.COLUMN_NAMES]
            self.table.insert("", "end", values=new_bonus)
            self.save_data()
            popup.destroy()

        ttk.Button(popup, text="Add Bonus", command=submit).grid(row=len(self.COLUMN_NAMES), column=0, columnspan=2, pady=10)

    def new_week(self):
        week_data = {
            "date_range": self.get_date_range(),
            "entries": [self.table.item(item, "values") for item in self.table.get_children()]
        }
        self.history_data.append(week_data)
        self.save_data()

        self.start_date += timedelta(weeks=1)
        self.end_date += timedelta(weeks=1)
        self.date_label.config(text=self.get_date_range())
        
        self.table.delete(*self.table.get_children())
        for row in self.TEMPLATE:
            self.table.insert("", "end", values=row)
        
        self.save_data()

    def show_history(self):
        history_window = tk.Toplevel(self)
        history_window.title("Bonus History")
        history_window.geometry("700x500")

        canvas = tk.Canvas(history_window)
        scrollbar = ttk.Scrollbar(history_window, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas)
        
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for week in self.history_data:
            tk.Label(frame, text=week["date_range"], font=("Arial", 14, "bold")).pack(pady=5)
            history_table = ttk.Treeview(frame, columns=self.COLUMN_NAMES, show="headings", height=5)
            history_table.pack(fill="both", padx=10, pady=5)

            for name in self.COLUMN_NAMES:
                history_table.heading(name, text=name)
                history_table.column(name, width=120)

            for row in week["entries"]:
                history_table.insert("", "end", values=row)

    def edit_cell(self, event):
        selected_item = self.table.focus()
        if not selected_item:
            return

        col = self.table.identify_column(event.x)
        row = self.table.identify_row(event.y)
        if not row:
            return

        column_index = int(col[1:]) - 1
        row_values = list(self.table.item(selected_item, "values"))

        while len(row_values) < 10:
            row_values.append("")

        DROPDOWN_OPTIONS = {
            4: ["Yes", "No"],
            6: ["Active", "LOA"],
            7: ["Dexter Cherry", "Myles Cherry", "Tommy Kade", "Carissa SL-Cherry", "Luna Kade", "BigKing HMDollas", "Blake Cherry", "Chip Monck", "Ling Cherry", "Jack Slater", "Bart", "Tommy Longsocks"]
        }

        x, y, width, height = self.table.bbox(selected_item, col)

        if column_index in DROPDOWN_OPTIONS:
            combobox = ttk.Combobox(self, values=DROPDOWN_OPTIONS[column_index], state="readonly")
            combobox.set(row_values[column_index])
            combobox.place(x=x, y=y + height, width=width)

            def save_dropdown(event=None):
                row_values[column_index] = combobox.get()
                self.table.item(selected_item, values=row_values)
                combobox.destroy()
                self.save_data()

            combobox.bind("<<ComboboxSelected>>", save_dropdown)
            combobox.focus_set()

        else:
            entry = tk.Entry(self)
            entry.insert(0, row_values[column_index])
            entry.place(x=x, y=y + height, width=width)

            def save_edit(event=None):
                row_values[column_index] = entry.get()
                self.table.item(selected_item, values=row_values)
                entry.destroy()
                self.save_data()

            entry.bind("<Return>", save_edit)
            entry.focus_set()

    def delete_selected_rows(self, event=None):
        selected_items = self.table.selection()
        if not selected_items:
            return

        for item in selected_items:
            self.table.delete(item)

        self.save_data()

    def save_data(self):
        data = {
            "current_week": {
                "start_date": self.start_date.strftime('%Y-%m-%d'),
                "end_date": self.end_date.strftime('%Y-%m-%d'),
                "entries": [self.table.item(item, "values") for item in self.table.get_children()]
            },
            "history": self.history_data
        }
        with open("training_data.json", "w") as f:
            json.dump(data, f)

    def load_data(self):
        if os.path.exists("training_data.json"):
            with open("training_data.json", "r") as f:
                data = json.load(f)
            
            self.start_date = datetime.strptime(data["current_week"]["start_date"], '%Y-%m-%d')
            self.end_date = datetime.strptime(data["current_week"]["end_date"], '%Y-%m-%d')
            self.date_label.config(text=self.get_date_range())
            self.history_data = data.get("history", [])
            
            for row in data["current_week"]["entries"]:
                self.table.insert("", "end", values=row)
        else:
            for row in self.TEMPLATE:
                self.table.insert("", "end", values=row)


class IngredientsBought(tk.Frame):
    TEMPLATE = []
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        content = tk.Frame(self)
        content.grid(row=0, column=0, sticky="nsew")

        label = tk.Label(content, text="Ingredients Bought", font=("Arial", 18))
        label.pack(pady=10)

        self.start_date = datetime.today()
        self.end_date = self.start_date + timedelta(days=6)
        self.date_label = tk.Label(content, text=self.get_date_range(), font=("Arial", 14))
        self.date_label.pack(pady=5)

        self.COLUMN_NAMES = ["Name", "UID", "Date", "Tomatoes", "Mushrooms", "Lettuce", "Meat", "Paid By", "Notes"]

        self.table = ttk.Treeview(content, columns=self.COLUMN_NAMES, show="headings", height=10)
        self.table.pack(expand=True, fill="both")

        for name in self.COLUMN_NAMES:
            self.table.heading(name, text=name)
            self.table.column(name, width=120)

        self.history_data = []

        self.load_data()

        self.table.bind("<Double-1>", self.edit_cell)
        self.table.bind("<Delete>", self.delete_selected_rows)
        self.table.bind("<BackSpace>", self.delete_selected_rows)

        ttk.Button(content, text="Add Bonuses", command=self.add_bonus).pack(pady=5)
        ttk.Button(content, text="New Week", command=self.new_week).pack(pady=5)
        ttk.Button(content, text="History", command=self.show_history).pack(pady=5)
        ttk.Button(content, text="Back to Main Page", command=lambda: parent.show_page("Main")).pack(pady=5)

    def get_date_range(self):
        return f"Week: {self.start_date.strftime('%m/%d/%Y')} - {self.end_date.strftime('%m/%d/%Y')}"
    
    def add_bonus(self):
        popup = tk.Toplevel(self)
        popup.title("Add Bonus")
        popup.geometry("400x400")

        entries = {}

        for i, name in enumerate(self.COLUMN_NAMES):
            tk.Label(popup, text=name).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = tk.Entry(popup)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            entries[name] = entry

        def submit():
            new_bonus = [entries[name].get() for name in self.COLUMN_NAMES]
            self.table.insert("", "end", values=new_bonus)
            self.save_data()
            popup.destroy()

        ttk.Button(popup, text="Add Bonus", command=submit).grid(row=len(self.COLUMN_NAMES), column=0, columnspan=2, pady=10)

    def new_week(self):
        week_data = {
            "date_range": self.get_date_range(),
            "entries": [self.table.item(item, "values") for item in self.table.get_children()]
        }
        self.history_data.append(week_data)
        self.save_data()

        self.start_date += timedelta(weeks=1)
        self.end_date += timedelta(weeks=1)
        self.date_label.config(text=self.get_date_range())
        
        self.table.delete(*self.table.get_children())
        for row in self.TEMPLATE:
            self.table.insert("", "end", values=row)
        
        self.save_data()

    def show_history(self):
        history_window = tk.Toplevel(self)
        history_window.title("Bonus History")
        history_window.geometry("700x500")

        canvas = tk.Canvas(history_window)
        scrollbar = ttk.Scrollbar(history_window, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas)
        
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for week in self.history_data:
            tk.Label(frame, text=week["date_range"], font=("Arial", 14, "bold")).pack(pady=5)
            history_table = ttk.Treeview(frame, columns=self.COLUMN_NAMES, show="headings", height=5)
            history_table.pack(fill="both", padx=10, pady=5)

            for name in self.COLUMN_NAMES:
                history_table.heading(name, text=name)
                history_table.column(name, width=120)

            for row in week["entries"]:
                history_table.insert("", "end", values=row)

    def edit_cell(self, event):
        selected_item = self.table.focus()
        if not selected_item:
            return

        col = self.table.identify_column(event.x)
        row = self.table.identify_row(event.y)
        if not row:
            return

        column_index = int(col[1:]) - 1
        row_values = list(self.table.item(selected_item, "values"))

        while len(row_values) < 10:
            row_values.append("")

        DROPDOWN_OPTIONS = {
            4: ["Yes", "No"],
            6: ["Active", "LOA"],
            7: ["Dexter Cherry", "Myles Cherry", "Tommy Kade", "Carissa SL-Cherry", "Luna Kade", "BigKing HMDollas", "Blake Cherry", "Chip Monck", "Ling Cherry", "Jack Slater", "Bart", "Tommy Longsocks"]
        }

        x, y, width, height = self.table.bbox(selected_item, col)

        if column_index in DROPDOWN_OPTIONS:
            combobox = ttk.Combobox(self, values=DROPDOWN_OPTIONS[column_index], state="readonly")
            combobox.set(row_values[column_index])
            combobox.place(x=x, y=y + height, width=width)

            def save_dropdown(event=None):
                row_values[column_index] = combobox.get()
                self.table.item(selected_item, values=row_values)
                combobox.destroy()
                self.save_data()

            combobox.bind("<<ComboboxSelected>>", save_dropdown)
            combobox.focus_set()

        else:
            entry = tk.Entry(self)
            entry.insert(0, row_values[column_index])
            entry.place(x=x, y=y + height, width=width)

            def save_edit(event=None):
                row_values[column_index] = entry.get()
                self.table.item(selected_item, values=row_values)
                entry.destroy()
                self.save_data()

            entry.bind("<Return>", save_edit)
            entry.focus_set()

    def delete_selected_rows(self, event=None):
        selected_items = self.table.selection()
        if not selected_items:
            return

        for item in selected_items:
            self.table.delete(item)

        self.save_data()

    def save_data(self):
        data = {
            "current_week": {
                "start_date": self.start_date.strftime('%Y-%m-%d'),
                "end_date": self.end_date.strftime('%Y-%m-%d'),
                "entries": [self.table.item(item, "values") for item in self.table.get_children()]
            },
            "history": self.history_data
        }
        with open("ingredients_bought_data.json", "w") as f:
            json.dump(data, f)

    def load_data(self):
        if os.path.exists("ingredients_bought_data.json"):
            with open("ingredients_bought_data.json", "r") as f:
                data = json.load(f)
            
            self.start_date = datetime.strptime(data["current_week"]["start_date"], '%Y-%m-%d')
            self.end_date = datetime.strptime(data["current_week"]["end_date"], '%Y-%m-%d')
            self.date_label.config(text=self.get_date_range())
            self.history_data = data.get("history", [])
            
            for row in data["current_week"]["entries"]:
                self.table.insert("", "end", values=row)
        else:
            for row in self.TEMPLATE:
                self.table.insert("", "end", values=row)


class CheatSheet(tk.Frame):
    TEMPLATE = []
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        content = tk.Frame(self)
        content.grid(row=0, column=0, sticky="nsew")

        label = tk.Label(content, text="Cheat Sheet", font=("Arial", 18))
        label.pack(pady=10)

        self.start_date = datetime.today()
        self.end_date = self.start_date + timedelta(days=6)
        self.date_label = tk.Label(content, text=self.get_date_range(), font=("Arial", 14))
        self.date_label.pack(pady=5)

        self.COLUMN_NAMES = ["Name", "UID", "Reason", "Bonus Amount", "Paid", "Paid By"]

        self.table = ttk.Treeview(content, columns=self.COLUMN_NAMES, show="headings", height=10)
        self.table.pack(expand=True, fill="both")

        for name in self.COLUMN_NAMES:
            self.table.heading(name, text=name)
            self.table.column(name, width=120)

        self.history_data = []

        self.load_data()

        self.table.bind("<Double-1>", self.edit_cell)
        self.table.bind("<Delete>", self.delete_selected_rows)
        self.table.bind("<BackSpace>", self.delete_selected_rows)

        ttk.Button(content, text="Add Bonuses", command=self.add_bonus).pack(pady=5)
        ttk.Button(content, text="New Week", command=self.new_week).pack(pady=5)
        ttk.Button(content, text="History", command=self.show_history).pack(pady=5)
        ttk.Button(content, text="Back to Main Page", command=lambda: parent.show_page("Main")).pack(pady=5)

    def get_date_range(self):
        return f"Week: {self.start_date.strftime('%m/%d/%Y')} - {self.end_date.strftime('%m/%d/%Y')}"
    
    def add_bonus(self):
        popup = tk.Toplevel(self)
        popup.title("Add Bonus")
        popup.geometry("400x400")

        entries = {}

        for i, name in enumerate(self.COLUMN_NAMES):
            tk.Label(popup, text=name).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = tk.Entry(popup)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            entries[name] = entry

        def submit():
            new_bonus = [entries[name].get() for name in self.COLUMN_NAMES]
            self.table.insert("", "end", values=new_bonus)
            self.save_data()
            popup.destroy()

        ttk.Button(popup, text="Add Bonus", command=submit).grid(row=len(self.COLUMN_NAMES), column=0, columnspan=2, pady=10)

    def new_week(self):
        week_data = {
            "date_range": self.get_date_range(),
            "entries": [self.table.item(item, "values") for item in self.table.get_children()]
        }
        self.history_data.append(week_data)
        self.save_data()

        self.start_date += timedelta(weeks=1)
        self.end_date += timedelta(weeks=1)
        self.date_label.config(text=self.get_date_range())
        
        self.table.delete(*self.table.get_children())
        for row in self.TEMPLATE:
            self.table.insert("", "end", values=row)
        
        self.save_data()

    def show_history(self):
        history_window = tk.Toplevel(self)
        history_window.title("Bonus History")
        history_window.geometry("700x500")

        canvas = tk.Canvas(history_window)
        scrollbar = ttk.Scrollbar(history_window, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas)
        
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for week in self.history_data:
            tk.Label(frame, text=week["date_range"], font=("Arial", 14, "bold")).pack(pady=5)
            history_table = ttk.Treeview(frame, columns=self.COLUMN_NAMES, show="headings", height=5)
            history_table.pack(fill="both", padx=10, pady=5)

            for name in self.COLUMN_NAMES:
                history_table.heading(name, text=name)
                history_table.column(name, width=120)

            for row in week["entries"]:
                history_table.insert("", "end", values=row)

    def edit_cell(self, event):
        selected_item = self.table.focus()
        if not selected_item:
            return

        col = self.table.identify_column(event.x)
        row = self.table.identify_row(event.y)
        if not row:
            return

        column_index = int(col[1:]) - 1
        row_values = list(self.table.item(selected_item, "values"))

        while len(row_values) < 10:
            row_values.append("")

        DROPDOWN_OPTIONS = {
            4: ["Yes", "No"],
            6: ["Active", "LOA"],
            7: ["Dexter Cherry", "Myles Cherry", "Tommy Kade", "Carissa SL-Cherry", "Luna Kade", "BigKing HMDollas", "Blake Cherry", "Chip Monck", "Ling Cherry", "Jack Slater", "Bart", "Tommy Longsocks"]
        }

        x, y, width, height = self.table.bbox(selected_item, col)

        if column_index in DROPDOWN_OPTIONS:
            combobox = ttk.Combobox(self, values=DROPDOWN_OPTIONS[column_index], state="readonly")
            combobox.set(row_values[column_index])
            combobox.place(x=x, y=y + height, width=width)

            def save_dropdown(event=None):
                row_values[column_index] = combobox.get()
                self.table.item(selected_item, values=row_values)
                combobox.destroy()
                self.save_data()

            combobox.bind("<<ComboboxSelected>>", save_dropdown)
            combobox.focus_set()

        else:
            entry = tk.Entry(self)
            entry.insert(0, row_values[column_index])
            entry.place(x=x, y=y + height, width=width)

            def save_edit(event=None):
                row_values[column_index] = entry.get()
                self.table.item(selected_item, values=row_values)
                entry.destroy()
                self.save_data()

            entry.bind("<Return>", save_edit)
            entry.focus_set()

    def delete_selected_rows(self, event=None):
        selected_items = self.table.selection()
        if not selected_items:
            return

        for item in selected_items:
            self.table.delete(item)

        self.save_data()

    def save_data(self):
        data = {
            "current_week": {
                "start_date": self.start_date.strftime('%Y-%m-%d'),
                "end_date": self.end_date.strftime('%Y-%m-%d'),
                "entries": [self.table.item(item, "values") for item in self.table.get_children()]
            },
            "history": self.history_data
        }
        with open("cheat_sheet_data.json", "w") as f:
            json.dump(data, f)

    def load_data(self):
        if os.path.exists("cheat_sheet_data.json"):
            with open("cheat_sheet_data.json", "r") as f:
                data = json.load(f)
            
            self.start_date = datetime.strptime(data["current_week"]["start_date"], '%Y-%m-%d')
            self.end_date = datetime.strptime(data["current_week"]["end_date"], '%Y-%m-%d')
            self.date_label.config(text=self.get_date_range())
            self.history_data = data.get("history", [])
            
            for row in data["current_week"]["entries"]:
                self.table.insert("", "end", values=row)
        else:
            for row in self.TEMPLATE:
                self.table.insert("", "end", values=row)






                



# class HR(tk.Frame):
    # def __init__(self, parent):
    #     super().__init__(parent)

    #     self.grid_rowconfigure(0, weight=1)
    #     self.grid_columnconfigure(0, weight=1)

    #     content = tk.Frame(self)
    #     content.grid(row=0, column=0, sticky="nsew")

    #     label = tk.Label(content, text="Bonuses", font=("Arial", 18))
    #     label.pack(pady=10)

        
    #     self.start_date = datetime.today()
    #     self.end_date = self.start_date + timedelta(days=6)
    #     self.date_label = tk.Label(content, text=self.get_date_range(), font=("Arial", 14))
    #     self.date_label.pack(pady=5)
    #     self.COLUMN_NAMES = ["Action", "Name", "Shop", "Farming", "Delivery"]


        

    #     self.table = ttk.Treeview(content, columns=self.COLUMN_NAMES, show="headings", height=10)
    #     self.table.pack(expand=True, fill="both")

    #     for name in self.COLUMN_NAMES:
    #         self.table.heading(name, text=name)
    #         self.table.column(name, width=120)

    #     self.history_data = []  # Stores past weeks' data

    #     self.load_data()

    #     self.table.bind("<Double-1>", self.edit_cell)
    #     self.table.bind("<Delete>", self.delete_selected_rows)
    #     self.table.bind("<BackSpace>", self.delete_selected_rows)

    #     def get_date_range(self):
    #         return f"Week: {self.start_date.strftime('%m/%d/%Y')} - {self.end_date.strftime('%m/%d/%Y')}"

    #     ttk.Button(content, text="Add Bonuses", command=self.add_bonus).pack(pady=5)
    #     ttk.Button(content, text="New Week", command=self.new_week).pack(pady=5)
    #     ttk.Button(content, text="History", command=self.show_history).pack(pady=5)
    #     ttk.Button(content, text="Back to Main Page", command=lambda: parent.show_page("Main")).pack(pady=5)



    # def load_data(self):
    #     if os.path.exists(self.HR_DATA):
    #         with open(self.HR_DATA, "r") as f:
    #             data = json.load(f)
            
    #         self.start_date = datetime.strptime(data["current_week"]["start_date"], '%Y-%m-%d')
    #         self.end_date = datetime.strptime(data["current_week"]["end_date"], '%Y-%m-%d')
    #         self.date_label.config(text=self.get_date_range())
    #         self.history_data = data.get("history", [])
            
    #         for row in data["current_week"]["entries"]:
    #             self.table.insert("", "end", values=row)
    #     else:
    #         for row in self.TEMPLATE:
    #             self.table.insert("", "end", values=row)


    # def save_data(self):
    #     data = {
    #         "current_week": {
    #             "start_date": self.start_date.strftime('%Y-%m-%d'),
    #             "end_date": self.end_date.strftime('%Y-%m-%d'),
    #             "entries": [self.table.item(item, "values") for item in self.table.get_children()]
    #         },
    #         "history": self.history_data
    #     }
    #     with open(self.HR_DATA, "w") as f:
    #         json.dump(data, f)
        
    
        



# Create the application
app = App()
app.mainloop()
