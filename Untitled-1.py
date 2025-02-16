import tkinter as tk
from tkinter import ttk
import csv
import os

DATA_FILE = "table_data.csv"  # File to save and load table data


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Luchetti's App")
        self.geometry("600x400")

        self.pages = {}

        # Add all pages
        main_page = MainPage(self)
        self.add_page("Main", main_page)

        self.add_page("Page1", OtherPage(self, "Page 1"))
        self.add_page("Page2", ExcelPage(self))
        self.add_page("Page3", OtherPage(self, "Page 3"))

        # Explicitly show the main page after adding all pages
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

        # Configure grid for the frame to expand and center content
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Add a content frame in the center
        content = tk.Frame(self)
        content.grid(row=0, column=0)

        # Widgets inside the content frame
        label = tk.Label(content, text="Main Page", font=("Arial", 18))
        label.pack(pady=20)

        button1 = ttk.Button(content, text="Go to Page 1", command=lambda: parent.show_page("Page1"))
        button1.pack(pady=5)

        button2 = ttk.Button(content, text="Go to Page 2 (Excel Sheet)", command=lambda: parent.show_page("Page2"))
        button2.pack(pady=5)

        button3 = ttk.Button(content, text="Go to Page 3", command=lambda: parent.show_page("Page3"))
        button3.pack(pady=5)



class OtherPage(tk.Frame):
    def __init__(self, parent, page_name):
        super().__init__(parent)

        # Configure grid for centering
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        content = tk.Frame(self)
        content.grid(row=0, column=0)
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)

        label = tk.Label(content, text=f"{page_name}", font=("Arial", 18))
        label.grid(row=0, column=0, pady=20)

        back_button = ttk.Button(content, text="Back to Main Page", command=lambda: parent.show_page("Main"))
        back_button.grid(row=1, column=0, pady=5)


class ExcelPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Configure grid for the frame to expand and center content
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Add a content frame in the center
        content = tk.Frame(self)
        content.pack(expand=True, fill="both")
        content.grid(row=0, column=0)

        # Add a label
        label = tk.Label(content, text="Editable Excel-Type Sheet", font=("Arial", 18))
        label.pack(pady=10)

        # Define columns (A to J for 10 columns)
        COLUMN_NAMES = [
        "Position",
        "Name",
        "UID",
        "Phone",
        "Activity",
        "Date Hired",
        "Hired by",
        "Crew",
        "Training",
        "Notes"
        ] 
        self.table = ttk.Treeview(content, columns=[f"Col{i}" for i in range(1, 11)], show="headings", height=10)


        self.table.pack(expand=True, fill="both")

        self.load_data()

        for i, name in enumerate(COLUMN_NAMES, start=1):
            self.table.heading(f"Col{i}", text=name)  # Assign custom name to the column
            self.table.column(f"Col{i}", width=100) 


        # Define column headings and widths
        for i in range(1, 11):
            self.table.heading(f"Col{i}", text=f"Column {i}")
            self.table.column(f"Col{i}", width=100)

        # Load saved data or add sample data
        self.load_data()

        # Add bindings to edit cells
        self.table.bind("<Double-1>", self.edit_cell)

        # Add a back button
        back_button = ttk.Button(content, text="Back to Main Page", command=lambda: parent.show_page("Main"))
        back_button.pack(pady=10)

        

    def edit_cell(self, event):
        """Enable cell editing for all columns, with dropdowns for specific ones."""
        selected_item = self.table.focus()
        if not selected_item:
            return

        # Get the clicked column and row
        col = self.table.identify_column(event.x)  # e.g., '#1' for column 1
        row = self.table.identify_row(event.y)


        DROPDOWN_OPTIONS = {
            0: ["Owner", "Director", "Executive", "Senior Manager", "Manager", "Assistant Manager", "Advisor", "Shift-lead", "Core", "Crew", "Probationary, Retired", "DNH"],  # Column 1 (index 0)
            5: ["Active", "LOA"],  # Column 6 (index 5)
            8: ["Completed", "Partial"],  # Column 9 (index 8)
        }

        if not row:
            return

        # Get the column index (1-based) and convert it to 0-based
        column_index = int(col[1:]) - 1

        # Ensure the row has enough values for all 10 columns
        row_values = list(self.table.item(selected_item, "values"))
        while len(row_values) < 10:  # Add empty values if needed
            row_values.append("")

        # Check if the column has a dropdown
        if column_index in DROPDOWN_OPTIONS:
            # Create a Combobox for dropdown editing
            combobox = ttk.Combobox(self, values=DROPDOWN_OPTIONS[column_index], state="readonly")
            combobox.set(row_values[column_index])  # Set current value
            combobox.place(x=event.x_root - self.winfo_rootx(), y=event.y_root - self.winfo_rooty())

            # Save the updated value
            def save_dropdown(event=None):
                new_value = combobox.get()
                row_values[column_index] = new_value  # Update the specific cell value
                self.table.item(selected_item, values=row_values)  # Save the row back to the table
                combobox.destroy()
                self.save_data()  # Save data after editing

            combobox.bind("<<ComboboxSelected>>", save_dropdown)
            combobox.focus_set()
        else:
            # Create an Entry widget for regular editing
            entry = tk.Entry(self)
            entry.insert(0, row_values[column_index])
            entry.place(x=event.x_root - self.winfo_rootx(), y=event.y_root - self.winfo_rooty())

            # Save the updated value
            def save_edit(event=None):
                new_value = entry.get()
                row_values[column_index] = new_value  # Update the specific cell value
                self.table.item(selected_item, values=row_values)  # Save the row back to the table
                entry.destroy()
                self.save_data()  # Save data after editing

            entry.bind("<Return>", save_edit)
            entry.focus_set()



    def load_data(self):
        """Load table data from a CSV file."""
        if os.path.exists(DATA_FILE):  # Check if the data file exists
            with open(DATA_FILE, "r", newline="") as file:
                reader = csv.reader(file)
                for row in reader:
                    # Ensure each row has exactly 10 columns
                    while len(row) < 10:
                        row.append("")
                    self.table.insert("", "end", values=row)  # Insert row into table
        else:
            # If no data file exists, add sample rows
            for i in range(10):  # Default rows for visualization
                self.table.insert("", "end", values=[f"Sample {i+1} Col {j}" for j in range(1, 11)])



    def save_data(self):
        """Save table data to a CSV file."""
        rows = []
        for item in self.table.get_children():
            row_values = list(self.table.item(item, "values"))
            # Ensure each row has exactly 10 columns
            while len(row_values) < 10:
                row_values.append("")
            rows.append(row_values)

        with open(DATA_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(rows)




# Create the application
app = App()

# Run the application
app.mainloop()
