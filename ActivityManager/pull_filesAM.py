import os
import xml.etree.ElementTree as ET
import openpyxl


def pull_activities(folder_path, base_excel_path):
    activities = []
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.endswith(".xml"):
                file_path = os.path.join(dirpath, filename)
                try:
                    tree = ET.parse(file_path)
                    root = tree.getroot()
                    for activity in root.findall(".//activity"):
                        activity_id = activity.get('id')
                        if activity_id:
                            activity_path = activity_id + "   PATH : " + file_path
                            unique_excel_name = activity_id + "_" + (file_path.split('.')[0]).replace('/', '-').strip().replace("\\", "-").replace(":", "") + ".xlsx"
                            excel_file_path = os.path.join(base_excel_path, unique_excel_name)
                            if os.path.exists(excel_file_path):
                                # If the excel file exists, get the sheet names
                                sheet_names = get_excel_sheet_names(excel_file_path)
                            else:
                                sheet_names = []

                            activities.append([activity_path, file_path, sheet_names, unique_excel_name])
                except ET.ParseError as e:
                    print(f"Error parsing file: {file_path}, Error: {e}")
                    continue
    return activities

def get_excel_sheet_names(excel_file_path):
    workbook = openpyxl.load_workbook(excel_file_path, read_only=True)
    return workbook.sheetnames