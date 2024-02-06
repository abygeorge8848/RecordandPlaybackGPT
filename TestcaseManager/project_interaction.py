import subprocess
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
    flow_path = flow_path.replace('\\', '/')
    try:
        with open(init_path, 'r') as file:
            lines = file.readlines()

        # Updating start.url
        for i in range(len(lines)):
            if lines[i].startswith('start.url='):
                lines[i] = f'start.url={init_url}\n'
                break

        # Initializing flags for flow.xml.path and flow.ids
        found_flow_path = False
        found_flow_ids = False

        # Updating flow.xml.path
        for i in range(len(lines)):
            if lines[i].startswith('flow.xml.path='):
                if found_flow_path:
                    lines[i] = '#' + lines[i]
                else:
                    found_flow_path = True
            elif not found_flow_path:
                lines.insert(i, 'flow.xml.path=\n')
                found_flow_path = True 

        for i in range(len(lines)):
            if lines[i].startswith('flow.xml.path=') and not lines[i].startswith('#flow.xml.path='):
                lines[i] = f'flow.xml.path={flow_path}\n'
                break

        # Updating flow.ids
        for i in range(len(lines)):
            if lines[i].startswith('flow.ids='):
                if found_flow_ids:
                    lines[i] = '#' + lines[i]
                else:
                    found_flow_ids = True
            elif not found_flow_ids:
                lines.insert(i, 'flow.ids=\n')
                found_flow_ids = True

        for i in range(len(lines)):
            if lines[i].startswith('flow.ids=') and not lines[i].startswith('#flow.ids='):
                lines[i] = f'flow.ids={flow_ids}\n'
                break  

        with open(init_path, 'w') as file:
            file.writelines(lines)

        print("Finished writing to init.properties")
        return True  # File saved successfully

    except Exception as e:
        print(f"Error occurred while writing to init.properties: {e}")
        return False  # File not saved due to an error
    


def find_start_line_number_of_element(root, flow_id):
        print(f"Searching for flow id : {flow_id}...")
        line_number = 1  # Line numbers typically start at 1 
        for elem in root.iter():
            if elem.tag == 'flow' and elem.get('id') == flow_id:
                return line_number  # Return the line number when the flow_id matches
            line_number += 1     
        return None  # Return None if the flow_id is not found


def open_flow(vs_code_path, flow_id, flow_path):
    tree = ET.parse(flow_path)
    root = tree.getroot()
    start_line_number = find_start_line_number_of_element(root, flow_id)

    if start_line_number:
        vs_code_path = vs_code_path.replace('/', '\\')
        command = [vs_code_path, '-g', f"{flow_path}:{start_line_number}"]
        subprocess.Popen(command, shell=True)
    else:
        print(f'Flow ID {flow_id} not found in the XML.')
