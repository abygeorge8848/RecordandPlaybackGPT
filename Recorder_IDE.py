import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from Recorder import start_recording, stop_and_show_records, create_xpath, pause_recording_main, resume_recording_main
from RunPAF import run_file, report_open
from serverConn import conn
import time


def start_record():
    start_button.pack_forget()
    stop_button.pack(side=tk.LEFT, padx=5)
    pause_resume_button.config(text="Pause", command=pause_recording)
    pause_resume_button.pack(side=tk.LEFT, padx=5)
    update_steps("Start Recording")
    disable_dropdown_options()
    url = url_entry.get()
    start_recording(url)

def stop_recording():
    stop_button.pack_forget()
    pause_resume_button.pack_forget()
    dropdown_frame.pack_forget()
    update_steps("Stop Recording")
    disable_dropdown_options()
    response = stop_and_show_records()
    if response:
        start_button.pack_forget()
        run_button.pack(side=tk.LEFT, padx=5)

def pause_recording():
    pause_recording_main()
    pause_resume_button.config(text="Resume", command=resume_recording)
    dropdown_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
    update_steps("Pause Recording")
    enable_dropdown_options()

def resume_recording():
    resume_recording_main()
    pause_resume_button.config(text="Pause", command=pause_recording)
    dropdown_frame.pack_forget()
    variable_value_frame.pack_forget()
    get_text_frame.pack_forget()
    validation_exists_frame.pack_forget()
    validation_not_exists_frame.pack_forget()
    validation_equals_frame.pack_forget()
    validation_not_equals_frame.pack_forget()
    validation_num_equals_frame.pack_forget()
    validation_num_not_equals_frame.pack_forget()
    update_steps("Resume Recording")
    disable_dropdown_options()

def run_script():
    print("\n I'll try to run your PAF script now! \n\n")
    file_run = run_file()
    print(f"The file run result is : {file_run}")
    if file_run:
        run_button.pack_forget()
        open_report_button.pack(side=tk.LEFT, padx=5)

def enable_dropdown_options():
    dropdown.configure(state='readonly')

def disable_dropdown_options():
    dropdown.configure(state='disabled')
    get_text_frame.pack_forget()
    validation_exists_frame.pack_forget()

def show_validation_menu(event):
    # Display the menu if the selected option is "validation"
    if dropdown_var.get() == "validation":
        x = dropdown.winfo_rootx()
        y = dropdown.winfo_rooty() + dropdown.winfo_height()
        validation_menu.tk_popup(x, y, 0)

def create_validation_menu():
    # Create the validation submenu
    menu = tk.Menu(root, tearoff=0)
    for option in ["exists", "not-exists", "equals", "not-equals", "num-equals", "num-not-equals"]:
        menu.add_command(label=option, command=lambda val=option: handle_validation_option(val))
    return menu

def on_validation_menu_selection(value):
    # Handle the selection from the validation menu
    print(value)
    validation_menu.unpost()

