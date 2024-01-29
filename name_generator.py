class NameGenerator:
    def __init__(self, activity_start=1, flow_start=1, variable_start=1, validation_start=1, excel_variable_start=1):
        self.activity_counter = activity_start - 1  # Subtracting 1 so that the first call to get a name returns the start value
        self.flow_counter = flow_start - 1
        self.variable_counter = variable_start - 1
        self.validation_counter = validation_start - 1
        self.excel_variable_counter = excel_variable_start - 1

    def get_activity_name(self):
        self.activity_counter += 1
        return f"activity_{self.activity_counter}"

    def get_flow_name(self):
        self.flow_counter += 1
        return f"flow_{self.flow_counter}"

    def get_variable_name(self):
        self.variable_counter += 1
        return f"variable_{self.variable_counter}"
    
    def get_validation_name(self):
        self.validation_counter += 1
        return f"validation_{self.validation_counter}"
    
    def get_excel_variable_name(self):
        self.excel_variable_counter += 1
        return f"excelVar_{self.excel_variable_counter}"