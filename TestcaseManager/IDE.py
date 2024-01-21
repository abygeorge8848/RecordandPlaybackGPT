import tkinter as tk
from tkinter import filedialog, ttk
from tkinter.ttk import Separator


def create_activity():
    # Implement the function to create an activity
    pass

def add_flow():
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
    widget = event.widget
    index = int(widget.curselection()[0])
    value = widget.get(index)
    chosen_activities_listbox.insert(tk.END, value)
    colorize_listbox(chosen_activities_listbox)

def delete_from_chosen_activities(event):
    widget = event.widget
    index = int(widget.curselection()[0])
    widget.delete(index)
    colorize_listbox(chosen_activities_listbox)

def colorize_listbox(listbox):
    for i in range(listbox.size()):
        listbox.itemconfig(i, {'bg': '#f0f0f0' if i % 2 == 0 else 'white'})


def generate_excel():
    # Implement function to generate excel
    pass

def duplicate_excel():
    # Implement function to duplicate excel
    pass

# Create the main window
root = tk.Tk()
root.title("Testcase Manager")
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

create_testcase_button = tk.Button(navbar_frame, text="Create Testcase", command=create_activity)
create_testcase_button.pack(side=tk.RIGHT)
navbar_separator = ttk.Separator(root, orient='horizontal')
navbar_separator.pack(fill=tk.X, pady=1)

# Create frame for Flow name and description
flow_frame = ttk.Frame(root)
flow_frame.pack(padx=12, pady=5, fill=tk.X)


# Create frame for file selection
file_frame = ttk.Frame(root)
file_frame.pack(padx=12, pady=5, fill=tk.X)

file1_entry = ttk.Entry(file_frame)
file1_entry.pack(side=tk.LEFT, padx=(0, 10))
file1_button = ttk.Button(file_frame, text="Choose Folder", command=lambda: choose_folder(file1_entry))
file1_button.pack(side=tk.LEFT)

file2_entry = ttk.Entry(file_frame)
file2_entry.pack(side=tk.LEFT, padx=(20, 10))
file2_button = ttk.Button(file_frame, text="Choose File", command=lambda: choose_file(file2_entry))
file2_button.pack(side=tk.LEFT)

# Create frame for Listboxes and their labels
listbox_frame = ttk.Frame(root)
listbox_frame.pack(padx=12, pady=5, fill=tk.BOTH, expand=True)

# Label and Listbox for Available Activities
available_activities_frame = ttk.Frame(listbox_frame)
available_activities_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

available_activities_label = ttk.Label(available_activities_frame, text="Available Testcases")
available_activities_label.pack(side=tk.TOP, fill=tk.X)

# Creating Scrollbars
av_act_vscroll = ttk.Scrollbar(available_activities_frame, orient="vertical")
av_act_hscroll = ttk.Scrollbar(available_activities_frame, orient="horizontal")
available_activities_listbox = tk.Listbox(available_activities_frame, yscrollcommand=av_act_vscroll.set, xscrollcommand=av_act_hscroll.set)
av_act_vscroll.config(command=available_activities_listbox.yview)
av_act_hscroll.config(command=available_activities_listbox.xview)

# Packing Scrollbars
av_act_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
av_act_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
available_activities_listbox.pack(fill=tk.BOTH, expand=True)
available_activities_listbox.bind('<Double-1>', add_to_chosen_activities)

# Frame for Chosen Activities
chosen_activities_frame = ttk.Frame(listbox_frame)
chosen_activities_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

chosen_activities_label = ttk.Label(chosen_activities_frame, text="Chosen Testcases")
chosen_activities_label.pack(side=tk.TOP, fill=tk.X)

# Creating Scrollbars
ch_act_vscroll = ttk.Scrollbar(chosen_activities_frame, orient="vertical")
ch_act_hscroll = ttk.Scrollbar(chosen_activities_frame, orient="horizontal")
chosen_activities_listbox = tk.Listbox(chosen_activities_frame, yscrollcommand=ch_act_vscroll.set, xscrollcommand=ch_act_hscroll.set)
ch_act_vscroll.config(command=chosen_activities_listbox.yview)
ch_act_hscroll.config(command=chosen_activities_listbox.xview)

# Packing Scrollbars
ch_act_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
ch_act_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
chosen_activities_listbox.pack(fill=tk.BOTH, expand=True)
chosen_activities_listbox.bind('<Double-1>', delete_from_chosen_activities)

# [Dummy data for available activities, Excel generation and folder selection frames...]
available_activities = ["Testcase 1", "Testcase 2", "Testcase 3", "Testcase 4", "Testcase 5"]
for activity in available_activities:
    available_activities_listbox.insert(tk.END, activity)
colorize_listbox(available_activities_listbox)

# Create frame for Excel generation and folder selection
excel_frame = ttk.Frame(root)
excel_frame.pack(padx=12, pady=5, fill=tk.X)

generate_excel_button = ttk.Button(excel_frame, text="Generate Excel", command=generate_excel)
generate_excel_button.pack(side=tk.LEFT, padx=(0, 10))

duplicate_excel_button = ttk.Button(excel_frame, text="Duplicate Excel", command=duplicate_excel)
duplicate_excel_button.pack(side=tk.LEFT)

folder_entry = ttk.Entry(excel_frame)
folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 10))

choose_folder_button = ttk.Button(excel_frame, text="Choose Folder", command=lambda: choose_folder(folder_entry))
choose_folder_button.pack(side=tk.LEFT)

# Run the application
root.mainloop()