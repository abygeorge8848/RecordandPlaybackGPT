import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import time
import math
import json
import urllib3
import threading
from RunPAF import run_file, report_open
from reformat_paf import reformat_paf_activity, reformat_paf_flow
from refactored_js import listeners, xpath_js


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


recorded_actions = []
paused_time_total= 0
paused_at = None


# Initialize Chrome driver and options
chrome_options = Options()
chrome_options.add_argument("--disable-web-security")  # WARNING: This is unsafe for regular browsing
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--remote-allow-origins=*")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--incognito")
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_argument('--ignore-certificate-errors')

download_path = "./downloads"  # Update this path
prefs = {
    "download.default_directory": download_path,
    "download.prompt_for_download": False,
    "plugins.plugins_disabled": ["Adobe Flash Player", "Chrome PDF Viewer"]
}
chrome_options.add_experimental_option("prefs", prefs)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
actions = ActionChains(driver)



# Set up listeners
def set_up_listeners():
    # Injecting JS to add click and input event listeners
    js_script = listeners
    result = driver.execute_script(js_script)
    print("The script has been injected successfully!")


def monitor_page_load(stop_thread_flag):
    global driver
    old_url = driver.current_url
    while not stop_thread_flag.is_set():
        try:
            time.sleep(0.01)
            if driver:
                new_url = driver.current_url
                if new_url != old_url:
                    print(f"URL : '{old_url}' has been changed to '{new_url}'")
                    print("URL change detected. Preparing to backup data ...")
                    #server_response = backup_events_to_server()
                    print("Page has navigated. Reinjecting scripts...")
                    WebDriverWait(driver, 240).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    set_up_listeners()
                    old_url = new_url
        except Exception as e:
            print("Exception in monitor_page_load: ", e)
            break


stop_thread_flag = threading.Event()


# Loop to continuously check for user inactivity
def start_recording(url):
    global driver, actions, start_time, last_time, stop_thread_flag, init_url
    init_url = url
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    actions = ActionChains(driver)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    set_up_listeners()

    stop_thread_flag.clear()
    monitor_thread = threading.Thread(target=monitor_page_load, args=(stop_thread_flag,))
    monitor_thread.daemon = True
    monitor_thread.start()
    
    start_time = time.time() * 1000
    last_time = time.time() * 1000



def pause_recording_main():
    global is_paused, paused_at, driver
    is_paused = True
    paused_at = time.time() * 1000
    driver.execute_script("window.isPaused = true;")

def resume_recording_main():
    global is_paused, paused_at, paused_time_total, driver
    if paused_at:
        pause_duration = (time.time() * 1000) - paused_at
        paused_time_total += pause_duration
    is_paused = False
    paused_at = None
    driver.execute_script("window.isPaused = false;")


def create_xpath():
    xpath = driver.execute_async_script(xpath_js)
    return xpath


