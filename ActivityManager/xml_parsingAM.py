import xml.etree.ElementTree as ET
import os



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



def insert_flow(flow_name, flow_desc, flow_path, activities_with_sheets):
    try:
        with open(flow_path, 'r') as file:
            lines = file.readlines()
        
        for i, line in enumerate(lines):
            if '<flows>' in line:
                # Insert a new line and the provided text after '<flows>'
                lines.insert(i + 1, '\n')
                lines.insert(i + 2, f'\t<flow id="{flow_name}" desc="{flow_desc}" name="{flow_name} : {flow_desc}" summary="{flow_desc}">\n')
                j = 0
                for activity in activities_with_sheets:
                    activity_name = activity['activity']
                    xml_path = activity['path']
                    excelPath = activity['sheets'][0]['excelPath']
                    sheetName = activity['sheets'][0]['sheetName']
                    lines.insert(i+3+j, f'\t\t<call activity="{activity_name}" xml="{xml_path}" excelPath="{excelPath}" sheetName="{sheetName}"></call>\n')
                    j += 1
                lines.insert(i+3+j, f'\t</flow>\n')
                break  # Exit the loop after inserting
        
        # Write the modified content back to the file
        with open(flow_path, 'w') as file:
            file.writelines(lines)
            
    except Exception as e:
        print(f"An error occurred: {e}")