def handle_validation_option(selected_validation):
    if recording_paused():
        if selected_validation == "exists":
            validation_exists_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            get_text_frame.pack_forget()
            validation_not_exists_frame.pack_forget()
            validation_equals_frame.pack_forget()
            validation_not_equals_frame.pack_forget()
            validation_num_equals_frame.pack_forget()
            validation_num_not_equals_frame.pack_forget()
            variable_value_frame.pack_forget()
        elif selected_validation == "not-exists":
            validation_not_exists_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            get_text_frame.pack_forget()
            validation_exists_frame.pack_forget()
            validation_equals_frame.pack_forget()
            validation_not_equals_frame.pack_forget()
            validation_num_equals_frame.pack_forget()
            validation_num_not_equals_frame.pack_forget()
            variable_value_frame.pack_forget()
        elif selected_validation == "equals":
            validation_equals_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            get_text_frame.pack_forget()
            validation_exists_frame.pack_forget()
            validation_not_exists_frame.pack_forget()
            validation_not_equals_frame.pack_forget()
            validation_num_equals_frame.pack_forget()
            validation_num_not_equals_frame.pack_forget()
            variable_value_frame.pack_forget()
        elif selected_validation == "not-equals":
            validation_not_equals_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            get_text_frame.pack_forget()
            validation_exists_frame.pack_forget()
            validation_not_exists_frame.pack_forget()
            validation_equals_frame.pack_forget()
            validation_num_equals_frame.pack_forget()
            validation_num_not_equals_frame.pack_forget()
            variable_value_frame.pack_forget()
        elif selected_validation == "num-equals":
            validation_num_equals_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            get_text_frame.pack_forget()
            validation_exists_frame.pack_forget()
            validation_not_exists_frame.pack_forget()
            validation_equals_frame.pack_forget()
            validation_not_equals_frame.pack_forget()
            validation_num_not_equals_frame.pack_forget()
            variable_value_frame.pack_forget()
        elif selected_validation == "num-not-equals":
            validation_num_not_equals_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            get_text_frame.pack_forget()
            validation_exists_frame.pack_forget()
            validation_not_exists_frame.pack_forget()
            validation_equals_frame.pack_forget()
            validation_not_equals_frame.pack_forget()
            validation_num_equals_frame.pack_forget()
            variable_value_frame.pack_forget()
        else:
            variable_value_frame.pack_forget()
            get_text_frame.pack_forget()
            validation_exists_frame.pack_forget()
            validation_not_exists_frame.pack_forget()
            validation_equals_frame.pack_forget()
            validation_not_equals_frame.pack_forget()
            validation_num_equals_frame.pack_forget()
            validation_num_not_equals_frame.pack_forget()
    

def handle_dropdown_selection(event):
    if recording_paused():
        selected = dropdown_var.get()
        if selected == "getText":
            get_text_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            validation_exists_frame.pack_forget()
            validation_not_exists_frame.pack_forget()
            validation_equals_frame.pack_forget()
            validation_not_equals_frame.pack_forget()
            validation_num_equals_frame.pack_forget()
            validation_num_not_equals_frame.pack_forget()
            variable_value_frame.pack_forget()
        elif selected == "variable-value":
            variable_value_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            validation_num_not_equals_frame.pack_forget()
            get_text_frame.pack_forget()
            validation_exists_frame.pack_forget()
            validation_not_exists_frame.pack_forget()
            validation_equals_frame.pack_forget()
            validation_not_equals_frame.pack_forget()
            validation_num_equals_frame.pack_forget()
        else:
            variable_value_frame.pack_forget()
            get_text_frame.pack_forget()
            validation_exists_frame.pack_forget()
            validation_not_exists_frame.pack_forget()
            validation_equals_frame.pack_forget()
            validation_not_equals_frame.pack_forget()
            validation_num_equals_frame.pack_forget()
            validation_num_not_equals_frame.pack_forget()
    else:
        messagebox.showinfo("Alert", "Please pause the recording before entering custom steps.")

def recording_paused():
    return pause_resume_button.cget('text') == "Resume"

def get_text():
    get_text_after_checked = get_text_after_var.get()
    get_text_before_checked = get_text_before_var.get()
    variable_name = getText_variable_name_entry.get()
    xpath = create_xpath()
    now = int(time.time() * 1000)
    conn([["getText", now, xpath, variable_name, get_text_after_checked, get_text_before_checked]])
    get_text_frame.pack_forget()
    update_steps(f"Get Text: {variable_name}")

def validate_exists():
    validate_exists_after_checked = validation_exists_after_var.get()
    validate_exists_before_checked = validation_exists_before_var.get()
    validation_name = validation_exists_name_entry.get()
    validation_pass_msg = valExists_pass_msg_entry.get()
    validation_fail_msg = valExists_fail_msg_entry.get()
    xpath = create_xpath()
    now = int(time.time() * 1000)
    conn([["validation-exists", now, xpath, validation_name, validation_pass_msg, validation_fail_msg, validate_exists_after_checked, validate_exists_before_checked]])
    validation_exists_frame.pack_forget()
    update_steps(f"Validate-exists: {validation_name}")

