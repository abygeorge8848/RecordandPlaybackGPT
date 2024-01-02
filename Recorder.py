# First part of the code: Recording User Actions on Web UI
#import spacy
#from spacy.matcher import Matcher
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
from gpt import align_input_steps


from openai_auth import get_token


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Load NLP model
#nlp = spacy.load("en_core_web_sm")
#matcher = Matcher(nlp.vocab)

# Initialize list to store recorded actions
recorded_actions = []


paused_time_total= 0
paused_at = None

instruction_frame = None
instruction_entry = None



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



def process_instruction():

    deployment_id, gpt_model, embedding_model, openai = get_token()

    instruction = instruction_entry.get()
    tag_found = align_input_steps(instruction)


    # If there's a match, it indicates the user wants to retrieve text
    if "getText" in tag_found or  "validate-exists" in tag_found or "validate-not-exists" in tag_found: 
        xpath = driver.execute_script("""
           document.addEventListener('click', function getTextEvent(e) {
            e.preventDefault();
            e.stopPropagation();
            var xpath = computeXPath(e.target);
            console.log(xpath);
            window.clickedElementXPath = xpath;
        });

            function computeXPath(element) {
                if (!element) return null;

                function escapeXPathString(str) {
                    if (!str.includes("'")) return `'${str}'`;
                    if (!str.includes('"')) return `"${str}"`;
                    let parts = str.split("'");
                    let xpathString = "concat(";
                    for (let i = 0; i < parts.length; i++) {
                        xpathString += `'${parts[i]}'`;
                        if (i < parts.length - 1) {
                            xpathString += `, "'", `;
                        }
                    }
                    xpathString += ")";

                    return xpathString;
                }

                function isUniqueByAttribute(element, attrName) {
                    let attrValue = element.getAttribute(attrName);
                    if (!attrValue) return false;
                    let xpath = `//${element.tagName.toLowerCase()}[@${attrName}=${escapeXPathString(attrValue)}]`;
                    return document.evaluate("count(" + xpath + ")", document, null, XPathResult.ANY_TYPE, null).numberValue === 1;
                }

                function isUniqueByText(element) {
                    let text = element.textContent.trim();
                    if (!text) return false;
                    let xpath = `//${element.tagName.toLowerCase()}[contains(text(), ${escapeXPathString(text)})]`;
                    return document.evaluate("count(" + xpath + ")", document, null, XPathResult.ANY_TYPE, null).numberValue === 1;
                }

                function getChildRelativeXPath(child, parent) {
                    var path = '';
                    for (var current = child; current && current !== parent; current = current.parentNode) {
                        let index = 1;
                        for (var sibling = current.previousElementSibling; sibling; sibling = sibling.previousElementSibling) {
                            if (sibling.nodeType === 1 && sibling.tagName === current.tagName) {
                                index++;
                            }
                        }
                        let tagName = current.tagName.toLowerCase();
                        let pathIndex = (index > 1 ? `[${index}]` : '');
                        path = '/' + tagName + pathIndex + path;
                    }
                    return path;
                }

                // Function to generate a unique XPath using parent attributes
                function generateRelativeXPath(element) {
                    var paths = [];
                    var currentElement = element;

                    while (currentElement && currentElement.nodeType === 1) {
                        let uniqueAttributeXPath = getUniqueAttributeXPath(currentElement);
                        if (uniqueAttributeXPath) {
                            paths.unshift(uniqueAttributeXPath);
                            break; // Break the loop if a unique attribute is found
                        }

                        let tagName = currentElement.tagName.toLowerCase();
                        let index = 1;
                        for (let sibling = currentElement.previousElementSibling; sibling; sibling = sibling.previousElementSibling) {
                            if (sibling.nodeType === 1 && sibling.tagName === currentElement.tagName) {
                                index++;
                            }
                        }
                        let pathIndex = (index > 1 ? `[${index}]` : '');
                        paths.unshift(`${tagName}${pathIndex}`);

                        currentElement = currentElement.parentNode;
                    }

                    return paths.length ? `//${paths.join('/')}` : null;
                }

                function getUniqueAttributeXPath(element) {
                    const attributes = ['id', 'name', 'type', 'value', 'title', 'alt', 'col-id', 'colid', 'ref', 'role', 'ng-bind'];
                    for (let attr of attributes) {
                        if (isUniqueByAttribute(element, attr)) {
                            return `${element.tagName.toLowerCase()}[@${attr}='${element.getAttribute(attr)}']`;
                        }
                    }
                    return null;
                }    

                // Special handling for svg elements
                if (element.tagName.toLowerCase() === 'svg' || element.tagName.toLowerCase() === 'path') {
                    let parentElement = element.parentElement;
                    if (parentElement) {
                        let parentXPath = computeXPath(parentElement);
                        if (parentXPath) {
                            if (parentXPath.startsWith('//')){
                                return parentXPath;
                            } else if (parentXPath.startsWith('/')){
                                return '/' + parentXPath;
                            } else {
                                return '//' + parentXPath;
                            }	
                        }
                    }
                    return null;
                }

                const attributes = ['id', 'name', 'type', 'value', 'title', 'alt', 'col-id', 'colid', 'ref', 'role', 'ng-bind'];
                for (let attr of attributes) {
                    if (isUniqueByAttribute(element, attr)) {
                        return `//${element.tagName.toLowerCase()}[@${attr}='${element.getAttribute(attr)}']`;
                    }
                }

                if (element.className && typeof element.className === 'string') {	
                    let classes = element.className.trim().split(/\s+/);
                    let combinedClassSelector = classes.join('.');
                    let xpath = `//${element.tagName.toLowerCase()}[contains(@class, '${combinedClassSelector}')]`;
                    if (document.evaluate("count(" + xpath + ")", document, null, XPathResult.ANY_TYPE, null).numberValue === 1) {
                        return xpath;
                    }
                }

                if (element.tagName.toLowerCase() !== 'i' && isUniqueByText(element)) {
                    return `//${element.tagName.toLowerCase()}[contains(text(), ${escapeXPathString(element.textContent.trim())})]`;
                }

                return generateRelativeXPath(element);
                }
        """)

    time.sleep(3)
    all_ok = True
    for tag in tag_found:
        if tag:
            if tag in ["getText", "validation-exists", "validation-not-exists"]:
                xpath = driver.execute_script("return window.clickedElementXPath || '';")
                print(f"The xpath is : {xpath}")
                if not xpath:
                    all_ok = False
                    messagebox.showwarning("Action Recorder", "No element selected. Please try again.")
        else:
            print("No tag has been found while processing the instruction")


        

