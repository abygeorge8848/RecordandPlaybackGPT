import os
import xml.etree.ElementTree as ET

def pull_activities(folder_path):
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
                            activities.append([activity_path, file_path])
                except ET.ParseError as e:
                    # Log the error and continue with the next file
                    print(f"Error parsing file: {file_path}, Error: {e}")
                    continue  # Skip to the next file
    return activities

