import tkinter as tk
from tkinter import filedialog, ttk, messagebox, Toplevel, Label, Entry, Button
from pull_files import pull_activities
from effects import create_tooltip
from xml_parsing import retrieve_activities, insert_recorder_id, update_activity_paths
from excel import create_excel, is_legitimate_path, extract_data_and_write_to_excel, create_duplicates
import os


def choose_folder(entry_widget):
    print("Extracting all your available activities!")
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry_widget.delete(0, tk.END)  # Clear the current entry
        entry_widget.insert(0, folder_selected)  # Insert the selected folder path
        available_flows = pull_activities(folder_selected)  # Call pull_activities with the folder path
        bordered_edit_text = '▌Edit▐' # Unicode characters for left and right border

        for index, activity in enumerate(available_flows):
            tag = 'oddrow' if index % 2 else ''  # Apply tag for alternating row colors
            #activity_path = f"{activity[0]}  -  {activity[1]}"
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

def add_flow():
    # Implement the function to add a flow
    pass

def choose_file(entry):
    filename = filedialog.askopenfilename()
    entry.delete(0, tk.END)
    entry.insert(0, filename)


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


def generate_excel():
    base_excel_path='C:\\Users\\u1138322\\PAF\\ProjectContainer\\SampleProject\\excel'
    selected_items = chosen_flows_tree.selection()  # Get selected items in the treeview
    if selected_items:
        selected_flow = chosen_flows_tree.item(selected_items[0], 'values')[0]
        print(f"Generating excel for: {selected_flow}")
        parts = selected_flow.split('   PATH : ')
        flow_name = parts[0]
        path = parts[1]        
        base_excel_path = create_excel(flow_name, base_excel_path)
        activity_list = retrieve_activities(flow_name, path)
        updated_activity_list = update_activity_paths(activity_list, base_excel_path)
        insert_recorder_id(updated_activity_list)
        extract_data_and_write_to_excel(updated_activity_list, base_excel_path)
        

    else:
        # If no flow is selected, show an alert
        messagebox.showinfo("No Selection", "Please select a flow you want to generate the excel for")

def duplicate_excel():
    base_excel_path='C:\\Users\\u1138322\\PAF\\ProjectContainer\\SampleProject\\excel'
    selected_items = chosen_flows_tree.selection()  # Get selected items in the treeview
    if selected_items:
        selected_flow = chosen_flows_tree.item(selected_items[0], 'values')[0]
        print(f"Generating excel for: {selected_flow}")
        parts = selected_flow.split('   PATH : ')
        flow_name = parts[0]
        path = parts[1]
        file_name = f"{flow_name}.xlsx"
        file_path = os.path.join(base_excel_path, file_name)
        if not os.path.isfile(file_path):
            messagebox.showinfo("File Not Found", "There is no excel for this flow. Please generate an excel before you duplicate it.")
        else:
            open_duplicate_window(file_path, chosen_flows_tree)
    
    else:
        # If no flow is selected, show an alert
        messagebox.showinfo("No Selection", "Please select a flow you want to generate the excel for")

def open_duplicate_window(base_excel_path, chosen_flows_tree):
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
    duplicate_button = ttk.Button(content_frame, text="Duplicate", command=lambda: duplicate_file(duplicate_window, num_duplicates_entry, base_excel_path, chosen_flows_tree))
    duplicate_button.pack(side=tk.TOP, pady=(0, 10))

    # Center the window on the screen
    center_window_on_screen(duplicate_window)

def center_window_on_screen(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))


def duplicate_file(duplicate_window, num_duplicates_entry, base_excel_path, chosen_flows_tree):
    try:
        num_duplicates = int(num_duplicates_entry.get())
    except ValueError:
        messagebox.showinfo("Invalid Input", "Please enter a valid number")
        return
    # Close the duplicate window
    duplicate_window.destroy()
    # Call the new function for duplicating the file
    sheets = create_duplicates(num_duplicates, base_excel_path)






# Create the main window
root = tk.Tk()
root.title("Flow Manager")
style = ttk.Style()
style.theme_use('clam')

# Create navbar frame
navbar_frame = tk.Frame(root)
navbar_frame.pack(padx=12, pady=2, fill=tk.X)

url_name_label = ttk.Label(navbar_frame, text="Enter URL")
url_name_label.pack(side=tk.LEFT, padx=(0, 10))
url_name_entry = ttk.Entry(navbar_frame)
url_name_entry.pack(side=tk.LEFT, padx=(0, 10))

add_flow_button = tk.Button(navbar_frame, text="Run", command=add_flow)
add_flow_button.pack(side=tk.LEFT)

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
flow_button = ttk.Button(file_frame, text="Choose Folder", command=lambda: choose_folder(flow_entry))
flow_button.pack(side=tk.LEFT)

flow_button = ttk.Entry(file_frame)
testcase_button = ttk.Button(file_frame, text="Choose File", command=lambda: choose_file(flow_button))
testcase_button.pack(side=tk.RIGHT)
flow_button.pack(side=tk.RIGHT, padx=(20, 10))


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

# Create frame for Excel generation and folder selection
excel_frame = ttk.Frame(root)
excel_frame.pack(padx=12, pady=5, fill=tk.X)

generate_excel_button = ttk.Button(excel_frame, text="Generate Excel", command=generate_excel)
generate_excel_button.pack(side=tk.LEFT, padx=(0, 10))

duplicate_excel_button = ttk.Button(excel_frame, text="Duplicate Excel", command=duplicate_excel)
duplicate_excel_button.pack(side=tk.LEFT)

# Run the application
root.mainloop()