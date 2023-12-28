import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

def start_recording():
    start_button.pack_forget()
    stop_button.pack(side=tk.LEFT, padx=5)
    pause_resume_button.config(text="Pause", command=pause_recording)
    pause_resume_button.pack(side=tk.LEFT, padx=5)
    update_steps("Start Recording")
    disable_dropdown_options()

def stop_recording():
    stop_button.pack_forget()
    start_button.pack(side=tk.LEFT, padx=5)
    pause_resume_button.pack_forget()
    dropdown_frame.pack_forget()
    update_steps("Stop Recording")
    disable_dropdown_options()

def pause_recording():
    pause_resume_button.config(text="Resume", command=resume_recording)
    dropdown_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
    update_steps("Pause Recording")
    enable_dropdown_options()

def resume_recording():
    pause_resume_button.config(text="Pause", command=pause_recording)
    dropdown_frame.pack_forget()
    update_steps("Resume Recording")
    disable_dropdown_options()

def enable_dropdown_options():
    dropdown.configure(state='readonly')

def disable_dropdown_options():
    dropdown.configure(state='disabled')
    get_text_frame.pack_forget()
    validation_exists_frame.pack_forget()

def handle_dropdown_selection(event):
    if recording_paused():
        selected = dropdown_var.get()
        if selected == "getText":
            get_text_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            validation_exists_frame.pack_forget()
        elif selected == "validation-exists":
            validation_exists_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            get_text_frame.pack_forget()
            validation_not_exists_frame.pack_forget()
            validation_equals_frame.pack_forget()
            validation_not_equals_frame.pack_forget()
            validation_num_equals_frame.pack_forget()
            validation_num_not_equals_frame.pack_forget()
        elif selected == "validation-not-exists":
            validation_not_exists_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            get_text_frame.pack_forget()
            validation_exists_frame.pack_forget()
            validation_equals_frame.pack_forget()
            validation_not_equals_frame.pack_forget()
            validation_num_equals_frame.pack_forget()
            validation_num_not_equals_frame.pack_forget()
        elif selected == "validation-equals":
            validation_equals_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            get_text_frame.pack_forget()
            validation_exists_frame.pack_forget()
            validation_not_exists_frame.pack_forget()
            validation_not_equals_frame.pack_forget()
            validation_num_equals_frame.pack_forget()
            validation_num_not_equals_frame.pack_forget()
        elif selected == "validation-not-equals":
            validation_not_equals_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            get_text_frame.pack_forget()
            validation_exists_frame.pack_forget()
            validation_not_exists_frame.pack_forget()
            validation_equals_frame.pack_forget()
            validation_num_equals_frame.pack_forget()
            validation_num_not_equals_frame.pack_forget()
        elif selected == "validation-num-equals":
            validation_num_equals_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            get_text_frame.pack_forget()
            validation_exists_frame.pack_forget()
            validation_not_exists_frame.pack_forget()
            validation_equals_frame.pack_forget()
            validation_not_equals_frame.pack_forget()
            validation_num_not_equals_frame.pack_forget()
        elif selected == "validation-num-not-equals":
            validation_num_not_equals_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            get_text_frame.pack_forget()
            validation_exists_frame.pack_forget()
            validation_not_exists_frame.pack_forget()
            validation_equals_frame.pack_forget()
            validation_not_equals_frame.pack_forget()
            validation_num_equals_frame.pack_forget()
        else:
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
    variable_name = variable_name_entry.get()
    # Implement your get_text logic here
    get_text_frame.pack_forget()
    update_steps(f"Get Text: {variable_name}")

def validate_exists():
    validation_name = validation_name_entry.get()
    # Implement your validation logic here
    validation_exists_frame.pack_forget()
    update_steps(f"Validate-exists: {validation_name}")

def validate_not_exists():
    validation_name = validation_name_entry.get()
    # Implement your validation logic here
    validation_not_exists_frame.pack_forget()
    update_steps(f"Validate-not-exists: {validation_name}")

def validate_equals():
    validation_name = validation_name_entry.get()
    # Implement your validation logic here
    validation_equals_frame.pack_forget()
    update_steps(f"validate-equals: {validation_name}")

def validate_not_equals():
    validation_name = validation_name_entry.get()
    # Implement your validation logic here
    validation_not_equals_frame.pack_forget()
    update_steps(f"validate-not-equals: {validation_name}")

def validate_num_equals():
    validation_name = validation_name_entry.get()
    # Implement your validation logic here
    validation_num_equals_frame.pack_forget()
    update_steps(f"validate-num-equals: {validation_name}")