# Modify stop_and_show_records to call GPT-4 script
def stop_and_show_records():

    global driver, last_time, paused_time_total, stop_thread_flag
    if driver:

        combined_events = []
        try:
            final_session_events = driver.execute_script("return window.recordedEvents || [];")
            if final_session_events:
                print(f"\n\n\n Successfully retrieved the final session events : \n{final_session_events}\n\n\n")
            else:
                final_session_events = []


            server_events = driver.execute_script("""
                var request = new XMLHttpRequest();
                request.open('GET', 'http://localhost:9005/retrieve', false);  // false for synchronous
                request.send(null);
                if (request.status === 200) {
                    return request.responseText;
                }
                return '[]';
            """)
            if server_events:
                server_events = json.loads(server_events)
                print(f"\n\n Retrieved the events from the server : \n{server_events} \n\n")
            else:
                server_events = []

            #combined_events = server_events + final_session_events
            combined_events = server_events
            print(f"\n\n The combined events are : {combined_events}\n\n")
        
        except Exception as e:
            print("Exception in stop_and_show_records: ", e)


        recorded_events = combined_events

        print(f"\n\nRecorded events: {recorded_events}\n\n\n")

        last_time = start_time
        prev_event_was_input = False
        prev_event_was_wait = False
        prev_event_was_waitforpageload = False
        combined_input = None
        combined_xpath = None

        event_queue = []
        for event in recorded_events:
            event_type, timestamp, *others = event

            # Print wait only if previous event wasn't input or current event is not input
            if (not prev_event_was_input or event_type != "input") and ((event_type != "WaitForPageLoad" and not prev_event_was_waitforpageload) and not prev_event_was_wait):
                wait_time = abs(math.ceil((timestamp - last_time - paused_time_total) / 1000.0)) * 1000
                paused_time_total=0
                event_queue.append({"event": "wait", "time": wait_time})
                prev_event_was_wait = True
                prev_event_was_waitforpageload == False

            if event_type == "click" or event_type == "dblClick" or event_type == "scroll":
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                xpath = others[0]
                event_queue.append({"event": event_type, "xpath": xpath})
                prev_event_was_input = False 
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False

            elif event_type == "getText":
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                xpath = others[0]
                variable = others[1]
                event_queue.append({"event": event_type, "xpath": xpath, "variable": variable})
                prev_event_was_input = False 
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False

            elif event_type == "variable-value":
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                variable_name = others[0]
                variable_value = others[1]
                event_queue.append({"event": event_type, "name": variable_name, "value": variable_value})
                prev_event_was_input = False 
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False

            elif event_type == "validation-exists" or event_type == "validation-not-exists":
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                xpath = others[0]
                validation_name = others[1]
                pass_msg = others[2]
                fail_msg = others[3]
                event_queue.append({"event": event_type, "validation_name": validation_name, "xpath": xpath, "pass_msg": pass_msg, "fail_msg": fail_msg})
                prev_event_was_input = False 
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False

            elif event_type == "validation-equals" or event_type == "validation-not-equals":
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                validation_name = others[0]
                variable1 = others[1]
                variable2 = others[2]
                pass_msg = others[3]
                fail_msg = others[4]
                event_queue.append({"event": event_type, "validation_name": validation_name, "variable1": variable1, "variable2": variable2, "pass_msg": pass_msg, "fail_msg": fail_msg})
                prev_event_was_input = False 
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False

            elif event_type == "input":
                xpath = others[0]
                char = others[1]
                if prev_event_was_input and xpath == combined_xpath:
                    combined_input += char
                else:
                    if combined_input:
                        event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = char
                    combined_xpath = xpath
                prev_event_was_input = True
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False

            elif event_type == "loop" or event_type == "if-condition" or event_type == "validation-equals" or event_type == "validation-starts-with" or event_type == "validation-ends-with" or event_type == "variable-expression" or event_type == "validation-num-equals" or event_type == "validation-num-not-equals" or event_type == "validation-num-le" or event_type == "validation-num-ge" or event_type == "validation-contains":
                instruction = others[1]
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                event_queue.append({"event": event_type, "instruction": instruction})
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False


            elif event_type == "WaitForPageLoad" and prev_event_was_waitforpageload == False:
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                prev_event_was_waitforpageload = True
                event_queue.append({"event": "WaitForPageLoad"})
                prev_event_was_wait = False

            last_time = timestamp
        # Print any remaining combined input after loop ends
        if combined_input:
            event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})

        stop_thread_flag.set()
        driver.quit()


        def process_wait_in_queue(event_queue):
            i = 0
            while i < len(event_queue):
                if event_queue[i]["event"] == "wait":
                    total_time = event_queue[i]["time"]
                    if total_time == 0:
                        event_queue.pop(i)
                        continue

                    j = i+1
                    while j < len(event_queue) and event_queue[j]["event"] == "wait":
                        total_time += event_queue[j]["time"]
                        j += 1
                    
                    event_queue[i]["time"] = total_time
                    for _ in range(j - i -1):
                        event_queue.pop(i+1)

                i += 1
            
            return event_queue
        
        event_queue = process_wait_in_queue(event_queue)

        i = 0
        while i < len(event_queue) - 1: 
            current_event = event_queue[i]["event"]
            next_event = event_queue[i + 1]["event"]
            if current_event == "scroll" and next_event == "scroll":
                event_queue.pop(i)
            else:
                i += 1
#
        print(f"\n\n The event_queue for execution is : {event_queue}\n\n")

        completed_code= ""
        
        PAF_ACTIVITY = reformat_paf_activity(event_queue)
        completed_code = PAF_ACTIVITY["PAF_SCRIPT"]
        activity_id = PAF_ACTIVITY["activity_id"]
        

        #flows_code = get_flow_code(completed_code)
        FLOWS = reformat_paf_flow(activity_id)
        flows_code = FLOWS["PAF_FLOW"]
        flow_id = FLOWS["flow_id"]

        flow_path = "C:/Users/u1138322/PAF/ProjectContainer/SampleProject/sample_xml/flow.xml"
        activity_path = "C:/Users/u1138322/PAF/ProjectContainer/SampleProject/sample_xml/activity.xml"
        init_path = "C:/Users/u1138322/PAF/ProjectContainer/SampleProject/src/init.properties"

        completed_code = "<activities>\n\n" + completed_code + "\n\n</activities>"
        with open(activity_path, 'w') as f:
            f.write(completed_code)


        flows_code = "<flows>\n\n" + flows_code + "\n\n</flows>"
        with open(flow_path, 'w') as f:
            f.write(flows_code)

        with open(init_path, 'r') as file:
            lines = file.readlines()

        # Flag to check if 'flow.ids=' has been found
        found_flow_ids = False

        # Iterate through the lines and modify as needed
        for i in range(len(lines)):
            if lines[i].startswith('flow.ids='):
                if found_flow_ids:
                    # Add a '#' at the start of the line to comment it out
                    lines[i] = '#' + lines[i]
                else:
                    found_flow_ids = True
            elif not found_flow_ids:
                # If 'flow.ids=' hasn't been found yet, add a new line with 'flow.ids='
                lines.insert(i, 'flow.ids=\n')
                found_flow_ids = True


        for i in range(len(lines)):
            if lines[i].startswith('flow.ids=') and not lines[i].startswith('#flow.ids='):
                # Replace the value of the uncommented 'flow.ids=' line
                lines[i] = f'flow.ids={flow_id}\n'
                break  # Stop processing the file after modifying the line

        # Iterate through the lines and find the 'start.url=' line
        for i in range(len(lines)):
            if lines[i].startswith('start.url='):
                # Replace the value of the 'start.url=' line
                lines[i] = f'start.url={init_url}\n'
                break  # Stop processing the file after modifying the line

                # Write the modified content back to the file

        with open(init_path, 'w') as file:
            file.writelines(lines)
            # Explicitly flush and close the file (optional, as 'with open' should handle it)
            file.flush()
            file.close()
            print("Finished writing to init.properties")

    
    return 1
     








