import tkinter as tk
from tkinter import filedialog, ttk



class ActivityConfig():
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.root = tk.Tk()
        self.root.title('Activity Configuration')

        self.style = ttk.Style()
        self.style.configure('TLabel', padding=5)
        self.style.configure('TButton', padding=5)
        self.style.configure('TEntry', padding=5)

        # Configure the grid layout
        self.root.columnconfigure(1, weight=1)

        # Activity Name
        ttk.Label(self.root, text='Activity Name:', style='TLabel').grid(row=0, column=0, sticky=tk.W)
        self.activity_name_entry = ttk.Entry(self.root)
        self.activity_name_entry.grid(row=0, column=1, sticky=tk.EW, padx=10, pady=5)

        # Activity Description
        ttk.Label(self.root, text='Activity Description:', style='TLabel').grid(row=1, column=0, sticky=tk.W)
        self.activity_description_entry = ttk.Entry(self.root)
        self.activity_description_entry.grid(row=1, column=1, sticky=tk.EW, padx=10, pady=5)

        # File Chooser
        ttk.Label(self.root, text='Choose File:', style='TLabel').grid(row=2, column=0, sticky=tk.W)
        self.file_path_entry = ttk.Entry(self.root)
        self.file_path_entry.grid(row=2, column=1, sticky=tk.EW, padx=10, pady=5)
        ttk.Button(self.root, text='Choose File', command=self.choose_file, style='TButton').grid(row=2, column=2, padx=10, pady=5)

        # Start Recorder Button
        ttk.Button(self.root, text='Start Recorder', command=self.start_recorder, style='TButton').grid(row=3, column=0, columnspan=3, pady=8)
        ttk.Button(self.root, text='Back', command=self.back_to_ActivityManager, style='TButton').grid(row=4, column=0, columnspan=3, pady=4)

    
    def choose_file(self):
        file_path = filedialog.askopenfilename()
        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, file_path)

    def start_recorder(self):
        activity_name = self.activity_name_entry.get()
        activity_description = self.activity_description_entry.get()
        file_path = self.file_path_entry.get()
        self.controller.start_recorder(activity_name, activity_description, file_path)

    def back_to_ActivityManager(self):
        print("Let's head back to the Activity Manager!")
        self.controller.show_activity_manager()

    def run(self):
        self.root.deiconify()

    def withdraw(self):
        self.root.withdraw()



if __name__ == "__main__":
    ActivityConfigManager = ActivityConfig()
    ActivityConfigManager.run()
