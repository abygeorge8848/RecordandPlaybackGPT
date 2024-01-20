import tkinter as tk
from tkinter import filedialog, ttk


def choose_file():
    file_path = filedialog.askopenfilename()
    file_path_entry.delete(0, tk.END)
    file_path_entry.insert(0, file_path)

def start_recorder():
    activity_name = activity_name_entry.get()
    activity_description = activity_description_entry.get()
    file_path = file_path_entry.get()
    root.destroy()


root = tk.Tk()
root.title('Activity Configuration')

style = ttk.Style()
style.configure('TLabel', padding=5)
style.configure('TButton', padding=5)
style.configure('TEntry', padding=5)

# Configure the grid layout
root.columnconfigure(1, weight=1)

# Activity Name
ttk.Label(root, text='Activity Name:', style='TLabel').grid(row=0, column=0, sticky=tk.W)
activity_name_entry = ttk.Entry(root)
activity_name_entry.grid(row=0, column=1, sticky=tk.EW, padx=10, pady=5)

# Activity Description
ttk.Label(root, text='Activity Description:', style='TLabel').grid(row=1, column=0, sticky=tk.W)
activity_description_entry = ttk.Entry(root)
activity_description_entry.grid(row=1, column=1, sticky=tk.EW, padx=10, pady=5)

# File Chooser
ttk.Label(root, text='Choose File:', style='TLabel').grid(row=2, column=0, sticky=tk.W)
file_path_entry = ttk.Entry(root)
file_path_entry.grid(row=2, column=1, sticky=tk.EW, padx=10, pady=5)
ttk.Button(root, text='Choose File', command=choose_file, style='TButton').grid(row=2, column=2, padx=10, pady=5)

# Start Recorder Button
ttk.Button(root, text='Start Recorder', command=start_recorder, style='TButton').grid(row=3, column=0, columnspan=3, pady=10)

root.mainloop()
