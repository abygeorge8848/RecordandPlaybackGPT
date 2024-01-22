import os
import xml.etree.ElementTree as ET

def pull_activities(folder_path):
    activities = []

    # Iterate over all files in the directory
    for filename in os.listdir(folder_path):
        if filename.endswith(".xml"):
            file_path = os.path.join(folder_path, filename)

            try:
                # Parse the XML file
                tree = ET.parse(file_path)
                root = tree.getroot()

                # Iterate over all 'activity' elements
                for activity in root.findall(".//activity"):
                    activity_id = activity.get('id')
                    if activity_id:
                        activities.append([activity_id, file_path])
            except ET.ParseError:
                print(f"Error parsing file: {file_path}")

    return activities
