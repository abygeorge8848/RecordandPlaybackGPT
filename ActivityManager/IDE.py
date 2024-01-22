import tkinter as tk
from tkinter import filedialog, ttk

def create_activity():
    # Implement the function to create an activity
    pass

def add_flow():
    # Implement the function to add a flow
    pass

def choose_file(entry):
    filename = filedialog.askopenfilename()
    entry.delete(0, tk.END)
    entry.insert(0, filename)

def choose_folder(entry):
    foldername = filedialog.askdirectory()
    entry.delete(0, tk.END)
    entry.insert(0, foldername)

def add_to_chosen_activities(event):
    tree = event.widget
    item_id = tree.focus()
    if item_id:
        activity_name = tree.item(item_id, 'values')[0]
        chosen_activities_tree.insert('', tk.END, values=(activity_name, 'Edit'))

def delete_from_chosen_activities(event):
    tree = event.widget
    item_id = tree.focus()
    if item_id:
        tree.delete(item_id)
    
def on_treeview_click(event, tree):
    # Identify the item row where the click happened
    item_id = event.widget.identify_row(event.y)
    if item_id:
        # Set the focus to the clicked item
        event.widget.focus(item_id)

        # Check if the click is on the 'Edit' column
        if event.widget.identify_column(event.x) == "#2":  # '#2' is the 'Edit' column
            x, y, width, height = event.widget.bbox(item_id, column="#2")
            if x <= event.x < x + width:
                activity_name = event.widget.item(item_id, 'values')[0]
                edit_activity(activity_name, tree)

def update_chosen_activities():
    for i, item in enumerate(chosen_activities_tree.get_children()):
        tag = 'oddrow' if i % 2 else ''
        chosen_activities_tree.item(item, tags=(tag,))
        chosen_activities_tree.set(item, column='Edit', value=bordered_edit_text)

def add_to_chosen_activities(event):
    tree = event.widget
    item_id = tree.focus()
    if item_id:
        activity_name = tree.item(item_id, 'values')[0]
        chosen_activities_tree.insert('', tk.END, values=(activity_name, bordered_edit_text), tags=('oddrow',))
        update_chosen_activities()

def style_edit_column(tree):
    tree.tag_configure('editTag', background='lightblue', font=('Arial', 10, 'bold'))  # Set background color and bold font

def stripe_rows(tree):
    tree.tag_configure('oddrow', background='#f0f0f0')

def bordered_edit_text():
    return '▌Edit▐'

def edit_activity(activity_name, tree):
    print(f"Edit activity: {activity_name} from {tree}")

def generate_excel():
    pass

def duplicate_excel():
    pass

# Create the main window
root = tk.Tk()
root.title("Testcase Manager")
style = ttk.Style()
style.theme_use('clam')

# Navbar frame
navbar_frame = tk.Frame(root)
navbar_frame.pack(padx=12, pady=2, fill=tk.X)

add_flow_button = tk.Button(navbar_frame, text="Confirm Testcase", command=add_flow)
add_flow_button.pack(side=tk.LEFT)

create_activity_button = tk.Button(navbar_frame, text="Create Activity", command=create_activity)
create_activity_button.pack(side=tk.RIGHT)

navbar_separator = ttk.Separator(root, orient='horizontal')
navbar_separator.pack(fill=tk.X, pady=1)

# Frame for Flow name and description
flow_frame = ttk.Frame(root)
flow_frame.pack(padx=12, pady=5, fill=tk.X)

flow_name_label = ttk.Label(flow_frame, text="Flow Name")
flow_name_label.pack(side=tk.LEFT, padx=(0, 10))
flow_name_entry = ttk.Entry(flow_frame)
flow_name_entry.pack(side=tk.LEFT, padx=(0, 10))

flow_description_label = ttk.Label(flow_frame, text="Flow Description")
flow_description_label.pack(side=tk.LEFT, padx=(10, 10))
flow_description_entry = ttk.Entry(flow_frame)
flow_description_entry.pack(side=tk.LEFT)

# Frame for file selection
file_frame = ttk.Frame(root)
file_frame.pack(padx=12, pady=5, fill=tk.X)