def validate_not_exists():
    validate_not_exists_after_checked = validation_not_exists_after_var.get()
    validate_not_exists_before_checked = validation_not_exists_before_var.get()
    validation_name = validation_not_exists_name_entry.get()
    validation_pass_msg = valNotExists_pass_msg_entry.get()
    validation_fail_msg = valNotExists_fail_msg_entry.get()
    xpath = create_xpath()
    now = int(time.time() * 1000)
    conn([["validation-not-exists", now, xpath, validation_name, validation_pass_msg, validation_fail_msg, validate_not_exists_after_checked, validate_not_exists_before_checked]])
    variable_value_frame.pack_forget()
    update_steps(f"Validate-not-exists: {validation_name}")

def validate_equals():
    validate_equals_after_checked = validation_equals_after_var.get()
    validate_equals_before_checked = validation_equals_before_var.get()
    validation_name = equals_validation_name_entry.get()
    variable1 = equals_variable1_value_entry.get()
    variable2 = equals_variable2_value_entry.get()
    validation_pass_msg = equals_pass_msg_entry.get()
    validation_fail_msg = equals_fail_msg_entry.get()
    now = int(time.time() * 1000)
    conn([["validation-equals", now, validation_name, variable1, variable2, validation_pass_msg, validation_fail_msg, validate_equals_after_checked, validate_equals_before_checked]])
    validation_equals_frame.pack_forget()
    update_steps(f"validate-equals: {validation_name}")

def validate_not_equals():
    validate_not_equals_after_checked = validation_not_equals_after_var.get()
    validate_not_equals_before_checked = validation_not_equals_before_var.get()
    validation_name = not_equals_validation_name_entry.get()
    variable1 = not_equals_variable1_value_entry.get()
    variable2 = not_equals_variable2_value_entry.get()
    validation_pass_msg = not_equals_pass_msg_entry.get()
    validation_fail_msg = not_equals_fail_msg_entry.get()
    now = int(time.time() * 1000)
    conn([["validation-not-equals", now, validation_name, variable1, variable2, validation_pass_msg, validation_fail_msg, validate_not_equals_after_checked, validate_not_equals_before_checked]])
    validation_not_equals_frame.pack_forget()
    update_steps(f"validate-not-equals: {validation_name}")

def validate_num_equals():
    validate_num_equals_after_checked = validation_num_equals_after_var.get()
    validate_num_equals_before_checked = validation_num_equals_before_var.get()
    validation_name = num_equals_validation_name_entry.get()
    variable1 = num_equals_variable1_value_entry.get()
    variable2 = num_equals_variable2_value_entry.get()
    validation_pass_msg = num_equals_pass_msg_entry.get()
    validation_fail_msg = num_equals_fail_msg_entry.get()
    now = int(time.time() * 1000)
    conn([["validation-num-equals", now, validation_name, variable1, variable2, validation_pass_msg, validation_fail_msg, validate_num_equals_after_checked, validate_num_equals_before_checked]])
    validation_num_equals_frame.pack_forget()
    update_steps(f"validate-num-equals: {validation_name}")

def validate_num_not_equals():
    validate_num_not_equals_after_checked = validation_num_not_equals_after_var.get()
    validate_num_not_equals_before_checked = validation_num_not_equals_before_var.get()
    validation_name = num_not_equals_validation_name_entry.get()
    variable1 = num_not_equals_variable1_value_entry.get()
    variable2 = num_not_equals_variable2_value_entry.get()
    validation_pass_msg = num_not_equals_pass_msg_entry.get()
    validation_fail_msg = num_not_equals_fail_msg_entry.get()
    now = int(time.time() * 1000)
    conn([["validation-num-not-equals", now, validation_name, variable1, variable2, validation_pass_msg, validation_fail_msg, validate_num_not_equals_after_checked, validate_num_not_equals_before_checked]])
    validation_num_not_equals_frame.pack_forget()
    update_steps(f"validate-num-not-equals: {validation_name}")

def variable_value():
    variable_value_after_checked = variable_value_after_var.get()
    variable_value_before_checked = variable_value_before_var.get()
    variable_name = variable_value_name_entry.get()
    variable_value = variable_value_entry.get()
    now = int(time.time() * 1000)
    conn([["variable-value", now, variable_name, variable_value, variable_value_after_checked, variable_value_before_checked]])
    variable_value_frame.pack_forget()
    update_steps(f"variable-value: {variable_name}")