def escape_js_string(s):
    return s.replace("'", "\\'")


def xpath_instructions(xpath, tag, instruction):
    if xpath:
        escaped_tag = escape_js_string(tag)
        escaped_xpath = escape_js_string(xpath)
        escaped_instruction = escape_js_string(instruction)
        js_script = f"""
            function sendEventsToServerSync() {{
                console.log("Sending the respective event to the server");
                if (window.isSending || window.recordedEvents.length === 0) {{
                    return; // Do not send if a send operation is in progress or if there are no events to send
                }}
                window.isSending = true;
                var xhr = new XMLHttpRequest();
                xhr.open("POST", 'http://localhost:9000/save', true);
                xhr.onreadystatechange = function() {{
                    if (xhr.readyState == 4) {{
                        if (xhr.status == 200) {{
                            console.log('Event data sent successfully');
                        }}
                        window.isSending = false;
                        window.recordedEvents = []; // Clear the recorded events after sending
                    }}
                }};
                xhr.setRequestHeader('Content-Type', 'application/json');
                xhr.send(JSON.stringify(window.recordedEvents));
            }}
            window.recordedEvents.push(['{escaped_tag}', Date.now(), '{escaped_xpath}', '{escaped_instruction}']);
            sendEventsToServerSync();
            window.clickedElementXPath = null;
        """
        driver.execute_script(js_script)
    
    else:
        messagebox.showwarning("Action Recorder", "No element selected. Please try again.")


