import tkinter as tk
from tkinter import filedialog, ttk, messagebox, Toplevel, Label, Entry, Button
from project_interaction import pull_activities, write_init
from effects import create_tooltip
from RunPAF import run_file, report_open
from xml_parsing import retrieve_activities, insert_recorder_id, update_activity_paths
from excel import create_excel, is_legitimate_path, extract_data_and_write_to_excel, create_duplicates
import os


project_path = "C:/Users/u1138322/PAF/ProjectContainer/SampleProject"

def choose_flow_file(entry_widget):
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
            available_flows_tree.insert('', tk.END, values=(activity[0], bordered_edit_text), tags=(tag,))

        # Call the stripe function for the available activities tree
        stripe_rows(available_flows_tree)
        stripe_rows(chosen_flows_tree)
        style_edit_column(available_flows_tree)

def show_tooltip(event, tree):
    row_id = tree.identify_row(event.y)
    if row_id:
        item_text = tree.item(row_id, 'values')[0]
        create_tooltip(available_flows_tree)
        create_tooltip(chosen_flows_tree)


def create_flow():
    # Implement the function to create an activity
    pass

def run_suite():
    # Retrieve URL from the URL entry
    url = url_name_entry.get()
    init_path = init_entry.get()
    print(f"URL: {url}")
    # Get all the flow names from the chosen flows tree
    flow_names = [chosen_flows_tree.item(item_id, 'values')[0] for item_id in chosen_flows_tree.get_children()]
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
            open_report_button.pack(side=tk.LEFT, padx=5)
    

    


def choose_init_file(entry):
    # Allow only .properties files to be selected
    filename = filedialog.askopenfilename(filetypes=[("Properties files", "*.properties")])
    if filename:
        if filename.endswith('.properties') and filename.startswith('init'):
            entry.delete(0, tk.END)
            entry.insert(0, filename)
        else:
            messagebox.showerror("Invalid File", "Please select an init.properties file")



def delete_from_chosen_flows(event):
    tree = event.widget
    item_id = tree.focus()
    if item_id:
        tree.delete(item_id)
    
def on_treeview_click(event):
    item_id = event.widget.identify_row(event.y)
    column = event.widget.identify_column(event.x)
    if item_id and column == "#2":  # Assuming '#2' is the 'Edit' column
        activity_name = event.widget.item(item_id, 'values')[0]
        edit_activity(activity_name, event.widget)


def update_chosen_flows():
    for i, item in enumerate(chosen_flows_tree.get_children()):
        tag = 'oddrow' if i % 2 else ''
        print(f"The item is : {item}")
        chosen_flows_tree.item(item, tags=(tag,))

def add_to_chosen_flows(event):
    tree = event.widget
    item_id = tree.focus()
    if item_id:
        item_values = tree.item(item_id, 'values')
        activity_name = item_values[0]
        full_text = f"{activity_name}"
        print(f"Chosen item id : {item_id} and activity name : {full_text}")
        chosen_flows_tree.insert('', tk.END, values=(full_text,), tags=('oddrow',))
        update_chosen_flows()

def style_edit_column(tree):
    tree.tag_configure('editTag', background='lightblue', font=('Arial', 10, 'bold'))  # Set background color and bold font

def stripe_rows(tree):
    tree.tag_configure('oddrow', background='#f0f0f0')

def bordered_edit_text():
    return '▌Edit▐'

def edit_activity(activity_name):
    # Implementation of edit_activity
    # Use activity_name as needed
    print(f"Edit activity: {activity_name}")

def edit_activity(activity_name, tree):
    # Implementation of edit_activity
    # Use both activity_name and tree as needed
    print(f"Edit activity: {activity_name} from {tree}")




# Create the main window
root = tk.Tk()
root.title("Flow Manager")
style = ttk.Style()
style.theme_use('clam')


# Create navbar frame
navbar_frame = tk.Frame(root)
navbar_frame.pack(padx=12, pady=2, fill=tk.X)

open_report_button = tk.Button(navbar_frame, text="Open Report", command=report_open)

url_name_label = ttk.Label(navbar_frame, text="Enter URL")
url_name_label.pack(side=tk.LEFT, padx=(0, 10))
url_name_entry = ttk.Entry(navbar_frame)
url_name_entry.pack(side=tk.LEFT, padx=(0, 10))

run_button = tk.Button(navbar_frame, text="Run", command=run_suite)
run_button.pack(side=tk.LEFT)