def update_steps(step):
    executed_steps.insert(tk.END, step)
    executed_steps.see(tk.END)




root = tk.Tk()
root.title("Recorder")

# Navigation Bar
nav_bar = tk.Frame(root)
nav_bar.pack(side=tk.TOP, fill=tk.X)

url_entry = tk.Entry(nav_bar)
url_entry.insert(0, 'http://')  # You can set a default or placeholder text if needed
url_entry.pack(side=tk.LEFT, padx=5)

start_button = tk.Button(nav_bar, text="Start", command=start_record)
run_button = tk.Button(nav_bar, text="Run Script", command=run_script)
open_report_button = tk.Button(nav_bar, text="Open Report", command=report_open)
stop_button = tk.Button(nav_bar, text="Stop", command=stop_recording)
pause_resume_button = tk.Button(nav_bar, text="Pause", command=pause_recording)

start_button.pack(side=tk.LEFT, padx=5)

# Right Sidebar
sidebar = tk.Frame(root)
sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

dropdown_var = tk.StringVar()
dropdown = ttk.Combobox(sidebar, textvariable=dropdown_var, state="readonly")
dropdown['values'] = ["getText", "variable-value", "validation"]
dropdown.bind("<<ComboboxSelected>>", handle_dropdown_selection)
dropdown.pack(fill=tk.X)

# Create the validation submenu
validation_menu = create_validation_menu()

# Bind hover event to the main dropdown
dropdown.bind("<Motion>", show_validation_menu)

dropdown_frame = tk.Frame(sidebar)
dropdown.pack(fill=tk.X)       

get_text_frame = tk.Frame(sidebar)
variable_frame = tk.Frame(get_text_frame)
variable_name_label = tk.Label(variable_frame, text="Variable Name:")
variable_name_label.pack(side=tk.LEFT, padx=5, pady=5)
getText_variable_name_entry = tk.Entry(variable_frame)
getText_variable_name_entry.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5)
variable_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
get_text_snapshot_frame = tk.Frame(get_text_frame)
get_text_snapshot_label = tk.Label(get_text_snapshot_frame, text="Snapshot")
get_text_snapshot_label.pack(side=tk.LEFT, padx=5)
get_text_after_var = tk.IntVar()
get_text_before_var = tk.IntVar()
get_text_after_check = tk.Checkbutton(get_text_snapshot_frame, text="After", variable=get_text_after_var)
get_text_before_check = tk.Checkbutton(get_text_snapshot_frame, text="Before", variable=get_text_before_var)
get_text_after_check.pack(side=tk.LEFT, padx=5)
get_text_before_check.pack(side=tk.LEFT, padx=5)
get_text_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
get_text_button = tk.Button(get_text_frame, text="Get Text", command=get_text)
get_text_button.pack(side=tk.TOP)


validation_exists_frame = tk.Frame(sidebar)
title_label = tk.Label(validation_exists_frame, text='Validation - exists')
title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
validation_exists_name_entry = tk.Entry(validation_exists_frame)
validation_exists_name_entry.insert(0, 'Enter validation name(optional)')
validation_exists_name_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
valExists_pass_msg_entry = tk.Entry(validation_exists_frame)
valExists_pass_msg_entry.insert(0, 'Enter pass message(optional)')
valExists_pass_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
valExists_fail_msg_entry = tk.Entry(validation_exists_frame)
valExists_fail_msg_entry.insert(0, 'Enter fail message(optional)')
valExists_fail_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
validation_exists_snapshot_frame = tk.Frame(validation_exists_frame)
validation_exists_snapshot_label = tk.Label(validation_exists_snapshot_frame, text="Snapshot")
validation_exists_snapshot_label.pack(side=tk.LEFT, padx=5)
validation_exists_after_var = tk.IntVar()
validation_exists_before_var = tk.IntVar()
validation_exists_after_check = tk.Checkbutton(validation_exists_snapshot_frame, text="After", variable=validation_exists_after_var)
validation_exists_before_check = tk.Checkbutton(validation_exists_snapshot_frame, text="Before", variable=validation_exists_before_var)
validation_exists_after_check.pack(side=tk.LEFT, padx=5)
validation_exists_before_check.pack(side=tk.LEFT, padx=5)
validation_exists_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
validate_button = tk.Button(validation_exists_frame, text="Validate", command=validate_exists)
validate_button.pack(side=tk.TOP, pady=10)