def validate_num_not_equals():
    validation_name = validation_name_entry.get()
    # Implement your validation logic here
    validation_num_not_equals_frame.pack_forget()
    update_steps(f"validate-num-not-equals: {validation_name}")

def update_steps(step):
    executed_steps.insert(tk.END, step)
    executed_steps.see(tk.END)

root = tk.Tk()
root.title("Recording GUI")

# Navigation Bar
nav_bar = tk.Frame(root)
nav_bar.pack(side=tk.TOP, fill=tk.X)

start_button = tk.Button(nav_bar, text="Start", command=start_recording)
stop_button = tk.Button(nav_bar, text="Stop", command=stop_recording)
pause_resume_button = tk.Button(nav_bar, text="Pause", command=pause_recording)

start_button.pack(side=tk.LEFT, padx=5)

# Right Sidebar
sidebar = tk.Frame(root)
sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

dropdown_var = tk.StringVar()
dropdown = ttk.Combobox(sidebar, textvariable=dropdown_var, state="disabled")
dropdown['values'] = ["getText", "validation-exists", "validation-not-exists", "validation-equals", "validation-not-equals", "validation-num-equals", "validation-num-not-equals"]
dropdown.bind("<<ComboboxSelected>>", handle_dropdown_selection)

dropdown_frame = tk.Frame(sidebar)
dropdown.pack(fill=tk.X)

get_text_frame = tk.Frame(sidebar)
variable_name_entry = tk.Entry(get_text_frame)
variable_name_entry.insert(0, 'variable name')
get_text_button = tk.Button(get_text_frame, text="Get Text", command=get_text)
variable_name_entry.pack(side=tk.LEFT, padx=5)
get_text_button.pack(side=tk.LEFT)

validation_exists_frame = tk.Frame(sidebar)
validation_name_entry = tk.Entry(validation_exists_frame)
validation_name_entry.insert(0, 'validation name')
validate_button = tk.Button(validation_exists_frame, text="Validate", command=validate_exists)
validation_name_entry.pack(side=tk.LEFT, padx=5)
validate_button.pack(side=tk.LEFT)

validation_not_exists_frame = tk.Frame(sidebar)
validation_name_entry = tk.Entry(validation_not_exists_frame)
validation_name_entry.insert(0, 'validation name')
validate_button = tk.Button(validation_not_exists_frame, text="Validate", command=validate_not_exists)
validation_name_entry.pack(side=tk.LEFT, padx=5)
validate_button.pack(side=tk.LEFT)

validation_equals_frame = tk.Frame(sidebar)
validation_name_entry = tk.Entry(validation_equals_frame)
validation_name_entry.insert(0, 'validation name')
validate_button = tk.Button(validation_equals_frame, text="Validate", command=validate_equals)
validation_name_entry.pack(side=tk.LEFT, padx=5)
validate_button.pack(side=tk.LEFT)

validation_not_equals_frame = tk.Frame(sidebar)
validation_name_entry = tk.Entry(validation_not_equals_frame)
validation_name_entry.insert(0, 'validation name')
validate_button = tk.Button(validation_not_equals_frame, text="Validate", command=validate_not_equals)
validation_name_entry.pack(side=tk.LEFT, padx=5)
validate_button.pack(side=tk.LEFT)

validation_num_equals_frame = tk.Frame(sidebar)
validation_name_entry = tk.Entry(validation_num_equals_frame)
validation_name_entry.insert(0, 'validation name')
validate_button = tk.Button(validation_num_equals_frame, text="Validate", command=validate_num_equals)
validation_name_entry.pack(side=tk.LEFT, padx=5)
validate_button.pack(side=tk.LEFT)

validation_num_not_equals_frame = tk.Frame(sidebar)
validation_name_entry = tk.Entry(validation_num_not_equals_frame)
validation_name_entry.insert(0, 'validation name')
validate_button = tk.Button(validation_num_not_equals_frame, text="Validate", command=validate_num_not_equals)
validation_name_entry.pack(side=tk.LEFT, padx=5)
validate_button.pack(side=tk.LEFT)

# Left Main Area
main_area = tk.Frame(root)
main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

executed_steps = tk.Listbox(main_area, width=50, height=20)
executed_steps.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Scrollbar for the Listbox
scrollbar = tk.Scrollbar(main_area, orient="vertical", command=executed_steps.yview)
scrollbar.pack(side=tk.LEFT, fill=tk.Y)
executed_steps.config(yscrollcommand=scrollbar.set)

root.mainloop()
