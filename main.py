from main_controller import MainController

if __name__ == "__main__":
    controller = MainController()
    controller.show_testcase_manager()  
    controller.testcase_manager_instance.root.mainloop()