validation_not_exists_frame = tk.Frame(sidebar)
title_label = tk.Label(validation_not_exists_frame, text='Validation - not exists')
title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
validation_not_exists_name_entry = tk.Entry(validation_not_exists_frame)
validation_not_exists_name_entry.insert(0, 'Enter validation name(optional)')
validation_not_exists_name_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
valNotExists_pass_msg_entry = tk.Entry(validation_not_exists_frame)
valNotExists_pass_msg_entry.insert(0, 'Enter pass message(optional)')
valNotExists_pass_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
valNotExists_fail_msg_entry = tk.Entry(validation_not_exists_frame)
valNotExists_fail_msg_entry.insert(0, 'Enter fail message(optional)')
valNotExists_fail_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
validation_not_exists_snapshot_frame = tk.Frame(validation_not_exists_frame)
validation_not_exists_snapshot_label = tk.Label(validation_not_exists_snapshot_frame, text="Snapshot")
validation_not_exists_snapshot_label.pack(side=tk.LEFT, padx=5)
validation_not_exists_after_var = tk.IntVar()
validation_not_exists_before_var = tk.IntVar()
validation_not_exists_after_check = tk.Checkbutton(validation_not_exists_snapshot_frame, text="After", variable=validation_not_exists_after_var)
validation_not_exists_before_check = tk.Checkbutton(validation_not_exists_snapshot_frame, text="Before", variable=validation_not_exists_before_var)
validation_not_exists_after_check.pack(side=tk.LEFT, padx=5)
validation_not_exists_before_check.pack(side=tk.LEFT, padx=5)
validation_not_exists_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
validate_button = tk.Button(validation_not_exists_frame, text="Validate", command=validate_not_exists)
validate_button.pack(side=tk.TOP, pady=10)


validation_equals_frame = tk.Frame(sidebar)
title_label = tk.Label(validation_equals_frame, text='Validation - equals')
title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
equals_variable1_value_entry = tk.Entry(validation_equals_frame)
equals_variable1_value_entry.insert(0, 'Enter value 1 value')
equals_variable1_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
equals_variable2_value_entry = tk.Entry(validation_equals_frame)
equals_variable2_value_entry.insert(0, 'Enter value 2 value')
equals_variable2_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
equals_validation_name_entry = tk.Entry(validation_equals_frame)
equals_validation_name_entry.insert(0, 'Enter validation name(optional)')
equals_validation_name_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
equals_pass_msg_entry = tk.Entry(validation_equals_frame)
equals_pass_msg_entry.insert(0, 'Enter pass message(optional)')
equals_pass_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
equals_fail_msg_entry = tk.Entry(validation_equals_frame)
equals_fail_msg_entry.insert(0, 'Enter fail message(optional)')
equals_fail_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
validation_equals_snapshot_frame = tk.Frame(validation_equals_frame)
validation_equals_snapshot_label = tk.Label(validation_equals_snapshot_frame, text="Snapshot")
validation_equals_snapshot_label.pack(side=tk.LEFT, padx=5)
validation_equals_after_var = tk.IntVar()
validation_equals_before_var = tk.IntVar()
validation_equals_after_check = tk.Checkbutton(validation_equals_snapshot_frame, text="After", variable=validation_equals_after_var)
validation_equals_before_check = tk.Checkbutton(validation_equals_snapshot_frame, text="Before", variable=validation_equals_before_var)
validation_equals_after_check.pack(side=tk.LEFT, padx=5)
validation_equals_before_check.pack(side=tk.LEFT, padx=5)
validation_equals_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
validate_button = tk.Button(validation_equals_frame, text="Validate", command=validate_equals)
validate_button.pack(side=tk.TOP, pady=14)