create_Flow_button = tk.Button(navbar_frame, text="Create Flow", command=create_flow)
create_Flow_button.pack(side=tk.RIGHT)
navbar_separator = ttk.Separator(root, orient='horizontal')
navbar_separator.pack(fill=tk.X, pady=1)

# Create frame for Flow name and description
flow_frame = ttk.Frame(root)
flow_frame.pack(padx=12, pady=5, fill=tk.X)


# Create frame for file selection
file_frame = ttk.Frame(root)
file_frame.pack(padx=12, pady=5, fill=tk.X)

flow_entry = ttk.Entry(file_frame)
flow_entry.pack(side=tk.LEFT, padx=(0, 10))
flow_button = ttk.Button(file_frame, text="Choose Flow File", command=lambda: choose_flow_file(flow_entry))
flow_button.pack(side=tk.LEFT)

init_entry = ttk.Entry(file_frame)
testcase_button = ttk.Button(file_frame, text="Choose Init File", command=lambda: choose_init_file(init_entry))
testcase_button.pack(side=tk.RIGHT)
init_entry.pack(side=tk.RIGHT, padx=(20, 10))


# Create frame for Listboxes and their labels
listbox_frame = ttk.Frame(root)
listbox_frame.pack(padx=12, pady=5, fill=tk.BOTH, expand=True)

# Frame for Available Activities
available_flows_frame = ttk.Frame(listbox_frame)
available_flows_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

available_flows_label = ttk.Label(available_flows_frame, text="Available Flows")
available_flows_label.pack(side=tk.TOP, fill=tk.X)

available_flows_tree = ttk.Treeview(available_flows_frame, columns=('Flow', 'Edit'), show='headings')
available_flows_tree.heading('Flow', text='Flow')
available_flows_tree.heading('Edit', text='Edit')
available_flows_tree.column('Flow', width=200) 
available_flows_tree.column('Edit', width=100, anchor='center')

av_act_vscroll = ttk.Scrollbar(available_flows_frame, orient="vertical", command=available_flows_tree.yview)
av_act_hscroll = ttk.Scrollbar(available_flows_frame, orient="horizontal", command=available_flows_tree.xview)
available_flows_tree.configure(xscrollcommand=av_act_hscroll.set)
av_act_hscroll.configure(command=available_flows_tree.xview)
av_act_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
av_act_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
available_flows_tree.pack(fill=tk.BOTH, expand=True)

# Frame for Chosen Activities
chosen_flows_frame = ttk.Frame(listbox_frame)
chosen_flows_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

chosen_flows_label = ttk.Label(chosen_flows_frame, text="Chosen Flows")
chosen_flows_label.pack(side=tk.TOP, fill=tk.X)

chosen_flows_tree = ttk.Treeview(chosen_flows_frame, columns=('Flow'), show='headings')
chosen_flows_tree.heading('Flow', text='Flow')
chosen_flows_tree.column('Flow', width=300, stretch=tk.YES)

ch_act_vscroll = ttk.Scrollbar(chosen_flows_frame, orient="vertical", command=chosen_flows_tree.yview)
ch_act_hscroll = ttk.Scrollbar(chosen_flows_frame, orient="horizontal", command=chosen_flows_tree.xview)
chosen_flows_tree.configure(xscrollcommand=ch_act_hscroll.set)
ch_act_hscroll.configure(command=chosen_flows_tree.xview)
ch_act_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
ch_act_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
chosen_flows_tree.pack(fill=tk.BOTH, expand=True)

# Change cursor on hover over 'Edit'
def change_cursor(event):
    if event.widget.identify_column(event.x) == "#2":
        event.widget.config(cursor="hand2")
    else:
        event.widget.config(cursor="")

available_flows_tree.bind('<Motion>', change_cursor)
chosen_flows_tree.bind('<Motion>', change_cursor)

# Binding events
available_flows_tree.bind('<Double-1>', add_to_chosen_flows)
chosen_flows_tree.bind('<Double-1>', delete_from_chosen_flows)
available_flows_tree.bind('<Motion>', lambda e: show_tooltip(e, available_flows_tree))
chosen_flows_tree.bind('<Motion>', lambda e: show_tooltip(e, chosen_flows_tree))

available_flows_tree.bind('<Button-1>', on_treeview_click)
chosen_flows_tree.bind('<Button-1>', on_treeview_click)


# Run the application
root.mainloop()