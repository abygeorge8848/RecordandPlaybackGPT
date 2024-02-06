import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from ActivityManager.pull_filesAM import pull_activities
from ActivityManager.effectsAM import create_tooltip
from ActivityManager.xml_parsingAM import insert_recorder_id, insert_flow, refactor_for_excel, open_flow
from ActivityManager.excelAM import create_excel, extract_data_and_write_to_excel, create_duplicates
import os
from set_paths import project_path, vs_code_path


#project_path = "C:\\Users\\u1138322\\PAF\\ProjectContainer\\SampleProject"

class ActivityManager():

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        # Create the main window
        self.root = tk.Tk()
        self.root.title("Activity Manager")
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Create navbar frame
        self.navbar_frame = tk.Frame(self.root)
        self.navbar_frame.pack(padx=12, pady=2, fill=tk.X)

        self.flow_frame = ttk.Frame(self.root)
        self.flow_frame.pack(padx=12, pady=5, fill=tk.X)

        self.flow_name_label = ttk.Label(self.flow_frame, text="Flow Name")
        self.flow_name_label.pack(side=tk.LEFT, padx=(0, 10))
        self.flow_name_entry = ttk.Entry(self.flow_frame)
        self.flow_name_entry.pack(side=tk.LEFT, padx=(0, 10))

        self.flow_description_label = ttk.Label(self.flow_frame, text="Flow Description")
        self.flow_description_label.pack(side=tk.LEFT, padx=(10, 10))
        self.flow_description_entry = ttk.Entry(self.flow_frame)
        self.flow_description_entry.pack(side=tk.LEFT)


        self.back_button = tk.Button(self.navbar_frame, text="<", command=self.back_to_FlowManager)
        self.back_button.pack(side=tk.LEFT)
        self.add_activity_button = tk.Button(self.navbar_frame, text="Save", command=self.add_flow)
        self.add_activity_button.pack(side=tk.LEFT)

        self.create_activity_button = tk.Button(self.navbar_frame, text="Create activity", command=self.create_activity)
        self.create_activity_button.pack(side=tk.RIGHT)
        self.navbar_separator = ttk.Separator(self.root, orient='horizontal')
        self.navbar_separator.pack(fill=tk.X, pady=1)

        # Create frame for activity name and description
        self.activity_frame = ttk.Frame(self.root)
        self.activity_frame.pack(padx=12, pady=5, fill=tk.X)


        # Create frame for file selection
        self.file_frame = ttk.Frame(self.root)
        self.file_frame.pack(padx=12, pady=5, fill=tk.X)

        self.activity_entry = ttk.Entry(self.file_frame)
        self.activity_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.activity_button = ttk.Button(self.file_frame, text="Choose Folder", command=lambda: self.choose_folder(self.activity_entry))
        self.activity_button.pack(side=tk.LEFT)

        self.flow_entry = ttk.Entry(self.file_frame)
        self.testcase_button = ttk.Button(self.file_frame, text="Choose File", command=lambda: self.choose_file(self.flow_entry))
        self.testcase_button.pack(side=tk.RIGHT)
        self.flow_entry.pack(side=tk.RIGHT, padx=(20, 10))


        # Create frame for Listboxes and their labels
        self.listbox_frame = ttk.Frame(self.root)
        self.listbox_frame.pack(padx=12, pady=5, fill=tk.BOTH, expand=True)

        # Frame for Available Activities
        self.available_activities_frame = ttk.Frame(self.listbox_frame)
        self.available_activities_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.available_activities_label = ttk.Label(self.available_activities_frame, text="Available activities")
        self.available_activities_label.pack(side=tk.TOP, fill=tk.X)

        self.available_search_frame = ttk.Frame(self.available_activities_frame)
        self.available_search_frame.pack(side=tk.TOP, fill=tk.X)
        self.available_search_entry = ttk.Entry(self.available_search_frame)
        self.available_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.available_search_button = ttk.Button(self.available_search_frame, text="Search", command=self.search_available_activities)
        self.available_search_button.pack(side=tk.LEFT, padx=(5, 0))

        self.available_activities_tree = ttk.Treeview(self.available_activities_frame, columns=('activity', 'Edit'), show='headings')
        self.available_activities_tree.heading('activity', text='Activity')
        self.available_activities_tree.heading('Edit', text='Edit')
        self.available_activities_tree.column('activity', width=200) 
        self.available_activities_tree.column('Edit', width=100, anchor='center')

        self.av_act_vscroll = ttk.Scrollbar(self.available_activities_frame, orient="vertical", command=self.available_activities_tree.yview)
        self.av_act_hscroll = ttk.Scrollbar(self.available_activities_frame, orient="horizontal", command=self.available_activities_tree.xview)
        self.available_activities_tree.configure(xscrollcommand=self.av_act_hscroll.set)
        self.av_act_hscroll.configure(command=self.available_activities_tree.xview)
        self.av_act_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.av_act_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.available_activities_tree.pack(fill=tk.BOTH, expand=True)

        # Frame for Chosen Activities
        self.chosen_activities_frame = ttk.Frame(self.listbox_frame)
        self.chosen_activities_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.chosen_activities_label = ttk.Label(self.chosen_activities_frame, text="Chosen activities")
        self.chosen_activities_label.pack(side=tk.TOP, fill=tk.X)

        self.chosen_search_frame = ttk.Frame(self.chosen_activities_frame)
        self.chosen_search_frame.pack(side=tk.TOP, fill=tk.X)
        self.chosen_search_entry = ttk.Entry(self.chosen_search_frame)
        self.chosen_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.chosen_search_button = ttk.Button(self.chosen_search_frame, text="Search", command=self.search_chosen_activities)
        self.chosen_search_button.pack(side=tk.LEFT, padx=(5, 0))

        self.chosen_activities_tree = ttk.Treeview(self.chosen_activities_frame, columns=('activity'), show='headings')
        self.chosen_activities_tree.heading('activity', text='Activity')
        self.chosen_activities_tree.column('activity', width=300, stretch=tk.YES)

        self.ch_act_vscroll = ttk.Scrollbar(self.chosen_activities_frame, orient="vertical", command=self.chosen_activities_tree.yview)
        self.ch_act_hscroll = ttk.Scrollbar(self.chosen_activities_frame, orient="horizontal", command=self.chosen_activities_tree.xview)
        self.chosen_activities_tree.configure(xscrollcommand=self.ch_act_hscroll.set)
        self.ch_act_hscroll.configure(command=self.chosen_activities_tree.xview)
        self.ch_act_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.ch_act_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.chosen_activities_tree.pack(fill=tk.BOTH, expand=True)

        # Change cursor on hover over 'Edit'
        def change_cursor(event):
            if event.widget.identify_column(event.x) == "#2":
                event.widget.config(cursor="hand2")
            else:
                event.widget.config(cursor="")

        self.available_activities_tree.bind('<Motion>', change_cursor)
        self.chosen_activities_tree.bind('<Motion>', change_cursor)

        # Binding events
        self.available_activities_tree.bind('<Double-1>', self.add_to_chosen_activities)
        self.chosen_activities_tree.bind('<Double-1>', self.delete_from_chosen_activities)
        self.available_activities_tree.bind('<Motion>', lambda e: self.show_tooltip(e, self.available_activities_tree))
        self.chosen_activities_tree.bind('<Motion>', lambda e: self.show_tooltip(e, self.chosen_activities_tree))

        self.available_activities_tree.bind('<Button-1>', self.toggle_activity_expand_collapse)
        self.chosen_activities_tree.bind('<Button-1>', self.toggle_activity_expand_collapse)

        # Create frame for Excel generation and folder selection
        self.excel_frame = ttk.Frame(self.root)
        self.excel_frame.pack(padx=12, pady=5, fill=tk.X)

        self.generate_excel_button = ttk.Button(self.excel_frame, text="Generate Excel", command=self.generate_excel)
        self.generate_excel_button.pack(side=tk.LEFT, padx=(0, 10))

        self.duplicate_excel_button = ttk.Button(self.excel_frame, text="Duplicate Excel", command=self.duplicate_excel)
        self.duplicate_excel_button.pack(side=tk.LEFT)


    def fetch_initial_available_activities_from_treeview(self):
        self.all_available_activities = [self.available_activities_tree.item(child)["values"] for child in self.available_activities_tree.get_children()]
    
    def fetch_initial_chosen_activities_from_treeview(self):
        self.all_chosen_activities = [self.chosen_activities_tree.item(child)["values"] for child in self.chosen_activities_tree.get_children()]

    def populate_available_activities(self, activities):
        self.available_activities_tree.delete(*self.available_activities_tree.get_children())
        for activity in activities:
            self.available_activities_tree.insert('', 'end', values=activity)

    def populate_chosen_activities(self, activities):
        self.chosen_activities_tree.delete(*self.chosen_activities_tree.get_children())
        for activity in activities:
            self.chosen_activities_tree.insert('', 'end', values=activity)
        
    def search_available_activities(self):
        search_query = self.available_search_entry.get().lower()
        if search_query:
            ranked_matches = []
            for item in self.all_available_activities:
                activity_name = item[0].lower()  # Assuming the activity name is the first element
                if activity_name.startswith(search_query):
                    rank = 1  # Highest rank for start match
                elif search_query in activity_name:
                    rank = 2  # Lower rank for partial match
                else:
                    rank = None  # No match
                if rank is not None:
                    ranked_matches.append((item, rank)) 
            ranked_matches.sort(key=lambda x: (x[1], x[0][0]))
            matched_activities = [item[0] for item in ranked_matches]
            self.populate_available_activities(matched_activities)
        else:
            self.populate_available_activities(self.all_available_activities)

    def search_chosen_activities(self):
        search_query = self.chosen_search_entry.get().lower()
        if search_query:
            ranked_matches = []
            for item in self.all_chosen_activities:
                activity_name = item[0].lower()  # Assuming the activity name is the first element
                if activity_name.startswith(search_query):
                    rank = 1  # Highest rank for start match
                elif search_query in activity_name:
                    rank = 2  # Lower rank for partial match
                else:
                    rank = None  # No match
                if rank is not None:
                    ranked_matches.append((item, rank)) 
            ranked_matches.sort(key=lambda x: (x[1], x[0][0]))
            matched_activities = [item[0] for item in ranked_matches]
            self.populate_chosen_activities(matched_activities)
        else:
            self.populate_chosen_activities(self.all_chosen_activities)

    

    def choose_folder(self, entry_widget):
        excel_path='\\excel'
        base_excel_path = project_path + excel_path
        print("Extracting all your available activities!")
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            entry_widget.delete(0, tk.END)  # Clear the current entry
            entry_widget.insert(0, folder_selected)  # Insert the selected folder path
            available_activities = pull_activities(folder_selected, base_excel_path)  # Call pull_activities with the folder path
            print(f"The available activities along with their corresponding sheets are : {available_activities}")
            # Clear existing items in the treeview
            for item in self.available_activities_tree.get_children():
                self.available_activities_tree.delete(item)

            bordered_edit_text = '▌Edit▐'  # Unicode characters for left and right border
            for index, (activity_name, path, sheets, unique_excel_name) in enumerate(available_activities):
                tag = 'oddrow' if index % 2 else ''
                display_name = f"> {activity_name}" if sheets else activity_name  # Ensure full name is used
                parent_id = self.available_activities_tree.insert('', tk.END, values=(display_name, bordered_edit_text), tags=(tag,))

                for sheet in sheets:
                    sheet_display_name = f"  - {sheet}   FILE : {unique_excel_name}"
                    self.available_activities_tree.insert(parent_id, tk.END, values=(sheet_display_name, bordered_edit_text), tags=(tag,))


            # Call the stripe function for the available activities tree
            self.stripe_rows(self.available_activities_tree)
            self.stripe_rows(self.chosen_activities_tree)
            self.style_edit_column(self.available_activities_tree)
            self.fetch_initial_available_activities_from_treeview()

    
    def reload_folder(self, entry_widget):
        excel_path='\\excel'
        base_excel_path = project_path + excel_path
        print("Extracting all your available activities!")
        folder_selected = entry_widget.get()
        if folder_selected:
            available_activities = pull_activities(folder_selected, base_excel_path)  # Call pull_activities with the folder path
            print(f"The available activities along with their corresponding sheets are : {available_activities}")
            # Clear existing items in the treeview
            for item in self.available_activities_tree.get_children():
                self.available_activities_tree.delete(item)
            
            for item in self.chosen_activities_tree.get_children():
                self.chosen_activities_tree.delete(item)

            bordered_edit_text = '▌Edit▐'  # Unicode characters for left and right border
            for index, (activity_name, path, sheets, unique_excel_name) in enumerate(available_activities):
                tag = 'oddrow' if index % 2 else ''
                display_name = f"> {activity_name}" if sheets else activity_name  # Ensure full name is used
                parent_id = self.available_activities_tree.insert('', tk.END, values=(display_name, bordered_edit_text), tags=(tag,))

                for sheet in sheets:
                    sheet_display_name = f"  - {sheet}   FILE : {unique_excel_name}"
                    self.available_activities_tree.insert(parent_id, tk.END, values=(sheet_display_name, bordered_edit_text), tags=(tag,))

            # Call the stripe function for the available activities tree
            self.stripe_rows(self.available_activities_tree)
            self.stripe_rows(self.chosen_activities_tree)
            self.style_edit_column(self.available_activities_tree)
            self.fetch_initial_available_activities_from_treeview()



    def show_tooltip(self, event, tree):
        row_id = tree.identify_row(event.y)
        if row_id:
            item_text = tree.item(row_id, 'values')[0]
            create_tooltip(self.available_activities_tree)
            create_tooltip(self.chosen_activities_tree)


    def create_activity(self):
        self.controller.show_activity_config()

    def add_flow(self):
        activities_with_sheets = []
        flow_name = self.flow_name_entry.get()
        flow_desc = self.flow_description_entry.get()
        flow_path = self.flow_entry.get()

        for item_id in self.chosen_activities_tree.get_children():
            # Check if the item is a parent (activity)
            if not self.chosen_activities_tree.parent(item_id):
                activity_name = self.chosen_activities_tree.item(item_id, 'values')[0]
                sheets = []

                # Iterate through child items (sheets) of the activity
                for child_id in self.chosen_activities_tree.get_children(item_id):
                    sheet_name = self.chosen_activities_tree.item(child_id, 'values')[0]
                    sheet_name = sheet_name[4:]
                    parts = sheet_name.split('   FILE : ')
                    sheet_name = parts[0]
                    excelPath = ".\\excel\\" + parts[1]
                    sheets.append({"sheetName": sheet_name, "excelPath": excelPath})

                if activity_name.startswith(">"):
                    activity_name = activity_name[2:]
                parts = activity_name.split('   PATH : ')
                activity = parts[0]
                path = parts[1]
                relative_path = os.path.relpath(path, project_path)
                relative_path = relative_path.replace('/', '\\')
                activities_with_sheets.append({"activity": activity, "path": relative_path, "sheets": sheets})

        print("Chosen Activities with Sheets:", activities_with_sheets)
        insert_flow(flow_name, flow_desc, flow_path, activities_with_sheets)
        self.controller.show_testcase_manager()


    def back_to_FlowManager(self):
        print("Let's go back to the Flow Manager!")
        self.controller.show_testcase_manager()


    def choose_file(self, entry):
        filename = filedialog.askopenfilename()
        entry.delete(0, tk.END)
        entry.insert(0, filename)


    def delete_from_chosen_activities(self, event):
        tree = event.widget
        item_id = tree.focus()
        if item_id:
            parent_id = tree.parent(item_id)
            if parent_id:  # If it's a sheet
                tree.delete(item_id)
            else:  # If it's an activity
                # Delete all children first
                for child_id in tree.get_children(item_id):
                    tree.delete(child_id)
                tree.delete(item_id)
        self.fetch_initial_chosen_activities_from_treeview()

    def on_treeview_click(self, event):
        item_id = event.widget.identify_row(event.y)
        column = event.widget.identify_column(event.x)
        if item_id and column == "#2":  # Assuming '#2' is the 'Edit' column
            activity_name = event.widget.item(item_id, 'values')[0]
            self.edit_activity(activity_name, event.widget)


    def update_chosen_activities(self):
        for i, item in enumerate(self.chosen_activities_tree.get_children()):
            tag = 'oddrow' if i % 2 else ''
            print(f"The item is : {item}")
            self.chosen_activities_tree.item(item, tags=(tag,))

    def toggle_activity_expand_collapse(self, event):
        tree = event.widget
        item_id = tree.identify_row(event.y)
        if item_id and not tree.parent(item_id):  # Only for parent items (activities)
            if tree.item(item_id, 'open'):  # If the node is open, close it
                tree.item(item_id, open=False)
            else:  # If the node is closed, open it
                tree.item(item_id, open=True)
        
        column = event.widget.identify_column(event.x)
        if item_id and column == "#2":  # Assuming '#2' is the 'Edit' column
            activity_name = event.widget.item(item_id, 'values')[0]
            if activity_name.startswith(">"):
                    activity_name = activity_name[2:]
            self.edit_activity(activity_name, event.widget)


    def add_to_chosen_activities(self, event):
        tree = event.widget
        item_id = tree.focus()
        if item_id:
            parent_id = tree.parent(item_id)
            if parent_id:  # If it's a sheet
                activity_name = tree.item(parent_id, 'values')[0]
                # Check if the parent activity already exists in chosen_activities_tree
                existing_parent_id = None
                for child_id in self.chosen_activities_tree.get_children():
                    if self.chosen_activities_tree.item(child_id, 'values')[0] == activity_name:
                        existing_parent_id = child_id
                        break

                if existing_parent_id:
                    # Parent exists, add sheet under this parent
                    sheet_name = tree.item(item_id, 'values')[0]
                    self.chosen_activities_tree.insert(existing_parent_id, tk.END, values=(sheet_name,), tags=('oddrow',))
                else:
                    # Parent doesn't exist, add both parent and sheet
                    new_parent_id = self.chosen_activities_tree.insert('', tk.END, values=(activity_name,), tags=('oddrow',))
                    sheet_name = tree.item(item_id, 'values')[0]
                    self.chosen_activities_tree.insert(new_parent_id, tk.END, values=(sheet_name,), tags=('oddrow',))
            else:
                # If it's an activity, add it along with its sheets
                activity_name = tree.item(item_id, 'values')[0]
                new_parent_id = self.chosen_activities_tree.insert('', tk.END, values=(activity_name,), tags=('oddrow',))
                for child_id in tree.get_children(item_id):
                    sheet_name = tree.item(child_id, 'values')[0]
                    self.chosen_activities_tree.insert(new_parent_id, tk.END, values=(sheet_name,), tags=('oddrow',))
            self.update_chosen_activities()
            self.fetch_initial_chosen_activities_from_treeview()



    def style_edit_column(self, tree):
        tree.tag_configure('editTag', background='lightblue', font=('Arial', 10, 'bold'))  # Set background color and bold font

    def stripe_rows(self, tree):
        tree.tag_configure('oddrow', background='#f0f0f0')

    def bordered_edit_text(self):
        return '▌Edit▐'

    def edit_activity(self, activity_name):
        flow_details = activity_name.split('   PATH : ')
        flow_id = flow_details[0]
        flow_path = flow_details[1]
        #open_flow(vs_code_path, flow_id, flow_path)
        print(f"Edit activity: {activity_name}")
        

    def edit_activity(self, activity_name, tree):
        flow_details = activity_name.split('   PATH : ')
        flow_id = flow_details[0]
        flow_path = flow_details[1]
        open_flow(vs_code_path, flow_id, flow_path)
        print(f"Edit activity: {activity_name} from {tree}")


    def generate_excel(self):
        excel_path='\\excel'
        base_excel_path = project_path + excel_path
        print(f"The base excel path is : {base_excel_path}")
        selected_items = self.chosen_activities_tree.selection()  # Get selected items in the treeview
        if selected_items:
            selected_activity = self.chosen_activities_tree.item(selected_items[0], 'values')[0]
            print(f"Generating excel for: {selected_activity}")
            parts = selected_activity.split('   PATH : ')
            activity_name = parts[0]
            path = parts[1]
            unique_excel_name = activity_name + "_" + (path.split('.')[0]).replace('/', '-').strip().replace("\\", "-").replace(":", "")
            print(f"The unique excel name is : {unique_excel_name}")
            base_excel_path = create_excel(unique_excel_name, base_excel_path)
            insert_recorder_id([{'activity': activity_name, 'path': path}])
            excelComplete = extract_data_and_write_to_excel([{'activity': activity_name, 'path': path}], base_excel_path)
            print(f"\n\n\n Base Excel Path is : {base_excel_path} \n\n\n")
            print(f"\n\n\n Path is : {path} \n\n\n")
            print(f"\n\n\n Activity name is : {activity_name} \n\n\n")
            if excelComplete:
                refactor_for_excel(base_excel_path, path, activity_name)
            self.reload_folder(self.activity_entry)

        else:
            # If no activity is selected, show an alert
            messagebox.showinfo("No Selection", "Please select a activity you want to generate the excel for")

    def duplicate_excel(self):
        excel_path='\\excel'
        base_excel_path = project_path + excel_path
        selected_items = self.chosen_activities_tree.selection()  # Get selected items in the treeview
        if selected_items:
            selected_activity = self.chosen_activities_tree.item(selected_items[0], 'values')[0]
            print(f"Generating excel for: {selected_activity}")
            parts = selected_activity.split('   PATH : ')
            activity_name = parts[0]
            path = parts[1]
            file_name = activity_name + "_" + (path.split('.')[0]).replace('/', '-').strip().replace("\\", "-").replace(":", "") + ".xlsx"
            file_name = file_name[2:]
            file_path = os.path.join(base_excel_path, file_name)
            print(f"The excel file path I'm searching in is : {file_path}")
            if not os.path.isfile(file_path):
                messagebox.showinfo("File Not Found", "There is no excel for this activity. Please generate an excel before you duplicate it.")
            else:
                self.open_duplicate_window(file_path, self.chosen_activities_tree)

        else:
            # If no activity is selected, show an alert
            messagebox.showinfo("No Selection", "Please select a activity you want to generate the excel for")

    def open_duplicate_window(self, base_excel_path, chosen_activities_tree):
        # New window for duplicating the file
        duplicate_window = tk.Toplevel()
        duplicate_window.title("Duplicate Excel File")
        duplicate_window.geometry("350x150")  # Adjust the window size for better fit
        duplicate_window.resizable(False, False)  # Disable resizing
        # Frame for content
        content_frame = ttk.Frame(duplicate_window, padding="10")
        content_frame.pack(expand=True, fill=tk.BOTH)
        # Label and textfield for number of duplicates
        label = ttk.Label(content_frame, text="Number of duplicates:", font=("Arial", 10))
        label.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        num_duplicates_entry = ttk.Entry(content_frame, font=("Arial", 10))
        num_duplicates_entry.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        # Duplicate button
        duplicate_button = ttk.Button(content_frame, text="Duplicate", command=lambda: self.duplicate_file(duplicate_window, num_duplicates_entry, base_excel_path, chosen_activities_tree))
        duplicate_button.pack(side=tk.TOP, pady=(0, 10))

        # Center the window on the screen
        self.center_window_on_screen(duplicate_window)

    def center_window_on_screen(self, window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry('{}x{}+{}+{}'.format(width, height, x, y))


    def duplicate_file(self, duplicate_window, num_duplicates_entry, base_excel_path, chosen_activities_tree):
        try:
            num_duplicates = int(num_duplicates_entry.get())
        except ValueError:
            messagebox.showinfo("Invalid Input", "Please enter a valid number")
            return
        # Close the duplicate window
        duplicate_window.destroy()
        # Call the new function for duplicating the file
        sheets = create_duplicates(num_duplicates, base_excel_path)
        self.reload_folder(self.activity_entry)

    def run(self):
        self.root.deiconify()

    def withdraw(self):
        self.root.withdraw()



if __name__ == "__main__":
    ActivityManagerInstance = ActivityManager()
    ActivityManagerInstance.run()