activityfolder_entry = ttk.Entry(file_frame)
activityfolder_entry.pack(side=tk.LEFT, padx=(0, 10))
activityfolder_button = tk.Button(file_frame, text="Choose Folder", command=lambda: choose_folder(activityfolder_entry))
activityfolder_button.pack(side=tk.LEFT)

file2_entry = ttk.Entry(file_frame)
file2_entry.pack(side=tk.LEFT, padx=(20, 10))
file2_button = tk.Button(file_frame, text="Choose File", command=lambda: choose_file(file2_entry))
file2_button.pack(side=tk.LEFT)

# Frame for Treeviews and their labels
listbox_frame = ttk.Frame(root)
listbox_frame.pack(padx=12, pady=5, fill=tk.BOTH, expand=True)

# Frame for Available Activities
available_activities_frame = ttk.Frame(listbox_frame)
available_activities_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

available_activities_label = ttk.Label(available_activities_frame, text="Available Activities")
available_activities_label.pack(side=tk.TOP, fill=tk.X)

available_activities_tree = ttk.Treeview(available_activities_frame, columns=('Activity', 'Edit'), show='headings')
available_activities_tree.heading('Activity', text='Activity')
available_activities_tree.heading('Edit', text='Edit')
available_activities_tree.column('Edit', width=100, anchor='center')

av_act_vscroll = ttk.Scrollbar(available_activities_frame, orient="vertical", command=available_activities_tree.yview)
av_act_hscroll = ttk.Scrollbar(available_activities_frame, orient="horizontal", command=available_activities_tree.xview)
available_activities_tree.configure(yscrollcommand=av_act_vscroll.set, xscrollcommand=av_act_hscroll.set)
av_act_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
av_act_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
available_activities_tree.pack(fill=tk.BOTH, expand=True)

# Frame for Chosen Activities
chosen_activities_frame = ttk.Frame(listbox_frame)
chosen_activities_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

chosen_activities_label = ttk.Label(chosen_activities_frame, text="Chosen Activities")
chosen_activities_label.pack(side=tk.TOP, fill=tk.X)

chosen_activities_tree = ttk.Treeview(chosen_activities_frame, columns=('Activity', 'Edit'), show='headings')
chosen_activities_tree.heading('Activity', text='Activity')
chosen_activities_tree.heading('Edit', text='Edit')
chosen_activities_tree.column('Edit', width=100, anchor='center')

ch_act_vscroll = ttk.Scrollbar(chosen_activities_frame, orient="vertical", command=chosen_activities_tree.yview)
ch_act_hscroll = ttk.Scrollbar(chosen_activities_frame, orient="horizontal", command=chosen_activities_tree.xview)
chosen_activities_tree.configure(yscrollcommand=ch_act_vscroll.set, xscrollcommand=ch_act_hscroll.set)
ch_act_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
ch_act_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
chosen_activities_tree.pack(fill=tk.BOTH, expand=True)

# Change cursor on hover over 'Edit'
def change_cursor(event):
    if event.widget.identify_column(event.x) == "#2":
        event.widget.config(cursor="hand2")
    else:
        event.widget.config(cursor="")

available_activities_tree.bind('<Motion>', change_cursor)
chosen_activities_tree.bind('<Motion>', change_cursor)

# Binding events
available_activities_tree.bind('<Double-1>', add_to_chosen_activities)
chosen_activities_tree.bind('<Double-1>', delete_from_chosen_activities)
available_activities_tree.bind('<Button-1>', lambda e: on_treeview_click(e, 'Available'))
chosen_activities_tree.bind('<Button-1>', lambda e: on_treeview_click(e, 'Chosen'))

# Populate the available activities Treeview
available_activities = ["Activity 1", "Activity 2", "Activity 3", "Activity 4", "Activity 5"]
bordered_edit_text = '▌Edit▐' # Unicode characters for left and right border

for index, activity in enumerate(available_activities):
    tag = 'oddrow' if index % 2 else ''  # Apply tag for alternating row colors
    available_activities_tree.insert('', tk.END, values=(activity, bordered_edit_text), tags=(tag,))

# Call the stripe function for the available activities tree
stripe_rows(available_activities_tree)
stripe_rows(chosen_activities_tree)
# Call the style function for the available activities tree
style_edit_column(available_activities_tree)

# Run the application
root.mainloop()