def parameterless_instruction(tag, instruction):
    js_script = f"""
        function sendEventsToServerSync() {{
            console.log("Sending the respective event to the server");
            if (window.isSending || window.recordedEvents.length === 0) {{
                return; // Do not send if a send operation is in progress or if there are no events to send
            }}
            window.isSending = true;
            var xhr = new XMLHttpRequest();
            xhr.open("POST", 'http://localhost:9000/save', true);
            xhr.onreadystatechange = function() {{
                if (xhr.readyState == 4) {{
                    if (xhr.status == 200) {{
                        console.log('Event data sent successfully');
                    }}
                    window.isSending = false;
                    window.recordedEvents = []; // Clear the recorded events after sending
                }}
            }};
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.send(JSON.stringify(window.recordedEvents));
        }}
        window.recordedEvents.push([`'{tag}'`, Date.now(), `'{instruction}'`]);
        sendEventsToServerSync();
        window.clickedElementXPath = null;
    """
    driver.execute_script(js_script)




# Set up listeners
def set_up_listeners():
    # Injecting JS to add click and input event listeners
    js_script = """
        if (!window.hasInjected) {
            window.recordedEvents = [];
            window.hasInjected = true;
            window.isPaused = false;

            console.log("Listeners have been set up");
            function sendEventsToServerSync() {
                console.log("Sending the respective event to the server");
                if (window.isSending || window.recordedEvents.length === 0) {
                    return; // Do not send if a send operation is in progress or if there are no events to send
                }
                window.isSending = true;

                var xhr = new XMLHttpRequest();
                xhr.open("POST", 'http://localhost:9000/save', true);
                xhr.onreadystatechange = function() {
                    if (xhr.readyState == 4) {
                        if (xhr.status == 200) {
                            console.log('Event data sent successfully');
                        }
                        window.isSending = false;
                        window.recordedEvents = []; // Clear the recorded events after sending
                    }
                };

                xhr.setRequestHeader('Content-Type', 'application/json');
                xhr.send(JSON.stringify(window.recordedEvents));
            }

            var clickTimer;
            var doubleClickFlag = false;

            document.addEventListener('dblclick', function(e) {
                console.log("Double Click ...");
                if (window.isPaused) return;
                doubleClickFlag = true;
                clearTimeout(clickTimer);
                var xpath = computeXPath(e.target);
                window.recordedEvents.push(['dblClick', Date.now(), xpath]);
                sendEventsToServerSync();
            });

            document.addEventListener('click', function(e) {
                if (window.isPaused) return;
                if (!doubleClickFlag) {
                    clearTimeout(clickTimer);
                    clickTimer = setTimeout(function() {
                        if (!doubleClickFlag) {
                            console.log("You clicked right now ...");
                            var xpath = computeXPath(e.target);
                            window.recordedEvents.push(['click', Date.now(), xpath]);
                            sendEventsToServerSync();
                        }
                        doubleClickFlag = false;
                    }, 300); // Adjust the timeout duration (300ms) as needed
                }
            });


            document.addEventListener('keypress', function(e) {
                if (window.isPaused) return;
                var xpath = computeXPath(e.target);
                window.recordedEvents.push(['input', Date.now(), xpath, e.key]);
                sendEventsToServerSync();  
            });

            function recordPageLoadEvent() {
                if (window.recordedEvents.length === 0 || window.recordedEvents[window.recordedEvents.length - 1][0] !== 'WaitForPageLoad') {
                    window.recordedEvents.push(['WaitForPageLoad', Date.now()]);
                    sendEventsToServerSync();  
                }
            }

            document.addEventListener('scroll', function(e) {
                if (window.isPaused) return;
                var xpath = computeXPathOfElementAt20Percent()
                window.recordedEvents.push(['scroll', Date.now(), xpath]);
                sendEventsToServerSync();  
            });

            function computeXPathOfElementAt20Percent() {
                var yPosition = window.innerHeight * 0.25; 
                var elements = document.elementsFromPoint(window.innerWidth / 2, yPosition);
                for (var i = 0; i < elements.length; i++) {
                    var xpath = computeXPath(elements[i]);
                    if (xpath) {
                        return xpath;
                    }
                }
                return null;
            }

            recordPageLoadEvent();

            function computeXPath(element) {
                if (!element) return null;

                function escapeXPathString(str) {
                    if (!str.includes("'")) return `'${str}'`;
                    if (!str.includes('"')) return `"${str}"`;
                    let parts = str.split("'");
                    let xpathString = "concat(";
                    for (let i = 0; i < parts.length; i++) {
                        xpathString += `'${parts[i]}'`;
                        if (i < parts.length - 1) {
                            xpathString += `, "'", `;
                        }
                    }
                    xpathString += ")";

                    return xpathString;
                }

                function isUniqueByAttribute(element, attrName) {
                    let attrValue = element.getAttribute(attrName);
                    if (!attrValue) return false;
                    let xpath = `//${element.tagName.toLowerCase()}[@${attrName}=${escapeXPathString(attrValue)}]`;
                    return document.evaluate("count(" + xpath + ")", document, null, XPathResult.ANY_TYPE, null).numberValue === 1;
                }

                function isUniqueByText(element) {
                    let text = element.textContent.trim();
                    if (!text) return false;
                    let xpath = `//${element.tagName.toLowerCase()}[contains(text(), ${escapeXPathString(text)})]`;
                    return document.evaluate("count(" + xpath + ")", document, null, XPathResult.ANY_TYPE, null).numberValue === 1;
                }

                function getChildRelativeXPath(child, parent) {
                    var path = '';
                    for (var current = child; current && current !== parent; current = current.parentNode) {
                        let index = 1;
                        for (var sibling = current.previousElementSibling; sibling; sibling = sibling.previousElementSibling) {
                            if (sibling.nodeType === 1 && sibling.tagName === current.tagName) {
                                index++;
                            }
                        }
                        let tagName = current.tagName.toLowerCase();
                        let pathIndex = (index > 1 ? `[${index}]` : '');
                        path = '/' + tagName + pathIndex + path;
                    }
                    return path;
                }

                // Function to generate a unique XPath using parent attributes
                function generateRelativeXPath(element) {
                    var paths = [];
                    var currentElement = element;

                    while (currentElement && currentElement.nodeType === 1) {
                        let uniqueAttributeXPath = getUniqueAttributeXPath(currentElement);
                        if (uniqueAttributeXPath) {
                            paths.unshift(uniqueAttributeXPath);
                            break; // Break the loop if a unique attribute is found
                        }

                        let tagName = currentElement.tagName.toLowerCase();
                        let index = 1;
                        for (let sibling = currentElement.previousElementSibling; sibling; sibling = sibling.previousElementSibling) {
                            if (sibling.nodeType === 1 && sibling.tagName === currentElement.tagName) {
                                index++;
                            }
                        }
                        let pathIndex = (index > 1 ? `[${index}]` : '');
                        paths.unshift(`${tagName}${pathIndex}`);

                        currentElement = currentElement.parentNode;
                    }

                    return paths.length ? `//${paths.join('/')}` : null;
                }

                function getUniqueAttributeXPath(element) {
                    const attributes = ['id', 'name', 'type', 'value', 'title', 'alt', 'col-id', 'colid', 'ref', 'role', 'ng-bind'];
                    for (let attr of attributes) {
                        if (isUniqueByAttribute(element, attr)) {
                            return `${element.tagName.toLowerCase()}[@${attr}='${element.getAttribute(attr)}']`;
                        }
                    }
                    return null;
                }    

                // Special handling for svg elements
                if (element.tagName.toLowerCase() === 'svg' || element.tagName.toLowerCase() === 'path') {
                    let parentElement = element.parentElement;
                    if (parentElement) {
                        let parentXPath = computeXPath(parentElement);
                        if (parentXPath) {
                            if (parentXPath.startsWith('//')){
                                return parentXPath;
                            } else if (parentXPath.startsWith('/')){
                                return '/' + parentXPath;
                            } else {
                                return '//' + parentXPath;
                            }	
                        }
                    }
                    return null;
                }

                const attributes = ['id', 'name', 'type', 'value', 'title', 'alt', 'col-id', 'colid', 'ref', 'role', 'ng-bind'];
                for (let attr of attributes) {
                    if (isUniqueByAttribute(element, attr)) {
                        return `//${element.tagName.toLowerCase()}[@${attr}='${element.getAttribute(attr)}']`;
                    }
                }

                if (element.className && typeof element.className === 'string') {	
                    let classes = element.className.trim().split(/\s+/);
                    let combinedClassSelector = classes.join('.');
                    let xpath = `//${element.tagName.toLowerCase()}[contains(@class, '${combinedClassSelector}')]`;
                    if (document.evaluate("count(" + xpath + ")", document, null, XPathResult.ANY_TYPE, null).numberValue === 1) {
                        return xpath;
                    }
                }

                if (element.tagName.toLowerCase() !== 'i' && isUniqueByText(element)) {
                    return `//${element.tagName.toLowerCase()}[contains(text(), ${escapeXPathString(element.textContent.trim())})]`;
                }

                return generateRelativeXPath(element);
                }          



        }
    """
    
    result = driver.execute_script(js_script)
    print("The script has been injected successfully!")


