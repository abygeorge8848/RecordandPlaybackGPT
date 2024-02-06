from IDE_AM import ActivityManager
from IDE_TM import TestcaseManager
from ActivityConfigure_IDE import ActivityConfig
from flaskapp import start_flask_app
from Recorder_IDE import Recorder

class MainController:
    def __init__(self):
        # Initialize all GUI instances
        self.testcase_manager_instance = TestcaseManager(self)
        self.activity_manager_instance = ActivityManager(self)
        self.activity_config_instance = ActivityConfig(self)
        self.recorder_instance = None

    def show_testcase_manager(self):
        self.hide_all_guis()
        self.testcase_manager_instance.run()

    def show_activity_manager(self):
        self.hide_all_guis()
        self.activity_manager_instance.run()

    def show_activity_config(self):
        self.hide_all_guis()
        self.activity_config_instance.run()

    def start_recorder(self, activity_name, activity_description, activity_path):
        # Create Recorder instance when you have the necessary data
        start_flask_app()
        if not self.recorder_instance:
            # Ensure the order of arguments matches the Recorder class's __init__ method
            self.recorder_instance = Recorder(activity_name, activity_description, activity_path, self)
        self.show_recorder()

    def show_recorder(self):
        self.hide_all_guis()
        if self.recorder_instance:
            self.recorder_instance.run()

    def hide_all_guis(self):
        self.testcase_manager_instance.withdraw()
        self.activity_manager_instance.withdraw()
        self.activity_config_instance.withdraw()
        if self.recorder_instance:
            self.recorder_instance.withdraw()
    


