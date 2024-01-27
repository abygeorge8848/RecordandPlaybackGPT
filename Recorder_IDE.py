import tkinter as tk
from tkinter import ttk, messagebox
from Recorder import start_recording, stop_and_show_records, create_xpath, create_xpath2, pause_recording_main, resume_recording_main
from RunPAF import run_file, report_open
from serverConn import conn, delete_last_event
import time
from effects import FadingMessage




class Recorder:

    def __init__(self):

        self.root = tk.Tk()
        self.root.title("Recorder")

        # Navigation Bar
        self.nav_bar = tk.Frame(self.root)
        self.nav_bar.pack(side=tk.TOP, fill=tk.X)

        url_entry = tk.Entry(self.nav_bar)
        url_entry.insert(0, 'http://')  # You can set a default or placeholder text if needed
        url_entry.pack(side=tk.LEFT, padx=5)

        self.start_button = tk.Button(self.nav_bar, text="Start", command=self.start_record)
        self.run_button = tk.Button(self.nav_bar, text="Run Script", command=self.run_script)
        self.open_report_button = tk.Button(self.nav_bar, text="Open Report", command=report_open)
        self.stop_button = tk.Button(self.nav_bar, text="Stop", command=self.stop_recording)
        self.delete_button = tk.Button(self.nav_bar, text="Delete", command=self.delete_step)
        self.insert_custom_button = tk.Button(self.nav_bar, text="Insert", command=self.insert_custom_step)
        self.get_xpath_button = tk.Button(self.nav_bar, text="Get xpath", command=self.capture_xpath_main)
        self.pause_resume_button = tk.Button(self.nav_bar, text="Pause", command=self.pause_recording)
        self.end_if_button = tk.Button(self.nav_bar, text="End if segment", command=self.end_if)
        self.end_if_then_button = tk.Button(self.nav_bar, text="End if then segment", command=self.end_if_then)
        self.end_else_button = tk.Button(self.nav_bar, text="End else segment", command=self.end_else)
        self.end_loop_button = tk.Button(self.nav_bar, text="End loop", command=self.end_loop_placeholder)

        self.start_button.pack(side=tk.LEFT, padx=5)

        # Right Sidebar
        self.sidebar = tk.Frame(self.root)
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        self.dropdown_var = tk.StringVar()
        self.dropdown = ttk.Combobox(self.sidebar, textvariable=self.dropdown_var, state="readonly")
        self.dropdown['values'] = ["getText", "variable-value", "validation", "if-condition", "if-else-condition", "loop"]
        self.dropdown.bind("<<ComboboxSelected>>", self.handle_dropdown_selection)
        self.dropdown.pack(fill=tk.X)

        # Create the validation submenu
        validation_menu = self.create_validation_menu()

        # Bind hover event to the main dropdown
        self.dropdown.bind("<Motion>", self.show_validation_menu)

        self.dropdown_frame = tk.Frame(self.sidebar)
        self.dropdown.pack(fill=tk.X)     


        self.insert_custom_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.insert_custom_frame, text='Insert a custom step')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.custom_step_entry = tk.Entry(self.insert_custom_frame)
        self.custom_step_entry.insert(0, 'Enter the custom step')
        self.custom_step_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.custom_step_button = tk.Button(self.insert_custom_frame, text="Insert", command=self.insert_step)
        self.custom_step_button.pack(side=tk.TOP)

        self.display_xpath_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.display_xpath_frame, text='Generated xpath :')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.xpath_label = tk.Label(self.display_xpath_frame, bg='white', text='', relief='sunken', anchor='w')
        self.xpath_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.copy_button_text = "\U0001F4CB"
        self.copy_button = tk.Button(self.display_xpath_frame, text=self.copy_button_text)
        self.copy_button.pack(side=tk.LEFT, padx=5)
        self.copy_button.bind("<Button-1>", self.copy_to_clipboard)



        self.get_text_frame = tk.Frame(self.sidebar)
        self.variable_frame = tk.Frame(self.get_text_frame)
        self.variable_name_label = tk.Label(self.variable_frame, text="Variable Name:")
        self.variable_name_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.getText_variable_name_entry = tk.Entry(self.variable_frame)
        self.getText_variable_name_entry.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5)
        self.variable_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.get_text_snapshot_frame = tk.Frame(self.get_text_frame)
        self.get_text_snapshot_label = tk.Label(self.get_text_snapshot_frame, text="Snapshot")
        self.get_text_snapshot_label.pack(side=tk.LEFT, padx=5)
        self.get_text_after_var = tk.IntVar()
        self.get_text_before_var = tk.IntVar()
        self.get_text_after_check = tk.Checkbutton(self.get_text_snapshot_frame, text="After", variable=self.get_text_after_var)
        self.get_text_before_check = tk.Checkbutton(self.get_text_snapshot_frame, text="Before", variable=self.get_text_before_var)
        self.get_text_after_check.pack(side=tk.LEFT, padx=5)
        self.get_text_before_check.pack(side=tk.LEFT, padx=5)
        self.get_text_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.get_text_button = tk.Button(self.get_text_frame, text="Get Text", command=self.get_text)
        self.get_text_button.pack(side=tk.TOP)


        self.validation_exists_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.validation_exists_frame, text='Exists')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.validation_exists_name_entry = tk.Entry(self.validation_exists_frame)
        self.validation_exists_name_entry.insert(0, 'Enter validation name(optional)')
        self.validation_exists_name_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.valExists_pass_msg_entry = tk.Entry(self.validation_exists_frame)
        self.valExists_pass_msg_entry.insert(0, 'Enter pass message(optional)')
        self.valExists_pass_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.valExists_fail_msg_entry = tk.Entry(self.validation_exists_frame)
        self.valExists_fail_msg_entry.insert(0, 'Enter fail message(optional)')
        self.valExists_fail_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.validation_exists_snapshot_frame = tk.Frame(self.validation_exists_frame)
        self.validation_exists_snapshot_label = tk.Label(self.validation_exists_snapshot_frame, text="Snapshot")
        self.validation_exists_snapshot_label.pack(side=tk.LEFT, padx=5)
        self.validation_exists_after_var = tk.IntVar()
        self.validation_exists_before_var = tk.IntVar()
        self.validation_exists_after_check = tk.Checkbutton(self.validation_exists_snapshot_frame, text="After", variable=self.validation_exists_after_var)
        self.validation_exists_before_check = tk.Checkbutton(self.validation_exists_snapshot_frame, text="Before", variable=self.validation_exists_before_var)
        self.validation_exists_after_check.pack(side=tk.LEFT, padx=5)
        self.validation_exists_before_check.pack(side=tk.LEFT, padx=5)
        self.validation_exists_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.validate_button = tk.Button(self.validation_exists_frame, text="Validate", command=self.validate_exists)
        self.validate_button.pack(side=tk.TOP, pady=10)


        self.validation_not_exists_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.validation_not_exists_frame, text='Not exists')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.validation_not_exists_name_entry = tk.Entry(self.validation_not_exists_frame)
        self.validation_not_exists_name_entry.insert(0, 'Enter validation name(optional)')
        self.validation_not_exists_name_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.valNotExists_pass_msg_entry = tk.Entry(self.validation_not_exists_frame)
        self.valNotExists_pass_msg_entry.insert(0, 'Enter pass message(optional)')
        self.valNotExists_pass_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.valNotExists_fail_msg_entry = tk.Entry(self.validation_not_exists_frame)
        self.valNotExists_fail_msg_entry.insert(0, 'Enter fail message(optional)')
        self.valNotExists_fail_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.validation_not_exists_snapshot_frame = tk.Frame(self.validation_not_exists_frame)
        self.validation_not_exists_snapshot_label = tk.Label(self.validation_not_exists_snapshot_frame, text="Snapshot")
        self.validation_not_exists_snapshot_label.pack(side=tk.LEFT, padx=5)
        self.validation_not_exists_after_var = tk.IntVar()
        self.validation_not_exists_before_var = tk.IntVar()
        self.validation_not_exists_after_check = tk.Checkbutton(self.validation_not_exists_snapshot_frame, text="After", variable=self.validation_not_exists_after_var)
        self.validation_not_exists_before_check = tk.Checkbutton(self.validation_not_exists_snapshot_frame, text="Before", variable=self.validation_not_exists_before_var)
        self.validation_not_exists_after_check.pack(side=tk.LEFT, padx=5)
        self.validation_not_exists_before_check.pack(side=tk.LEFT, padx=5)
        self.validation_not_exists_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.validate_button = tk.Button(self.validation_not_exists_frame, text="Validate", command=self.validate_not_exists)
        self.validate_button.pack(side=tk.TOP, pady=10)


        self.validation_equals_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.validation_equals_frame, text='Equals')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.equals_variable1_value_entry = tk.Entry(self.validation_equals_frame)
        self.equals_variable1_value_entry.insert(0, 'Enter variable name')
        self.equals_variable1_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.equals_variable2_value_entry = tk.Entry(self.validation_equals_frame)
        self.equals_variable2_value_entry.insert(0, 'Enter value')
        self.equals_variable2_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.equals_validation_name_entry = tk.Entry(self.validation_equals_frame)
        self.equals_validation_name_entry.insert(0, 'Enter validation name(optional)')
        self.equals_validation_name_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.equals_pass_msg_entry = tk.Entry(self.validation_equals_frame)
        self.equals_pass_msg_entry.insert(0, 'Enter pass message(optional)')
        self.equals_pass_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.equals_fail_msg_entry = tk.Entry(self.validation_equals_frame)
        self.equals_fail_msg_entry.insert(0, 'Enter fail message(optional)')
        self.equals_fail_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.validation_equals_snapshot_frame = tk.Frame(self.validation_equals_frame)
        self.validation_equals_snapshot_label = tk.Label(self.validation_equals_snapshot_frame, text="Snapshot")
        self.validation_equals_snapshot_label.pack(side=tk.LEFT, padx=5)
        self.validation_equals_after_var = tk.IntVar()
        self.validation_equals_before_var = tk.IntVar()
        self.validation_equals_after_check = tk.Checkbutton(self.validation_equals_snapshot_frame, text="After", variable=self.validation_equals_after_var)
        self.validation_equals_before_check = tk.Checkbutton(self.validation_equals_snapshot_frame, text="Before", variable=self.validation_equals_before_var)
        self.validation_equals_after_check.pack(side=tk.LEFT, padx=5)
        self.validation_equals_before_check.pack(side=tk.LEFT, padx=5)
        self.validation_equals_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.validate_button = tk.Button(self.validation_equals_frame, text="Validate", command=self.validate_equals)
        self.validate_button.pack(side=tk.TOP, pady=14)

        self.validation_not_equals_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.validation_not_equals_frame, text='Not equals')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.not_equals_variable1_value_entry = tk.Entry(self.validation_not_equals_frame)
        self.not_equals_variable1_value_entry.insert(0, 'Enter variable name')
        self.not_equals_variable1_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.not_equals_variable2_value_entry = tk.Entry(self.validation_not_equals_frame)
        self.not_equals_variable2_value_entry.insert(0, 'Enter value')
        self.not_equals_variable2_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.not_equals_validation_name_entry = tk.Entry(self.validation_not_equals_frame)
        self.not_equals_validation_name_entry.insert(0, 'Enter validation name(optional)')
        self.not_equals_validation_name_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.not_equals_pass_msg_entry = tk.Entry(self.validation_not_equals_frame)
        self.not_equals_pass_msg_entry.insert(0, 'Enter pass message(optional)')
        self.not_equals_pass_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.not_equals_fail_msg_entry = tk.Entry(self.validation_not_equals_frame)
        self.not_equals_fail_msg_entry.insert(0, 'Enter fail message(optional)')
        self.not_equals_fail_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.validation_not_equals_snapshot_frame = tk.Frame(self.validation_not_equals_frame)
        self.validation_not_equals_snapshot_label = tk.Label(self.validation_not_equals_snapshot_frame, text="Snapshot")
        self.validation_not_equals_snapshot_label.pack(side=tk.LEFT, padx=5)
        self.validation_not_equals_after_var = tk.IntVar()
        self.validation_not_equals_before_var = tk.IntVar()
        self.validation_not_equals_after_check = tk.Checkbutton(self.validation_not_equals_snapshot_frame, text="After", variable=self.validation_not_equals_after_var)
        self.validation_not_equals_before_check = tk.Checkbutton(self.validation_not_equals_snapshot_frame, text="Before", variable=self.validation_not_equals_before_var)
        self.validation_not_equals_after_check.pack(side=tk.LEFT, padx=5)
        self.validation_not_equals_before_check.pack(side=tk.LEFT, padx=5)
        self.validation_not_equals_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.validate_button = tk.Button(self.validation_not_equals_frame, text="Validate", command=self.validate_not_equals)
        self.validate_button.pack(side=tk.TOP, pady=14)


        self.validation_num_equals_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.validation_num_equals_frame, text='Num equals')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_equals_variable1_value_entry = tk.Entry(self.validation_num_equals_frame)
        self.num_equals_variable1_value_entry.insert(0, 'Enter variable name')
        self.num_equals_variable1_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_equals_variable2_value_entry = tk.Entry(self.validation_num_equals_frame)
        self.num_equals_variable2_value_entry.insert(0, 'Enter value')
        self.num_equals_variable2_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_equals_validation_name_entry = tk.Entry(self.validation_num_equals_frame)
        self.num_equals_validation_name_entry.insert(0, 'Enter validation name(optional)')
        self.num_equals_validation_name_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_equals_pass_msg_entry = tk.Entry(self.validation_num_equals_frame)
        self.num_equals_pass_msg_entry.insert(0, 'Enter pass message(optional)')
        self.num_equals_pass_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_equals_fail_msg_entry = tk.Entry(self.validation_num_equals_frame)
        self.num_equals_fail_msg_entry.insert(0, 'Enter fail message(optional)')
        self.num_equals_fail_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.validation_num_equals_snapshot_frame = tk.Frame(self.validation_num_equals_frame)
        self.validation_num_equals_snapshot_label = tk.Label(self.validation_num_equals_snapshot_frame, text="Snapshot")
        self.validation_num_equals_snapshot_label.pack(side=tk.LEFT, padx=5)
        self.validation_num_equals_after_var = tk.IntVar()
        self.validation_num_equals_before_var = tk.IntVar()
        self.validation_num_equals_after_check = tk.Checkbutton(self.validation_num_equals_snapshot_frame, text="After", variable=self.validation_num_equals_after_var)
        self.validation_num_equals_before_check = tk.Checkbutton(self.validation_num_equals_snapshot_frame, text="Before", variable=self.validation_num_equals_before_var)
        self.validation_num_equals_after_check.pack(side=tk.LEFT, padx=5)
        self.validation_num_equals_before_check.pack(side=tk.LEFT, padx=5)
        self.validation_num_equals_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.validate_button = tk.Button(self.validation_num_equals_frame, text="Validate", command=self.validate_num_equals)
        self.validate_button.pack(side=tk.TOP, pady=14)


        self.validation_num_not_equals_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.validation_num_not_equals_frame, text='Num not equals')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_not_equals_variable1_value_entry = tk.Entry(self.validation_num_not_equals_frame)
        self.num_not_equals_variable1_value_entry.insert(0, 'Enter variable name')
        self.num_not_equals_variable1_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_not_equals_variable2_value_entry = tk.Entry(self.validation_num_not_equals_frame)
        self.num_not_equals_variable2_value_entry.insert(0, 'Enter value')
        self.num_not_equals_variable2_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_not_equals_validation_name_entry = tk.Entry(self.validation_num_not_equals_frame)
        self.num_not_equals_validation_name_entry.insert(0, 'Enter validation name(optional)')
        self.num_not_equals_validation_name_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_not_equals_pass_msg_entry = tk.Entry(self.validation_num_not_equals_frame)
        self.num_not_equals_pass_msg_entry.insert(0, 'Enter pass message(optional)')
        self.num_not_equals_pass_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_not_equals_fail_msg_entry = tk.Entry(self.validation_num_not_equals_frame)
        self.num_not_equals_fail_msg_entry.insert(0, 'Enter fail message(optional)')
        self.num_not_equals_fail_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.validation_num_not_equals_snapshot_frame = tk.Frame(self.validation_num_not_equals_frame)
        self.validation_num_not_equals_snapshot_label = tk.Label(self.validation_num_not_equals_snapshot_frame, text="Snapshot")
        self.validation_num_not_equals_snapshot_label.pack(side=tk.LEFT, padx=5)
        self.validation_num_not_equals_after_var = tk.IntVar()
        self.validation_num_not_equals_before_var = tk.IntVar()
        self.validation_num_not_equals_after_check = tk.Checkbutton(self.validation_num_not_equals_snapshot_frame, text="After", variable=self.validation_num_not_equals_after_var)
        self.validation_num_not_equals_before_check = tk.Checkbutton(self.validation_num_not_equals_snapshot_frame, text="Before", variable=self.validation_num_not_equals_before_var)
        self.validation_num_not_equals_after_check.pack(side=tk.LEFT, padx=5)
        self.validation_num_not_equals_before_check.pack(side=tk.LEFT, padx=5)
        self.validation_num_not_equals_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.validate_button = tk.Button(self.validation_num_not_equals_frame, text="Validate", command=self.validate_num_not_equals)
        self.validate_button.pack(side=tk.TOP, pady=14)


        self.variable_value_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.variable_value_frame, text='Variable value')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.variable_value_name_entry = tk.Entry(self.variable_value_frame)
        self.variable_value_name_entry.insert(0, 'Enter variable name')
        self.variable_value_name_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.variable_value_entry = tk.Entry(self.variable_value_frame)
        self.variable_value_entry.insert(0, 'Enter variable value')
        self.variable_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.variable_value_snapshot_frame = tk.Frame(self.variable_value_frame)
        self.variable_value_snapshot_label = tk.Label(self.variable_value_snapshot_frame, text="Snapshot")
        self.variable_value_snapshot_label.pack(side=tk.LEFT, padx=5)
        self.variable_value_after_var = tk.IntVar()
        self.variable_value_before_var = tk.IntVar()
        self.variable_value_after_check = tk.Checkbutton(self.variable_value_snapshot_frame, text="After", variable=self.variable_value_after_var)
        self.variable_value_before_check = tk.Checkbutton(self.variable_value_snapshot_frame, text="Before", variable=self.variable_value_before_var)
        self.variable_value_after_check.pack(side=tk.LEFT, padx=5)
        self.variable_value_before_check.pack(side=tk.LEFT, padx=5)
        self.variable_value_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.validate_button = tk.Button(self.variable_value_frame, text="Stash", command=self.variable_value)
        self.validate_button.pack(side=tk.TOP, pady=8)


        self.loop_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.loop_frame, text='Loop')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.start_index_entry = tk.Entry(self.loop_frame)
        self.start_index_entry.insert(0, 'Enter start index(optional - default to 1)')
        self.start_index_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.last_index_entry = tk.Entry(self.loop_frame)
        self.last_index_entry.insert(0, 'Enter last index')
        self.last_index_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.increment_entry = tk.Entry(self.loop_frame)
        self.increment_entry.insert(0, 'Enter increment(optional - deafult to 1)')
        self.increment_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.counterVar_entry = tk.Entry(self.loop_frame)
        self.counterVar_entry.insert(0, 'Assign counter(optional - default to i)')
        self.counterVar_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.start_loop_button = tk.Button(self.loop_frame, text="Start loop", command=self.start_loop)
        self.start_loop_button.pack(side=tk.TOP, pady=8)


        # Left Main Area
        self.main_area = tk.Frame(self.root)
        self.main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.executed_steps = tk.Listbox(self.main_area, width=50, height=20)
        self.executed_steps.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar for the Listbox
        self.scrollbar = tk.Scrollbar(self.main_area, orient="vertical", command=self.executed_steps.yview)
        self.scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.executed_steps.config(yscrollcommand=self.scrollbar.set)
        self.executed_steps.config(xscrollcommand=self.scrollbar.set)



    def start_record(self):
        self.start_button.pack_forget()
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.pause_resume_button.config(text="Pause", command=self.pause_recording)
        self.pause_resume_button.pack(side=tk.LEFT, padx=5)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        self.update_steps("Start Recording")
        self.disable_dropdown_options()
        url = self.url_entry.get()
        start_recording(url)

    def stop_recording(self):
        self.stop_button.pack_forget()
        self.pause_resume_button.pack_forget()
        self.dropdown_frame.pack_forget()
        self.delete_button.pack_forget()
        self.update_steps("Stop Recording")
        self.disable_dropdown_options()
        response = stop_and_show_records()
        if response:
            self.start_button.pack_forget()
            self.run_button.pack(side=tk.LEFT, padx=5)


    def pause_recording(self):
        pause_recording_main()
        self.pause_resume_button.config(text="Resume", command=self.resume_recording)
        self.dropdown_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
        self.insert_custom_button.pack(side=tk.RIGHT, padx=5)
        self.get_xpath_button.pack(side=tk.RIGHT, padx=5)
        self.update_steps("Pause Recording")
        self.enable_dropdown_options()

    def resume_recording(self):
        resume_recording_main()
        self.pause_resume_button.config(text="Pause", command=self.pause_recording)
        self.dropdown_frame.pack_forget()
        self.variable_value_frame.pack_forget()
        self.get_text_frame.pack_forget()
        self.validation_exists_frame.pack_forget()
        self.validation_not_exists_frame.pack_forget()
        self.validation_equals_frame.pack_forget()
        self.validation_not_equals_frame.pack_forget()
        self.validation_num_equals_frame.pack_forget()
        self.validation_num_not_equals_frame.pack_forget()
        self.loop_frame.pack_forget()
        self.insert_custom_button.pack_forget()
        self.insert_custom_frame.pack_forget()
        self.get_xpath_button.pack_forget()
        self.display_xpath_frame.pack_forget()
        self.update_steps("Resume Recording")
        self.disable_dropdown_options()

    def run_script(self):
        print("\n I'll try to run your PAF script now! \n\n")
        file_run = run_file()
        print(f"The file run result is : {file_run}")
        if file_run:
            self.run_button.pack_forget()
            self.open_report_button.pack(side=tk.LEFT, padx=5)


    def delete_step(self):
        # Show a confirmation dialog
        user_response = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete the previous step?")
        # Check the user's response
        if user_response:  # If the user clicked 'Yes'
            deleted_event = delete_last_event()
            if deleted_event[0] == "end-if" or deleted_event[0] == "end-if-then" or deleted_event[0] == "end-else" or deleted_event[0] == "end-loop" or deleted_event[0] == "loop" or deleted_event[0] == "getText" or deleted_event[0] == "validation-exists" or deleted_event[0] == "validation-not-exists" or deleted_event[0] == "validation-equals" or deleted_event[0] == "validation-not-equals" or deleted_event[0] == "validation-num-equals" or deleted_event[0] == "validation-num-not-equals" or deleted_event[0] == "if-condition" or deleted_event[0] == "if-else-condition" or deleted_event[0] == "variable-value" or deleted_event[0] == "custom-step":
                self.delete_last_step_from_executed_steps()
        else:
            return


    def insert_custom_step(self):
        self.insert_custom_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
        self.validation_exists_frame.pack_forget()
        self.validation_not_exists_frame.pack_forget()
        self.validation_equals_frame.pack_forget()
        self.validation_not_equals_frame.pack_forget()
        self.validation_num_equals_frame.pack_forget()
        self.validation_num_not_equals_frame.pack_forget()
        self.variable_value_frame.pack_forget()
        self.loop_frame.pack_forget()
        self.display_xpath_frame.pack_forget()

    def capture_xpath_main(self):
        xpath = create_xpath2()
        if not xpath:
            messagebox.showwarning("Warning", "You have not clicked on your target element you want the xpath of!")
            return
        self.xpath_label.config(text=xpath)
        self.display_xpath_frame.pack(side=tk.TOP, pady=5, fill=tk.X)


    def end_if(self):
        now = int(time.time() * 1000)
        conn([["end-if", now]])
        self.update_steps(f"End if condition segment")
        self.end_if_button.pack_forget()

    def end_if_then(self):
        now = int(time.time() * 1000)
        conn([["end-if-then", now]])
        self.update_steps(f"End if then condition segment")
        self.end_if_then_button.pack_forget()
        self.end_else_button.pack(side=tk.LEFT, padx=5)

    def end_else(self):
        now = int(time.time() * 1000)
        conn([["end-else", now]])
        self.update_steps(f"End else condition segment")
        self.end_else_button.pack_forget()

    def end_loop_create(self, counterVar):
        global counterVariable
        counterVariable = counterVar
        self.end_loop_button.config(text=f"End loop - {counterVar}", command=self.end_loop)
        self.end_loop_button.pack(side=tk.LEFT, padx=5)


    def end_loop(self):
        now = int(time.time() * 1000)
        conn([["end-loop", now]])
        self.update_steps(f"End loop - {counterVariable}")
        self.end_loop_button.pack_forget()

    def end_loop_placeholder():
        pass


    def enable_dropdown_options(self):
        self.dropdown.configure(state='readonly')

    def disable_dropdown_options(self):
        self.dropdown.configure(state='disabled')
        self.get_text_frame.pack_forget()
        self.validation_exists_frame.pack_forget()
        self.insert_custom_frame.pack_forget()
        self.display_xpath_frame.pack_forget()

    def show_validation_menu(self, event):
        # Display the menu if the selected option is "validation"
        if self.recording_paused():
            if self.dropdown_var.get() == "validation" or self.dropdown_var.get() == "if-condition" or self.dropdown_var.get() == "if-else-condition":
                x = self.dropdown.winfo_rootx()
                y = self.dropdown.winfo_rooty() + self.dropdown.winfo_height()
                self.validation_menu.tk_popup(x, y, 0)

    def create_validation_menu(self):
        # Create the validation submenu
        menu = tk.Menu(self.root, tearoff=0)
        for option in ["exists", "not-exists", "equals", "not-equals", "num-equals", "num-not-equals"]:
            menu.add_command(label=option, command=lambda val=option: self.handle_validation_option(val))
        return menu

    def on_validation_menu_selection(self, value):
        # Handle the selection from the validation menu
        print(value)
        self.validation_menu.unpost()


    def handle_validation_option(self, selected_validation):
        if self.recording_paused():
            if selected_validation == "exists":
                self.validation_exists_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
                self.get_text_frame.pack_forget()
                self.validation_not_exists_frame.pack_forget()
                self.validation_equals_frame.pack_forget()
                self.validation_not_equals_frame.pack_forget()
                self.validation_num_equals_frame.pack_forget()
                self.validation_num_not_equals_frame.pack_forget()
                self.variable_value_frame.pack_forget()
                self.loop_frame.pack_forget()
                self.insert_custom_frame.pack_forget()
                self.display_xpath_frame.pack_forget()
            elif selected_validation == "not-exists":
                self.validation_not_exists_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
                self.get_text_frame.pack_forget()
                self.validation_exists_frame.pack_forget()
                self.validation_equals_frame.pack_forget()
                self.validation_not_equals_frame.pack_forget()
                self.validation_num_equals_frame.pack_forget()
                self.validation_num_not_equals_frame.pack_forget()
                self.variable_value_frame.pack_forget()
                self.loop_frame.pack_forget()
                self.insert_custom_frame.pack_forget()
                self.display_xpath_frame.pack_forget()
            elif selected_validation == "equals":
                self.validation_equals_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
                self.get_text_frame.pack_forget()
                self.validation_exists_frame.pack_forget()
                self.validation_not_exists_frame.pack_forget()
                self.validation_not_equals_frame.pack_forget()
                self.validation_num_equals_frame.pack_forget()
                self.validation_num_not_equals_frame.pack_forget()
                self.variable_value_frame.pack_forget()
                self.loop_frame.pack_forget()
                self.insert_custom_frame.pack_forget()
                self.display_xpath_frame.pack_forget()
            elif selected_validation == "not-equals":
                self.validation_not_equals_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
                self.get_text_frame.pack_forget()
                self.validation_exists_frame.pack_forget()
                self.validation_not_exists_frame.pack_forget()
                self.validation_equals_frame.pack_forget()
                self.validation_num_equals_frame.pack_forget()
                self.validation_num_not_equals_frame.pack_forget()
                self.variable_value_frame.pack_forget()
                self.loop_frame.pack_forget()
                self.insert_custom_frame.pack_forget()
                self.display_xpath_frame.pack_forget()
            elif selected_validation == "num-equals":
                self.validation_num_equals_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
                self.get_text_frame.pack_forget()
                self.validation_exists_frame.pack_forget()
                self.validation_not_exists_frame.pack_forget()
                self.validation_equals_frame.pack_forget()
                self.validation_not_equals_frame.pack_forget()
                self.validation_num_not_equals_frame.pack_forget()
                self.variable_value_frame.pack_forget()
                self.loop_frame.pack_forget()
                self.insert_custom_frame.pack_forget()
                self.display_xpath_frame.pack_forget()
            elif selected_validation == "num-not-equals":
                self.validation_num_not_equals_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
                self.get_text_frame.pack_forget()
                self.validation_exists_frame.pack_forget()
                self.validation_not_exists_frame.pack_forget()
                self.validation_equals_frame.pack_forget()
                self.validation_not_equals_frame.pack_forget()
                self.validation_num_equals_frame.pack_forget()
                self.variable_value_frame.pack_forget()
                self.loop_frame.pack_forget()
                self.insert_custom_frame.pack_forget()
                self.display_xpath_frame.pack_forget()
            else:
                self.variable_value_frame.pack_forget()
                self.get_text_frame.pack_forget()
                self.validation_exists_frame.pack_forget()
                self.validation_not_exists_frame.pack_forget()
                self.validation_equals_frame.pack_forget()
                self.validation_not_equals_frame.pack_forget()
                self.validation_num_equals_frame.pack_forget()
                self.validation_num_not_equals_frame.pack_forget()
                self.loop_frame.pack_forget()
                self.insert_custom_frame.pack_forget()
                self.display_xpath_frame.pack_forget()


    def handle_dropdown_selection(self, event):
        if self.recording_paused():
            selected = self.dropdown_var.get()
            if selected == "getText":
                self.get_text_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
                self.validation_exists_frame.pack_forget()
                self.validation_not_exists_frame.pack_forget()
                self.validation_equals_frame.pack_forget()
                self.validation_not_equals_frame.pack_forget()
                self.validation_num_equals_frame.pack_forget()
                self.validation_num_not_equals_frame.pack_forget()
                self.variable_value_frame.pack_forget()
                self.loop_frame.pack_forget()
                self.insert_custom_frame.pack_forget()
                self.display_xpath_frame.pack_forget()
            elif selected == "variable-value":
                self.variable_value_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
                self.validation_num_not_equals_frame.pack_forget()
                self.get_text_frame.pack_forget()
                self.validation_exists_frame.pack_forget()
                self.validation_not_exists_frame.pack_forget()
                self.validation_equals_frame.pack_forget()
                self.validation_not_equals_frame.pack_forget()
                self.validation_num_equals_frame.pack_forget()
                self.loop_frame.pack_forget()
                self.insert_custom_frame.pack_forget()
                self.display_xpath_frame.pack_forget()
            elif selected == "loop":
                self.loop_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
                self.variable_value_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
                self.validation_num_not_equals_frame.pack_forget()
                self.get_text_frame.pack_forget()
                self.validation_exists_frame.pack_forget()
                self.validation_not_exists_frame.pack_forget()
                self.validation_equals_frame.pack_forget()
                self.validation_not_equals_frame.pack_forget()
                self.validation_num_equals_frame.pack_forget()
                self.variable_value_frame.pack_forget()
                self.insert_custom_frame.pack_forget()
                self.display_xpath_frame.pack_forget()
            else:
                self.variable_value_frame.pack_forget()
                self.get_text_frame.pack_forget()
                self.validation_exists_frame.pack_forget()
                self.validation_not_exists_frame.pack_forget()
                self.validation_equals_frame.pack_forget()
                self.validation_not_equals_frame.pack_forget()
                self.validation_num_equals_frame.pack_forget()
                self.validation_num_not_equals_frame.pack_forget()
                self.insert_custom_frame.pack_forget()
                self.display_xpath_frame.pack_forget()
        else:
            messagebox.showinfo("Alert", "Please pause the recording before entering custom steps.")

    def recording_paused(self):
        return self.pause_resume_button.cget('text') == "Resume"

    def get_text(self):
        get_text_after_checked = self.get_text_after_var.get()
        get_text_before_checked = self.get_text_before_var.get()
        variable_name = self.getText_variable_name_entry.get()
        xpath = create_xpath()
        now = int(time.time() * 1000)
        conn([["getText", now, xpath, variable_name, get_text_after_checked, get_text_before_checked]])
        self.get_text_frame.pack_forget()
        self.update_steps(f"Get Text: {variable_name}")

    def validate_exists(self):
        if_condition = False
        if_else_condition = False
        if self.dropdown_var.get() == "if-condition":
            if_condition = True
            self.end_if_button.pack(side=tk.LEFT, padx=5)
        elif self.dropdown_var.get() == "if-else-condition":
            if_condition = True
            if_else_condition = True
            self.end_if_then_button.pack(side=tk.LEFT, padx=5)
        validate_exists_after_checked = self.validation_exists_after_var.get()
        validate_exists_before_checked = self.validation_exists_before_var.get()
        validation_name = self.validation_exists_name_entry.get()
        validation_pass_msg = self.valExists_pass_msg_entry.get()
        validation_fail_msg = self.valExists_fail_msg_entry.get()
        xpath = create_xpath()
        now = int(time.time() * 1000)
        conn([["validation-exists", now, xpath, validation_name, validation_pass_msg, validation_fail_msg, validate_exists_after_checked, validate_exists_before_checked, if_condition, if_else_condition]])
        self.validation_exists_frame.pack_forget()
        if self.dropdown_var.get() == "validation":
            self.update_steps(f"Validate-exists: {validation_name}")
        elif self.dropdown_var.get() == "if-else-condition":
            self.update_steps(f"if then exists starts: {validation_name}")
        else:
            self.update_steps(f"if exists starts: {validation_name}")

    def validate_not_exists(self):
        if_condition = False
        if_else_condition = False
        if self.dropdown_var.get() == "if-condition":
            if_condition = True
            self.end_if_button.pack(side=tk.LEFT, padx=5)
        elif self.dropdown_var.get() == "if-else-condition":
            if_condition = True
            if_else_condition = True
            self.end_if_then_button.pack(side=tk.LEFT, padx=5)
        validate_not_exists_after_checked = self.validation_not_exists_after_var.get()
        validate_not_exists_before_checked = self.validation_not_exists_before_var.get()
        validation_name = self.validation_not_exists_name_entry.get()
        validation_pass_msg = self.valNotExists_pass_msg_entry.get()
        validation_fail_msg = self.valNotExists_fail_msg_entry.get()
        xpath = create_xpath()
        now = int(time.time() * 1000)
        conn([["validation-not-exists", now, xpath, validation_name, validation_pass_msg, validation_fail_msg, validate_not_exists_after_checked, validate_not_exists_before_checked, if_condition, if_else_condition]])
        self.variable_value_frame.pack_forget()
        if self.dropdown_var.get() == "validation":
            self.update_steps(f"Validate-not-exists: {validation_name}")
        elif self.dropdown_var.get() == "if-else-condition":
            self.update_steps(f"if then not-exists starts: {validation_name}")
        else:
            self.update_steps(f"if not-exists starts: {validation_name}")

    def validate_equals(self):
        if_condition = False
        if_else_condition = False
        if self.dropdown_var.get() == "if-condition":
            if_condition = True
            self.end_if_button.pack(side=tk.LEFT, padx=5)
        elif self.dropdown_var.get() == "if-else-condition":
            if_condition = True
            if_else_condition = True
            self.end_if_then_button.pack(side=tk.LEFT, padx=5)
        validate_equals_after_checked = self.validation_equals_after_var.get()
        validate_equals_before_checked = self.validation_equals_before_var.get()
        validation_name = self.equals_validation_name_entry.get()
        variable1 = self.equals_variable1_value_entry.get()
        variable2 = self.equals_variable2_value_entry.get()
        validation_pass_msg = self.equals_pass_msg_entry.get()
        validation_fail_msg = self.equals_fail_msg_entry.get()
        now = int(time.time() * 1000)
        conn([["validation-equals", now, validation_name, variable1, variable2, validation_pass_msg, validation_fail_msg, validate_equals_after_checked, validate_equals_before_checked, if_condition, if_else_condition]])
        self.validation_equals_frame.pack_forget()
        if self.dropdown_var.get() == "validation":
            self.update_steps(f"validate-equals: {validation_name}")
        elif self.dropdown_var.get() == "if-else-condition":
            self.update_steps(f"if then equals starts: {validation_name}")
        else:
            self.update_steps(f"if equals starts: {validation_name}")

    def validate_not_equals(self):
        if_condition = False
        if_else_condition = False
        if self.dropdown_var.get() == "if-condition":
            if_condition = True
            self.end_if_button.pack(side=tk.LEFT, padx=5)
        elif self.dropdown_var.get() == "if-else-condition":
            if_condition = True
            if_else_condition = True
            self.end_if_then_button.pack(side=tk.LEFT, padx=5)
        validate_not_equals_after_checked = self.validation_not_equals_after_var.get()
        validate_not_equals_before_checked = self.validation_not_equals_before_var.get()
        validation_name = self.not_equals_validation_name_entry.get()
        variable1 = self.not_equals_variable1_value_entry.get()
        variable2 = self.not_equals_variable2_value_entry.get()
        validation_pass_msg = self.not_equals_pass_msg_entry.get()
        validation_fail_msg = self.not_equals_fail_msg_entry.get()
        now = int(time.time() * 1000)
        conn([["validation-not-equals", now, validation_name, variable1, variable2, validation_pass_msg, validation_fail_msg, validate_not_equals_after_checked, validate_not_equals_before_checked, if_condition, if_else_condition]])
        self.validation_not_equals_frame.pack_forget()
        if self.dropdown_var.get() == "validation":
            self.update_steps(f"validate-not-equals: {validation_name}")
        elif self.dropdown_var.get() == "if-else-condition":
            self.update_steps(f"if then not-equals starts: {validation_name}")
        else:
            self.update_steps(f"if not-equals starts: {validation_name}")

    def validate_num_equals(self):
        if_condition = False
        if_else_condition = False
        if self.dropdown_var.get() == "if-condition":
            if_condition = True
            self.end_if_button.pack(side=tk.LEFT, padx=5)
        elif self.dropdown_var.get() == "if-else-condition":
            if_condition = True
            if_else_condition = True
            self.end_if_then_button.pack(side=tk.LEFT, padx=5)
        validate_num_equals_after_checked = self.validation_num_equals_after_var.get()
        validate_num_equals_before_checked = self.validation_num_equals_before_var.get()
        validation_name = self.num_equals_validation_name_entry.get()
        variable1 = self.num_equals_variable1_value_entry.get()
        variable2 = self.num_equals_variable2_value_entry.get()
        validation_pass_msg = self.num_equals_pass_msg_entry.get()
        validation_fail_msg = self.num_equals_fail_msg_entry.get()
        now = int(time.time() * 1000)
        conn([["validation-num-equals", now, validation_name, variable1, variable2, validation_pass_msg, validation_fail_msg, validate_num_equals_after_checked, validate_num_equals_before_checked, if_condition, if_else_condition]])
        self.validation_num_equals_frame.pack_forget()
        if self.dropdown_var.get() == "validation":
            self.update_steps(f"validate-num-equals: {validation_name}")
        elif self.dropdown_var.get() == "if-else-condition":
            self.update_steps(f"if then num-equals starts: {validation_name}")
        else:
            self.update_steps(f"if num-equals starts: {validation_name}")

    def validate_num_not_equals(self):
        if_condition = False
        if_else_condition = False
        if self.dropdown_var.get() == "if-condition":
            if_condition = True
            self.end_if_button.pack(side=tk.LEFT, padx=5)
        elif self.dropdown_var.get() == "if-else-condition":
            if_condition = True
            if_else_condition = True
            self.end_if_then_button.pack(side=tk.LEFT, padx=5)
        validate_num_not_equals_after_checked = self.validation_num_not_equals_after_var.get()
        validate_num_not_equals_before_checked = self.validation_num_not_equals_before_var.get()
        validation_name = self.num_not_equals_validation_name_entry.get()
        variable1 = self.num_not_equals_variable1_value_entry.get()
        variable2 = self.num_not_equals_variable2_value_entry.get()
        validation_pass_msg = self.num_not_equals_pass_msg_entry.get()
        validation_fail_msg = self.num_not_equals_fail_msg_entry.get()
        now = int(time.time() * 1000)
        conn([["validation-num-not-equals", now, validation_name, variable1, variable2, validation_pass_msg, validation_fail_msg, validate_num_not_equals_after_checked, validate_num_not_equals_before_checked, if_condition, if_else_condition]])
        self.validation_num_not_equals_frame.pack_forget()
        if self.dropdown_var.get() == "validation":
            self.update_steps(f"validate-num-not-equals: {validation_name}")
        elif self.dropdown_var.get() == "if-else-condition":
            self.update_steps(f"if then num-not-equals starts: {validation_name}")
        else:
            self.update_steps(f"if num-not-equals starts: {validation_name}")

    def variable_value(self):
        variable_value_after_checked = self.variable_value_after_var.get()
        variable_value_before_checked = self.variable_value_before_var.get()
        variable_name = self.variable_value_name_entry.get()
        variable_value = self.variable_value_entry.get()
        now = int(time.time() * 1000)
        conn([["variable-value", now, variable_name, variable_value, variable_value_after_checked, variable_value_before_checked]])
        self.variable_value_frame.pack_forget()
        self.update_steps(f"variable-value: {variable_name}")

    def start_loop(self):
        startIndex = self.start_index_entry.get()
        if startIndex == "Enter start index(optional - default to 1)" or not startIndex:
            startIndex = 1
        lastIndex = self.last_index_entry.get()
        increment = self.increment_entry.get()
        if increment == "Enter increment(optional - deafult to 1)" or not increment:
            increment = 1
        counterVar = self.counterVar_entry.get()
        if counterVar == "Assign counter(optional - default to i)" or not counterVar:
            counterVar = "i"
        now = int(time.time() * 1000)
        conn([["start-loop", now, startIndex, lastIndex, increment, counterVar]])
        self.loop_frame.pack_forget()
        self.end_loop_create(counterVar)
        self.update_steps(f"start-loop: Counter var -{counterVar}")

    def insert_step(self):
        custom_step = self.custom_step_entry.get()
        now = int(time.time() * 1000)
        conn([["custom-step", now, custom_step]])
        self.update_steps(f"Custom step enetred : {custom_step}")
        self.insert_custom_frame.pack_forget()


    def copy_to_clipboard(self, position):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.xpath_label.cget("text"))
        self.root.update()
        x, y = position.x_root, position.y_root
        FadingMessage(self.root, "Copied to clipboard!", x, y)


    def update_steps(self, step):
        self.executed_steps.insert(tk.END, step)
        self.executed_steps.see(tk.END)

    def delete_last_step_from_executed_steps(self):
        if self.executed_steps.size() > 0:  # Check if the Listbox is not empty
            last = 1
            last_item = self.get_last_item(last)
            last_index = self.executed_steps.size() - 1  # Index of the last item
            while last_item is not None and (last_item == "Pause Recording" or last_item == "Resume Recording"):   
                last_index -= 1
                last += 1
                last_item = self.get_last_item(last)
            self.executed_steps.delete(last_index)  # Delete the last item

    def get_last_item(self, last):
        if self.executed_steps.size() > 0:  # Check if the Listbox is not empty
            last_index = self.executed_steps.size() - last  # Index of the last item
            return self.executed_steps.get(last_index)  # Get the last item
        else:
            return None  # Return None if the Listbox is empty
    
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    RecorderInstance = Recorder()
    RecorderInstance.run()