def backup_events_to_server():
    global driver
    try:
        # Use execute_script instead of execute_async_script to block execution until the script completes
        response = driver.execute_script("""
            // Create a synchronous XMLHttpRequest to ensure that the function waits for the response
            var xhr = new XMLHttpRequest();
            xhr.open('POST', 'http://localhost:9000/save', false);  // false for synchronous request
            xhr.setRequestHeader('Content-Type', 'application/json');

            var tempRecordedEvents = [...window.recordedEvents];
            window.recordedEvents = [];  // Clear the recorded events
            xhr.send(JSON.stringify(tempRecordedEvents));

            // Check for successful response
            if (xhr.status === 200) {
                return JSON.parse(xhr.responseText);  // Assuming the server responds with JSON
            } else {
                throw new Error('Failed to backup events: ' + xhr.statusText);
            }
        """)
        print(f"The response from the server is :  {response}")
        return response
    except Exception as e:
        print("Exception in backup_events_to_server: ", e)



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




# Modify stop_and_show_records to call GPT-4 script
def stop_and_show_records():

    gpt_input = []
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
                request.open('GET', 'http://localhost:9000/retrieve', false);  // false for synchronous
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


        #if recorded_events:
        #    recorded_events = json.loads(recorded_events)
        recorded_events = combined_events

        print(f"\n\nRecorded events: {recorded_events}\n\n\n")
        #driver.execute_script("sessionStorage.removeItem('recordedEvents');")        

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
                input_string = f"wait : time={wait_time}, "
                gpt_input.append(input_string)
                event_queue.append({"event": "wait", "time": wait_time})
                prev_event_was_wait = True
                prev_event_was_waitforpageload == False

            if event_type == "click" or event_type == "dblClick" or event_type == "scroll" or event_type == "getText":
                if combined_input:
                    input_string = f"input : xpath={combined_xpath} and value={combined_input}, "
                    gpt_input.append(input_string)
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                xpath = others[0]
                input_string = f"{event_type} : xpath={xpath}, "
                gpt_input.append(input_string)
                event_queue.append({"event": event_type, "xpath": xpath})
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
                        input_string = f"input : xpath={combined_xpath} value={combined_input}, "
                        gpt_input.append(input_string)
                        event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = char
                    combined_xpath = xpath
                prev_event_was_input = True
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False
            
            elif event_type == "validation-exists" or event_type == "validation-not-exists" :
                xpath = others[0]
                instruction = others[1]
                if combined_input:
                    input_string = f"input : xpath={combined_xpath} and value={combined_input}, "
                    gpt_input.append(input_string)
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                event_queue.append({"event": event_type, "xpath": xpath, "instruction": instruction})
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False

            elif event_type == "loop" or event_type == "if-condition" or event_type == "validation-equals" or event_type == "validation-starts-with" or event_type == "validation-ends-with" or event_type == "variable-expression" or event_type == "validation-num-equals" or event_type == "validation-num-not-equals" or event_type == "validation-num-le" or event_type == "validation-num-ge" or event_type == "validation-contains":
                instruction = others[1]
                if combined_input:
                    input_string = f"input : xpath={combined_xpath} and value={combined_input}, "
                    gpt_input.append(input_string)
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                event_queue.append({"event": event_type, "instruction": instruction})
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False


            elif event_type == "WaitForPageLoad" and prev_event_was_waitforpageload == False:
                if combined_input:
                    input_string = f"input : xpath={combined_xpath} and value={combined_input}, "
                    gpt_input.append(input_string)
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                prev_event_was_waitforpageload = True
                input_string = "WaitForPageLoad, "
                gpt_input.append(input_string)
                event_queue.append({"event": "WaitForPageLoad"})
                prev_event_was_wait = False

            last_time = timestamp
        # Print any remaining combined input after loop ends
        if combined_input:
            input_string += f'input : xpath="{combined_xpath}" value="{combined_input}'
            gpt_input.append(input_string)
            event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
            #print(f'input : xpath="{combined_xpath}" value="{combined_input}" ')

        stop_thread_flag.set()
        driver.quit()


        def update_wait_times(input_str):
            parts = input_str.split(', ')
            updated_parts = []

            j = 0
            while j < len(parts):
                if 'wait : time' in parts[j]:
                    total_wait_time = int(parts[j].split('=')[1])
                    j += 1
                    while j < len(parts) and 'wait : time' in parts[j]:
                        total_wait_time += int(parts[i].split('=')[1])
                        j += 1
                    updated_parts.append(f'wait : time={total_wait_time}')
                else:
                    updated_parts.append(parts[j])
                    j += 1

            return ', '.join(updated_parts)        

        gpt_input = [update_wait_times(entry) for entry in gpt_input]

 
        #print(f"\n\n The value of gpt_input is : {gpt_input}")
    
        counter = 0
        while counter < len(gpt_input)-1:
            if (gpt_input[counter] == gpt_input[counter+1]) or (gpt_input[counter] == 'wait : time=0'):
                gpt_input.pop(counter)
            if 'scroll' in gpt_input[counter] and 'scroll' in gpt_input[counter+1]:
                gpt_input.pop(counter)
            
            counter += 1

        ###################################################
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
        ###################################################


        cleaned_gpt_input_1 = []
        for element in gpt_input:
            if "scroll" in element:
                if not cleaned_gpt_input_1 or "scroll" not in cleaned_gpt_input_1[-1]:
                    cleaned_gpt_input_1.append(element)
            else:
                cleaned_gpt_input_1.append(element)

        gpt_input = cleaned_gpt_input_1

        ###################################################
        i = 0
        while i < len(event_queue) - 1: 
            current_event = event_queue[i]["event"]
            next_event = event_queue[i + 1]["event"]
            if current_event == "scroll" and next_event == "scroll":
                event_queue.pop(i)
            else:
                i += 1
        ###################################################
        print(f"\n\n The event_queue for execution is : {event_queue}\n\n")

        completed_code= ""
        while len(gpt_input) > 0:
            gpt_input_string = ""
            input_count = 8 if len(gpt_input) >= 8 else len(gpt_input)
            for i in range(input_count):
                gpt_input_string += gpt_input.pop(0)
            # Call GPT-4 script with formatted actions
            gpt_input_string = gpt_input_string[:-2]
            #print("\n\n")
            print(f"The gpt_input_string is : \n{gpt_input_string}\n\n")
            #print("\n\n\n The PAF code equavalent is : \n\n")
            #completed_code += get_PAF_code(gpt_input_string) + "\n\n"
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
     








