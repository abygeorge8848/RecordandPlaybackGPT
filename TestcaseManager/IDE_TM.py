import tkinter as tk
from tkinter import filedialog, ttk, messagebox, Toplevel, Label, Entry, Button
from project_interaction import pull_activities, write_init
from effectsTM import create_tooltip
from RunPAFTM import run_file, report_open
import os
import sys
from pathlib import Path
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))
from ActivityManager.IDE import ActivityManager



project_path = "C:/Users/u1138322/PAF/ProjectContainer/SampleProject"


class TestcaseManager:

    def __init__(self):
        # Create the main window
        self.root = tk.Tk()
        self.root.title("Flow Manager")
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Create navbar frame
        self.navbar_frame = tk.Frame(self.root)
        self.navbar_frame.pack(padx=12, pady=2, fill=tk.X)

        self.open_report_button = tk.Button(self.navbar_frame, text="Open Report", command=report_open)

        self.url_name_label = ttk.Label(self.navbar_frame, text="Enter URL")
        self.url_name_label.pack(side=tk.LEFT, padx=(0, 10))
        self.url_name_entry = ttk.Entry(self.navbar_frame)
        self.url_name_entry.pack(side=tk.LEFT, padx=(0, 10))

        self.run_button = tk.Button(self.navbar_frame, text="Run", command=self.run_suite)
        self.run_button.pack(side=tk.LEFT)

        self.create_Flow_button = tk.Button(self.navbar_frame, text="Create Flow", command=self.create_flow)
        self. create_Flow_button.pack(side=tk.RIGHT)
        self.navbar_separator = ttk.Separator(self.root, orient='horizontal')
        self.navbar_separator.pack(fill=tk.X, pady=1)

        # Create frame for Flow name and description
        self.flow_frame = ttk.Frame(self.root)
        self.flow_frame.pack(padx=12, pady=5, fill=tk.X)


        # Create frame for file selection
        self.file_frame = ttk.Frame(self.root)
        self.file_frame.pack(padx=12, pady=5, fill=tk.X)

        self.flow_entry = ttk.Entry(self.file_frame)
        self.flow_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.flow_button = ttk.Button(self.file_frame, text="Choose Flow File", command=lambda: self.choose_flow_file(self.flow_entry))
        self.flow_button.pack(side=tk.LEFT)

        self.init_entry = ttk.Entry(self.file_frame)
        self.testcase_button = ttk.Button(self.file_frame, text="Choose Init File", command=lambda: self.choose_init_file(self.init_entry))
        self.testcase_button.pack(side=tk.RIGHT)
        self.init_entry.pack(side=tk.RIGHT, padx=(20, 10))

        # Create frame for Listboxes and their labels
        self.listbox_frame = ttk.Frame(self.root)
        self.listbox_frame.pack(padx=12, pady=5, fill=tk.BOTH, expand=True)

        # Frame for Available Activities
        self.available_flows_frame = ttk.Frame(self.listbox_frame)
        self.available_flows_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.available_flows_label = ttk.Label(self.available_flows_frame, text="Available Flows")
        self.available_flows_label.pack(side=tk.TOP, fill=tk.X)

        self.available_flows_tree = ttk.Treeview(self.available_flows_frame, columns=('Flow', 'Edit'), show='headings')
        self.available_flows_tree.heading('Flow', text='Flow')
        self.available_flows_tree.heading('Edit', text='Edit')
        self.available_flows_tree.column('Flow', width=200) 
        self.available_flows_tree.column('Edit', width=100, anchor='center')

        self.av_act_vscroll = ttk.Scrollbar(self.available_flows_frame, orient="vertical", command=self.available_flows_tree.yview)
        self.av_act_hscroll = ttk.Scrollbar(self.available_flows_frame, orient="horizontal", command=self.available_flows_tree.xview)
        self.available_flows_tree.configure(xscrollcommand=self.av_act_hscroll.set)
        self.av_act_hscroll.configure(command=self.available_flows_tree.xview)
        self.av_act_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.av_act_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.available_flows_tree.pack(fill=tk.BOTH, expand=True)

        # Frame for Chosen Activities
        self.chosen_flows_frame = ttk.Frame(self.listbox_frame)
        self.chosen_flows_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.chosen_flows_label = ttk.Label(self.chosen_flows_frame, text="Chosen Flows")
        self.chosen_flows_label.pack(side=tk.TOP, fill=tk.X)

        self.chosen_flows_tree = ttk.Treeview(self.chosen_flows_frame, columns=('Flow'), show='headings')
        self.chosen_flows_tree.heading('Flow', text='Flow')
        self.chosen_flows_tree.column('Flow', width=300, stretch=tk.YES)

        self.ch_act_vscroll = ttk.Scrollbar(self.chosen_flows_frame, orient="vertical", command=self.chosen_flows_tree.yview)
        self.ch_act_hscroll = ttk.Scrollbar(self.chosen_flows_frame, orient="horizontal", command=self.chosen_flows_tree.xview)
        self.chosen_flows_tree.configure(xscrollcommand=self.ch_act_hscroll.set)
        self.ch_act_hscroll.configure(command=self.chosen_flows_tree.xview)
        self.ch_act_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.ch_act_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.chosen_flows_tree.pack(fill=tk.BOTH, expand=True)

        # Change cursor on hover over 'Edit'
        def change_cursor(event):
            if event.widget.identify_column(event.x) == "#2":
                event.widget.config(cursor="hand2")
            else:
                event.widget.config(cursor="")

        self.available_flows_tree.bind('<Motion>', change_cursor)
        self.chosen_flows_tree.bind('<Motion>', change_cursor)

        # Binding events
        self.available_flows_tree.bind('<Double-1>', self.add_to_chosen_flows)
        self.chosen_flows_tree.bind('<Double-1>', self.delete_from_chosen_flows)
        self.available_flows_tree.bind('<Motion>', lambda e: self.show_tooltip(e, self.available_flows_tree))
        self.chosen_flows_tree.bind('<Motion>', lambda e: self.show_tooltip(e, self.chosen_flows_tree))

        self.available_flows_tree.bind('<Button-1>', self.on_treeview_click)
        self.chosen_flows_tree.bind('<Button-1>', self.on_treeview_click)

    

    def choose_flow_file(self, entry_widget):
        print("Extracting all your available activities!")
        file_selected = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if file_selected:
            entry_widget.delete(0, tk.END)  # Clear the current entry
            entry_widget.insert(0, file_selected)  # Insert the selected file path
            available_flows = pull_activities(file_selected)  # Call pull_activities with the file path
            bordered_edit_text = '▌Edit▐'  # Unicode characters for left and right border

            for index, activity in enumerate(available_flows):
                tag = 'oddrow' if index % 2 else ''  # Apply tag for alternating row colors
                print(activity[0])
                self.available_flows_tree.insert('', tk.END, values=(activity[0], bordered_edit_text), tags=(tag,))

            # Call the stripe function for the available activities tree
            self.stripe_rows(self.available_flows_tree)
            self.stripe_rows(self.chosen_flows_tree)
            self.style_edit_column(self.available_flows_tree)

    def show_tooltip(self, event, tree):
        row_id = tree.identify_row(event.y)
        if row_id:
            item_text = tree.item(row_id, 'values')[0]
            create_tooltip(self.available_flows_tree)
            create_tooltip(self.chosen_flows_tree)


    def create_flow(self):
        self.root.withdraw()
        activity_manager_instance = ActivityManager()
        activity_manager_instance.run()


    def run_suite(self):
        # Retrieve URL from the URL entry
        url = self.url_name_entry.get()
        init_path = self.init_entry.get()
        print(f"URL: {url}")
        # Get all the flow names from the chosen flows tree
        flow_names = [self.chosen_flows_tree.item(item_id, 'values')[0] for item_id in self.chosen_flows_tree.get_children()]
        print("Chosen flows:")
        flow_ids = []
        path = (flow_names[0].split('PATH : '))[1]
        flow_path = os.path.relpath(path, project_path)
        flow_path = os.path.join('.', flow_path)
        flow_path.replace('\\', '/')
        print(f"The flow path to be written to init properties is : {flow_path}")
        for flow_name in flow_names:
            flow_ids.append((flow_name.split('PATH : ')[0]).strip())

        print(f"The flow ids are : {flow_ids}") 
        flow_statement = ",".join(flow_ids)
        print(f"The flow statement to be written to init properties is : {flow_statement}")
        if not init_path:
            additional_path = '/src/init.properties'
            init_path = os.path.join(project_path, additional_path.strip("/"))
        write_status = write_init(init_path, url, flow_path, flow_statement)
        if write_status:
            print("\n I'll try to run your PAF script now! \n\n")
            file_run = run_file()
            print(f"The file run result is : {file_run}")
            if file_run:
                self.open_report_button.pack(side=tk.LEFT, padx=5)



    def choose_init_file(self, entry):
        # Allow only .properties files to be selected
        filename = filedialog.askopenfilename(filetypes=[("Properties files", "*.properties")])
        if filename:
            if filename.endswith('.properties'):
                entry.delete(0, tk.END)
                entry.insert(0, filename)
            else:
                messagebox.showerror("Invalid File", "Please select an init.properties file")



    def delete_from_chosen_flows(self, event):
        tree = event.widget
        item_id = tree.focus()
        if item_id:
            tree.delete(item_id)

    def on_treeview_click(self, event):
        item_id = event.widget.identify_row(event.y)
        column = event.widget.identify_column(event.x)
        if item_id and column == "#2":  # Assuming '#2' is the 'Edit' column
            activity_name = event.widget.item(item_id, 'values')[0]
            self.edit_activity(activity_name, event.widget)


    def update_chosen_flows(self):
        for i, item in enumerate(self.chosen_flows_tree.get_children()):
            tag = 'oddrow' if i % 2 else ''
            print(f"The item is : {item}")
            self.chosen_flows_tree.item(item, tags=(tag,))

    def add_to_chosen_flows(self, event):
        tree = event.widget
        item_id = tree.focus()
        if item_id:
            item_values = tree.item(item_id, 'values')
            activity_name = item_values[0]
            full_text = f"{activity_name}"
            print(f"Chosen item id : {item_id} and activity name : {full_text}")
            self.chosen_flows_tree.insert('', tk.END, values=(full_text,), tags=('oddrow',))
            self.update_chosen_flows()

    def style_edit_column(self, tree):
        tree.tag_configure('editTag', background='lightblue', font=('Arial', 10, 'bold'))  # Set background color and bold font

    def stripe_rows(self, tree):
        tree.tag_configure('oddrow', background='#f0f0f0')

    def bordered_edit_text(self):
        return '▌Edit▐'

    def edit_activity(activity_name):
        # Implementation of edit_activity
        # Use activity_name as needed
        print(f"Edit activity: {activity_name}")

    def edit_activity(activity_name, tree):
        # Implementation of edit_activity
        # Use both activity_name and tree as needed
        print(f"Edit activity: {activity_name} from {tree}")


    def run(self):
        # Run the application
        self.root.mainloop()


if __name__ == "__main__":
    TestcaseManagerInstance = TestcaseManager()
    TestcaseManagerInstance.run()