validation_not_equals_frame = tk.Frame(sidebar)
title_label = tk.Label(validation_not_equals_frame, text='Validation - not equals')
title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
not_equals_variable1_value_entry = tk.Entry(validation_not_equals_frame)
not_equals_variable1_value_entry.insert(0, 'Enter value 1 value')
not_equals_variable1_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
not_equals_variable2_value_entry = tk.Entry(validation_not_equals_frame)
not_equals_variable2_value_entry.insert(0, 'Enter value 2 value')
not_equals_variable2_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
not_equals_validation_name_entry = tk.Entry(validation_not_equals_frame)
not_equals_validation_name_entry.insert(0, 'Enter validation name(optional)')
not_equals_validation_name_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
not_equals_pass_msg_entry = tk.Entry(validation_not_equals_frame)
not_equals_pass_msg_entry.insert(0, 'Enter pass message(optional)')
not_equals_pass_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
not_equals_fail_msg_entry = tk.Entry(validation_not_equals_frame)
not_equals_fail_msg_entry.insert(0, 'Enter fail message(optional)')
not_equals_fail_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
validation_not_equals_snapshot_frame = tk.Frame(validation_not_equals_frame)
validation_not_equals_snapshot_label = tk.Label(validation_not_equals_snapshot_frame, text="Snapshot")
validation_not_equals_snapshot_label.pack(side=tk.LEFT, padx=5)
validation_not_equals_after_var = tk.IntVar()
validation_not_equals_before_var = tk.IntVar()
validation_not_equals_after_check = tk.Checkbutton(validation_not_equals_snapshot_frame, text="After", variable=validation_not_equals_after_var)
validation_not_equals_before_check = tk.Checkbutton(validation_not_equals_snapshot_frame, text="Before", variable=validation_not_equals_before_var)
validation_not_equals_after_check.pack(side=tk.LEFT, padx=5)
validation_not_equals_before_check.pack(side=tk.LEFT, padx=5)
validation_not_equals_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
validate_button = tk.Button(validation_not_equals_frame, text="Validate", command=validate_not_equals)
validate_button.pack(side=tk.TOP, pady=14)


validation_num_equals_frame = tk.Frame(sidebar)
title_label = tk.Label(validation_num_equals_frame, text='Validation - num equals')
title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
num_equals_variable1_value_entry = tk.Entry(validation_num_equals_frame)
num_equals_variable1_value_entry.insert(0, 'Enter value 1 value')
num_equals_variable1_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
num_equals_variable2_value_entry = tk.Entry(validation_num_equals_frame)
num_equals_variable2_value_entry.insert(0, 'Enter value 2 value')
num_equals_variable2_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
num_equals_validation_name_entry = tk.Entry(validation_num_equals_frame)
num_equals_validation_name_entry.insert(0, 'Enter validation name(optional)')
num_equals_validation_name_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
num_equals_pass_msg_entry = tk.Entry(validation_num_equals_frame)
num_equals_pass_msg_entry.insert(0, 'Enter pass message(optional)')
num_equals_pass_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
num_equals_fail_msg_entry = tk.Entry(validation_num_equals_frame)
num_equals_fail_msg_entry.insert(0, 'Enter fail message(optional)')
num_equals_fail_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
validation_num_equals_snapshot_frame = tk.Frame(validation_num_equals_frame)
validation_num_equals_snapshot_label = tk.Label(validation_num_equals_snapshot_frame, text="Snapshot")
validation_num_equals_snapshot_label.pack(side=tk.LEFT, padx=5)
validation_num_equals_after_var = tk.IntVar()
validation_num_equals_before_var = tk.IntVar()
validation_num_equals_after_check = tk.Checkbutton(validation_num_equals_snapshot_frame, text="After", variable=validation_num_equals_after_var)
validation_num_equals_before_check = tk.Checkbutton(validation_num_equals_snapshot_frame, text="Before", variable=validation_num_equals_before_var)
validation_num_equals_after_check.pack(side=tk.LEFT, padx=5)
validation_num_equals_before_check.pack(side=tk.LEFT, padx=5)
validation_num_equals_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
validate_button = tk.Button(validation_num_equals_frame, text="Validate", command=validate_num_equals)
validate_button.pack(side=tk.TOP, pady=14)


