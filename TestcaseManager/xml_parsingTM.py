import xml.etree.ElementTree as ET
import os

def retrieve_activities(flow_name, path):
    tree = ET.parse(path)
    root = tree.getroot()
    # Find the <flow> element with the specified id
    flow = root.find(f".//flow[@id='{flow_name}']")
    # Check if the flow is found
    if flow is not None:
        # Initialize a list to store xml attribute values
        xml_activities = []
        # Iterate through all <call> tags and extract xml attribute
        for call in flow.findall('call'):
            xml_path = call.get('xml')
            xml_activity = call.get('activity')
            excel_path = call.get('excelPath')
            if xml_path is not None:
                xml_activities.append({"activity": xml_activity, "path": xml_path, "excelPath": excel_path})
        print(xml_activities)
        # Return the list
        return xml_activities
    else:
        print(f"No flow found with id {flow_name}")



def update_activity_paths(data, base_path):
    project_container = 'ProjectContainer'
    project_name_start = base_path.find(project_container) + len(project_container) + 1
    project_name_end = base_path.find('\\', project_name_start)
    project_path = base_path[:project_name_end]

    # Updating paths for each activity
    updated_data = []
    for item in data:
        # Concatenating the project path with individual activity paths
        full_path = os.path.join(project_path, item['path'].strip('.\\').replace('\\', '/'))
        updated_data.append({'activity': item['activity'], 'path': full_path})

    print(f"The activities with their associated absolute path is : {updated_data}")
    return updated_data



def insert_recorder_ids_recursively(element, recorder_id_counter, root):
    for child in element:
        # Skip the activity tag itself
        if child.tag != 'activity':
            # Assign recorderId to the current child element
            child.set('recorderId', f'recorder_id_step_{recorder_id_counter}')
            recorder_id_counter += 1
        # Special handling for 'if' and 'validation' tags
        if child.tag in ['if', 'validation']:
            val_group_ids = child.get('valGroupIds')
            if val_group_ids:
                val_group = root.find(f".//valGroup[@groupId='{val_group_ids}']")
                if val_group is not None:
                    # Find the 'validate' child within 'valGroup' and assign recorderId
                    validate_tag = val_group.find('validate')
                    if validate_tag is not None:
                        validate_tag.set('recorderId', f'recorder_id_step_{recorder_id_counter}')
                        recorder_id_counter += 1

        # Recursively process all child elements
        recorder_id_counter = insert_recorder_ids_recursively(child, recorder_id_counter, root)

    return recorder_id_counter



def insert_recorder_id(data):
    print(f"The activities with the recorder ids to be inserted are: \n{data}")
    recorder_id_counter = 1
    for activity_info in data:
        activity_id = activity_info['activity']
        file_path = activity_info['path']
        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()
        # Find the <activity> element with the specified id
        print(f"Searching for activity with ID: {activity_id}")
        activity = root.find(f".//activity[@id='{activity_id}']")
        if activity is not None:
            # Insert recorder IDs recursively starting from the activity element's children
            recorder_id_counter = insert_recorder_ids_recursively(activity, recorder_id_counter, root)
            print(f"Recorder IDs injected for activity '{activity_id}' in '{file_path}'")
            # Save the modified XML back to the file
            tree.write(file_path)
        else:
            print(f"Activity '{activity_id}' not found in '{file_path}'")





