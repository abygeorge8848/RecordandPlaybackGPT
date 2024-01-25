import os
import xml.etree.ElementTree as ET


def pull_activities(file_path):
    activities = []
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        for activity in root.findall(".//flow"):
            activity_id = activity.get('id')
            if activity_id:
                activity_path = activity_id + "   PATH : " + file_path 
                activities.append([activity_path, file_path])
    except ET.ParseError as e:
        # Log the error and continue with the next file
        print(f"Error parsing file: {file_path}, Error: {e}")

    return activities



def write_init(init_path, init_url, flow_path, flow_ids):
    with open(init_path, 'r') as file:
        lines = file.readlines()
    found_flow_ids = False
    for i in range(len(lines)):
        if lines[i].startswith('flow.ids='):
            if found_flow_ids:
                lines[i] = '#' + lines[i]
            else:
                found_flow_ids = True
        elif not found_flow_ids:
            lines.insert(i, 'flow.ids=\n')
            found_flow_ids = True
        if lines[i].startswith('flow.xml.path='):
            if found_flow_ids:
                lines[i] = '#' + lines[i]
            else:
                found_flow_ids = True
        elif not found_flow_ids:
            lines.insert(i, 'flow.xml.path=\n')
            found_flow_ids = True
    for i in range(len(lines)):
        if lines[i].startswith('flow.ids=') and not lines[i].startswith('#flow.ids='):
            lines[i] = f'flow.ids={flow_ids}\n'
            break  
        if lines[i].startswith('flow.xml.path=') and not lines[i].startswith('#flow.xml.path='):
            lines[i] = f'flow.xml.path={flow_path}\n'
            break  
    for i in range(len(lines)):
        if lines[i].startswith('start.url='):
            lines[i] = f'start.url={init_url}\n'
            break  
    with open(init_path, 'w') as file:
        file.writelines(lines)
        file.flush()
        file.close()
        print("Finished writing to init.properties")