validation_num_not_equals_frame = tk.Frame(sidebar)
title_label = tk.Label(validation_num_not_equals_frame, text='Validation - num not equals')
title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
num_not_equals_variable1_value_entry = tk.Entry(validation_num_not_equals_frame)
num_not_equals_variable1_value_entry.insert(0, 'Enter value 1 value')
num_not_equals_variable1_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
num_not_equals_variable2_value_entry = tk.Entry(validation_num_not_equals_frame)
num_not_equals_variable2_value_entry.insert(0, 'Enter value 2 value')
num_not_equals_variable2_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
num_not_equals_validation_name_entry = tk.Entry(validation_num_not_equals_frame)
num_not_equals_validation_name_entry.insert(0, 'Enter validation name(optional)')
num_not_equals_validation_name_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
num_not_equals_pass_msg_entry = tk.Entry(validation_num_not_equals_frame)
num_not_equals_pass_msg_entry.insert(0, 'Enter pass message(optional)')
num_not_equals_pass_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
num_not_equals_fail_msg_entry = tk.Entry(validation_num_not_equals_frame)
num_not_equals_fail_msg_entry.insert(0, 'Enter fail message(optional)')
num_not_equals_fail_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
validation_num_not_equals_snapshot_frame = tk.Frame(validation_num_not_equals_frame)
validation_num_not_equals_snapshot_label = tk.Label(validation_num_not_equals_snapshot_frame, text="Snapshot")
validation_num_not_equals_snapshot_label.pack(side=tk.LEFT, padx=5)
validation_num_not_equals_after_var = tk.IntVar()
validation_num_not_equals_before_var = tk.IntVar()
validation_num_not_equals_after_check = tk.Checkbutton(validation_num_not_equals_snapshot_frame, text="After", variable=validation_num_not_equals_after_var)
validation_num_not_equals_before_check = tk.Checkbutton(validation_num_not_equals_snapshot_frame, text="Before", variable=validation_num_not_equals_before_var)
validation_num_not_equals_after_check.pack(side=tk.LEFT, padx=5)
validation_num_not_equals_before_check.pack(side=tk.LEFT, padx=5)
validation_num_not_equals_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
validate_button = tk.Button(validation_num_not_equals_frame, text="Validate", command=validate_num_not_equals)
validate_button.pack(side=tk.TOP, pady=14)


variable_value_frame = tk.Frame(sidebar)
variable_value_name_entry = tk.Entry(variable_value_frame)
variable_value_name_entry.insert(0, 'Enter variable name')
variable_value_name_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
variable_value_entry = tk.Entry(variable_value_frame)
variable_value_entry.insert(0, 'Enter variable value')
variable_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
variable_value_snapshot_frame = tk.Frame(variable_value_frame)
variable_value_snapshot_label = tk.Label(variable_value_snapshot_frame, text="Snapshot")
variable_value_snapshot_label.pack(side=tk.LEFT, padx=5)
variable_value_after_var = tk.IntVar()
variable_value_before_var = tk.IntVar()
variable_value_after_check = tk.Checkbutton(variable_value_snapshot_frame, text="After", variable=variable_value_after_var)
variable_value_before_check = tk.Checkbutton(variable_value_snapshot_frame, text="Before", variable=variable_value_before_var)
variable_value_after_check.pack(side=tk.LEFT, padx=5)
variable_value_before_check.pack(side=tk.LEFT, padx=5)
variable_value_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
validate_button = tk.Button(variable_value_frame, text="Stash", command=variable_value)
validate_button.pack(side=tk.TOP, pady=8)


# Left Main Area
main_area = tk.Frame(root)
main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

executed_steps = tk.Listbox(main_area, width=50, height=20)
executed_steps.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Scrollbar for the Listbox
scrollbar = tk.Scrollbar(main_area, orient="vertical", command=executed_steps.yview)
scrollbar.pack(side=tk.LEFT, fill=tk.Y)
executed_steps.config(yscrollcommand=scrollbar.set)
executed_steps.config(xscrollcommand=scrollbar.set)


if __name__ == "__main__":
    root.mainloop()

