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
import threading
import warnings
import urllib3


from openai_auth import get_token


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=urllib3.exceptions.PoolFullWarning)
warnings.filterwarnings("ignore", category=urllib3.exceptions.MaxRetryError)

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
    raw_response = gpt_call(openai, gpt_model, deployment_id, instruction)
    
    tag_found = raw_response.choices[0]["message"]["content"]
    # If there's a match, it indicates the user wants to retrieve text
    if "getText" in tag_found or  "validation" in tag_found:
        driver.execute_script("""
            document.addEventListener('click', function getTextEvent(e) {
                e.preventDefault();
                e.stopPropagation();
                var xpath = computeXPath(e.target);
                console.log(xpath);
                window.clickedElementXPath = xpath;
                document.removeEventListener('click', getTextEvent);
            });

            function computeXPath(element) {
                var paths = [];
                for (; element && element.nodeType == 1; element = element.parentNode) {
                    var index = 0;
                    for (var sibling = element.previousSibling; sibling; sibling = sibling.previousSibling) {
                        if (sibling.nodeType == 1 && sibling.tagName == element.tagName)
                            index++;
                    }
                    var tagName = element.tagName.toLowerCase();
                    var pathIndex = (index ? "[" + (index + 1) + "]" : "");
                    paths.splice(0, 0, tagName + pathIndex);
                }
                return paths.length ? "/" + paths.join("/") : null;
            }
        """)
        if "getText" in tag_found:
            root.after(2000, get_text_instruction)
        elif "validation" in tag_found:
            root.after(2000, validation_instruction)

    elif "validation" in tag_found:
        pass
        # Give user a brief moment to click the element they want to get text from
        



def get_text_instruction():
    xpath = driver.execute_script("return window.clickedElementXPath || '';")
    if xpath:
        js_script = f"""
            function saveEvents() {{
                sessionStorage.setItem('recordedEvents', JSON.stringify(window.recordedEvents));
            }}
            window.recordedEvents.push(['getText', Date.now(), '{xpath}']);
            saveEvents();
            window.clickedElementXPath = null;
        """
        driver.execute_script(js_script)
    
    else:
        messagebox.showwarning("Action Recorder", "No element selected. Please try again.")


def validation_instruction():
    xpath = driver.execute_script("return window.clickedElementXPath || '';")
    if xpath:
        js_script = f"""
            function saveEvents() {{
                sessionStorage.setItem('recordedEvents', JSON.stringify(window.recordedEvents));
            }}
            window.recordedEvents.push(['validate that an element exists', Date.now(), '{xpath}']);
            saveEvents();
            window.clickedElementXPath = null;
        """
        driver.execute_script(js_script)
    else:
        messagebox.showwarning("Action Recorder", "No element selected. Please try again.")



# Set up listeners
def set_up_listeners():
    # Injecting JS to add click and input event listeners
    js_script = """
        if (!window.hasInjected) {
            window.recordedEvents = [];

            //window.recordedEvents = JSON.parse(sessionStorage.getItem('recordedEvents')) || [];
            window.hasInjected = true;
            window.isPaused = false;

            // Function to save events to session storage
            function saveEvents() {
                sessionStorage.setItem('recordedEvents', JSON.stringify(window.recordedEvents));
            }

            document.addEventListener('submit', function(e) {
                window.recordedEvents.push(['formSubmit', Date.now(), computeXPath(e.target)]);
                saveEvents();
                sendEventsToServerSync();  // Add this line
            }, true);

            function sendEventsToServerSync() {
                var xhr = new XMLHttpRequest();
                xhr.open("POST", 'http://localhost:5000/save', false);  // false for synchronous request
                xhr.setRequestHeader('Content-Type', 'application/json');
                xhr.send(JSON.stringify(window.recordedEvents));
            }

            window.addEventListener('beforeunload', saveEvents);

            document.addEventListener('click', function(e) {
            if (window.isPaused) return;  // Add this condition
                var xpath = computeXPath(e.target);
                window.recordedEvents.push(['click', Date.now(), xpath]);
                saveEvents();
            });

            document.addEventListener('dblclick', function(e) {
                if (window.isPaused) return;
                var xpath = computeXPath(e.target);
                window.recordedEvents.push(['dblClick', Date.now(), xpath]);
                saveEvents();
            });

            document.addEventListener('keypress', function(e) {
                if (window.isPaused) return;  // Add this condition
                var xpath = computeXPath(e.target);
                window.recordedEvents.push(['input', Date.now(), xpath, e.key]);
                saveEvents();
            });

            function recordPageLoadEvent() {
                if (window.recordedEvents.length === 0 || window.recordedEvents[window.recordedEvents.length - 1][0] !== 'WaitForPageLoad') {
                    window.recordedEvents.push(['WaitForPageLoad', Date.now()]);
                    saveEvents();
                }
            }

            recordPageLoadEvent();

            function computeXPath(element) {
                if (!element) return null;
                if (element.id) return `//*[@id="${element.id}"]`;
                var attributes = element.attributes;
                var path = '';
                for (var i = 0; i < attributes.length; i++) {
                    var attr = attributes[i];
                    if (attr.specified && attr.name !== 'id' && attr.name !== 'class') {
                        path = `//${element.tagName.toLowerCase()}[@${attr.name}='${attr.value}']`;
                        if (document.evaluate("count(" + path + ")", document, null, XPathResult.ANY_TYPE, null).numberValue === 1) {
                            return path;
                        }
                    }
                }
                var paths = [];
                for (; element && element.nodeType === 1; element = element.parentNode) {
                    var index = 0;
                    var sibling = element.previousSibling;
                    for (; sibling; sibling = sibling.previousSibling) {
                        if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                            index++;
                        }
                    }
                    var tagName = element.tagName.toLowerCase();
                    var pathIndex = (index ? "[" + (index + 1) + "]" : "");
                    paths.splice(0, 0, tagName + pathIndex);
                    if (element.parentElement && element.parentElement.id) {
                        return `//*[@id="${element.parentElement.id}"]/${paths.join("/")}`;
                    }
                }
                return paths.length ? "/" + paths.join("/") : null;
            }
        }
    """
    
    result = driver.execute_script(js_script)
    print(f"Script injection result: {result}")


def backup_events_to_server():
    global driver
    try:
        response = driver.execute_async_script("""
            var done = arguments[0];
            var tempRecordedEvents = window.recordedEvents;
            window.recordedEvents = [];  // Clear the events array immediately
            window.isPaused = true;  // Pause event recording

            fetch('http://localhost:5000/save', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(tempRecordedEvents)
            })
            .then(function(response) {
                if (response.ok) {
                    sessionStorage.removeItem('recordedEvents');
                } else {
                    // If not successful, re-add the events for retry
                    window.recordedEvents = window.recordedEvents.concat(tempRecordedEvents);
                }
                window.isPaused = false;  // Resume event recording
                done(true);
            })
            .catch(function(error) {
                console.error('Error:', error);
                window.recordedEvents = window.recordedEvents.concat(tempRecordedEvents);
                window.isPaused = false;  // Resume event recording
                done(false);
            });
        """)
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
                    backup_events_to_server()
                    print("Page has navigated. Reinjecting scripts...")
                    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    set_up_listeners()
                    old_url = new_url
        except Exception as e:
            print("Exception in monitor_page_load: ", e)
            break



stop_thread_flag = threading.Event()

# Loop to continuously check for user inactivity
def start_recording():
    global driver, actions, start_time, last_time, stop_thread_flag
    url = url_entry.get()
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



def pause_recording():
    global is_paused, paused_at, driver
    is_paused = True
    paused_at = time.time() * 1000
    driver.execute_script("window.isPaused = true;")
    show_instruction_entry()

def resume_recording():
    global is_paused, paused_at, paused_time_total, driver
    hide_instruction_entry()
    if paused_at:
        pause_duration = (time.time() * 1000) - paused_at
        paused_time_total += pause_duration
    is_paused = False
    paused_at = None
    driver.execute_script("window.isPaused = false;")

def hide_instruction_entry():
    global instruction_frame
    if instruction_frame:
        instruction_frame.destroy()

    
def show_instruction_entry():
    global instruction_frame, instruction_entry
    instruction_frame = tk.Frame(frame, pady=10)
    instruction_frame.grid(row=2, column=0, columnspan=3, pady=10)

    instruction_label = tk.Label(instruction_frame, text="What do you want to do?")
    instruction_label.grid(row=0, column=0)

    instruction_entry = tk.Entry(instruction_frame, width=40)
    instruction_entry.grid(row=0, column=1)

    go_btn = tk.Button(instruction_frame, text="Go!", command=process_instruction)
    go_btn.grid(row=0, column=2)



# Modify stop_and_show_records to call GPT-4 script
def stop_and_show_records():
    #backup_events_to_server()

    gpt_input = []
    global driver, last_time, paused_time_total, stop_thread_flag
    if driver:

        combined_events = []
        try:
            final_session_events = driver.execute_script("return sessionStorage.getItem('recordedEvents');")
            if final_session_events:
                final_session_events = json.loads(final_session_events)
                print(f"\n\n\n Successfully retrieved the final session events : \n{final_session_events}\n\n\n")
            else:
                final_session_events = []

            server_events = driver.execute_script("""
                var request = new XMLHttpRequest();
                request.open('GET', 'http://localhost:5000/retrieve', false);  // false for synchronous
                request.send(null);
                if (request.status === 200) {
                    return request.responseText;
                }
                return '[]';
            """)
            if server_events:
                server_events = json.loads(server_events)
                print(f"\n\n\n Retrieved the events from the server : \n{server_events} \n\n\n")
            else:
                server_events = []

            combined_events = server_events + final_session_events
            #combined_events = server_events
            print(f"\n\n The combined events are : {combined_events}")
        
        except Exception as e:
            print("Exception in stop_and_show_records: ", e)


        #if recorded_events:
        #    recorded_events = json.loads(recorded_events)
        recorded_events = combined_events

        print(f"Recorded events: {recorded_events}\n\n\n")
        driver.execute_script("sessionStorage.removeItem('recordedEvents');")        

        last_time = start_time
        prev_event_was_input = False
        prev_event_was_wait = False
        prev_event_was_waitforpageload = False
        combined_input = None
        combined_xpath = None
        for event in recorded_events:
            event_type, timestamp, *others = event

            # Print wait only if previous event wasn't input or current event is not input
            if (not prev_event_was_input or event_type != "input") and ((event_type != "WaitForPageLoad" and not prev_event_was_waitforpageload) and not prev_event_was_wait):
                wait_time = abs(math.ceil((timestamp - last_time - paused_time_total) / 1000.0)) * 1000
                paused_time_total=0
                input_string = f"wait : time={wait_time}, "
                gpt_input.append(input_string)
                prev_event_was_wait = True
                prev_event_was_waitforpageload == False

            if event_type == "click":
                if combined_input:
                    input_string = f"input : xpath={combined_xpath} and value={combined_input}, "
                    gpt_input.append(input_string)
                    combined_input = None
                    combined_xpath = None
                xpath = others[0]
                input_string = f"click : xpath={xpath}, "
                gpt_input.append(input_string)
                prev_event_was_input = False
                
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False

            elif event_type == "dblClick":
                 if combined_input:
                    input_string = f"input : xpath={combined_xpath} and value={combined_input}, "
                    gpt_input.append(input_string)
                    combined_input = None
                    combined_xpath = None
                 xpath = others[0]
                 input_string = f"dblClick : xpath={xpath}, "
                 gpt_input.append(input_string)
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
                    combined_input = char
                    combined_xpath = xpath
                prev_event_was_input = True
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False

            elif event_type == "getText":
                if combined_input:
                    input_string = f"input : xpath={combined_xpath} and value={combined_input}, "
                    gpt_input.append(input_string)
                    combined_input = None
                    combined_xpath = None
                input_string = f"get text xpath={xpath}, "
                gpt_input.append(input_string)
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False

            elif event_type == "WaitForPageLoad" and prev_event_was_waitforpageload == False:
                if combined_input:
                    input_string = f"input : xpath={combined_xpath} and value={combined_input}, "
                    gpt_input.append(input_string)
                    combined_input = None
                    combined_xpath = None
                prev_event_was_waitforpageload = True
                input_string = "WaitForPageLoad, "
                gpt_input.append(input_string)
                prev_event_was_wait = False

            last_time = timestamp
        # Print any remaining combined input after loop ends
        if combined_input:
            input_string += f'input : xpath="{combined_xpath}" value="{combined_input}'
            gpt_input.append(input_string)
            #print(f'input : xpath="{combined_xpath}" value="{combined_input}" ')

        stop_thread_flag.set()
        driver.quit()
    
        counter = 0
        while counter < len(gpt_input)-1:
            if (gpt_input[counter] == gpt_input[counter+1]) or (gpt_input[counter] == 'wait : time=0'):
                gpt_input.pop(counter)
            
            counter += 1
        
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
        while len(gpt_input) > 0:
            gpt_input_string = ""
            input_count = 10 if len(gpt_input) > 9 else len(gpt_input)
            for i in range(input_count):
                gpt_input_string += gpt_input.pop(0)
            # Call GPT-4 script with formatted actions
            #print("\n\n")
            print(f"The gpt_input_string is : \n{gpt_input_string}")
            #print("\n\n\n The PAF code equavalent is : \n\n")
            #get_PAF_code(gpt_input_string)
        
    

# GUI setup
root = tk.Tk()
root.title("Action Recorder")
root.geometry("500x250")  # Adjust the initial window size for a better look

# Configure style
font_main = ("Arial", 12)
font_button = ("Arial", 10)

# Main frame
frame = tk.Frame(root, padx=30, pady=30)
frame.pack(padx=20, pady=20, expand=True, fill=tk.BOTH)

# URL components
url_label = tk.Label(frame, text="Enter URL:", font=font_main)
url_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 15))

url_entry = tk.Entry(frame, width=40, font=font_main)
url_entry.grid(row=0, column=1, columnspan=2, pady=(0, 15), sticky=tk.W)

# Buttons
button_frame = tk.Frame(frame)
button_frame.grid(row=1, column=0, columnspan=3, pady=10)

start_btn = tk.Button(button_frame, text="Start", command=start_recording, width=12, font=font_button)
start_btn.grid(row=0, column=0, padx=5)

stop_btn = tk.Button(button_frame, text="Stop & Show", command=stop_and_show_records, width=12, font=font_button)
stop_btn.grid(row=0, column=1, padx=5)

pause_btn = tk.Button(button_frame, text="Pause", command=pause_recording, width=12, font=font_button)
pause_btn.grid(row=1, column=0, padx=5, pady=(10, 0))

resume_btn = tk.Button(button_frame, text="Resume", command=resume_recording, width=12, font=font_button)
resume_btn.grid(row=1, column=1, padx=5, pady=(10, 0))

# Second part of the code: Interfacing with GPT-4 for PAF code generation

def get_PAF_code(formatted_actions):
    deployment_id, gpt_model, embedding_model, openai = get_token()

    query_final = ""
    for action_item in recorded_actions:
        single_action = action_item[0] + " : " + action_item[1]
        query_final += single_action + ',\n' 

    formatted_response = gpt_call(openai, gpt_model, deployment_id, formatted_actions)
    #print(f"\n\n\n The queries are : {query_final}")
    #print("\n\n\n The PAF code equavalent is : \n\n")
    print(formatted_response.choices[0]["message"]["content"])

def gpt_call(openai, gpt_model, deployment_id, question):
    # Define the prompt for GPT-4
    prompt = (f"""
    The below content gives information about an XML framework named PAF. Use that information to create the PAF code for the user query  
    Some attributes for each tag will be given. If an attribute is not given then please fill the attribute value,  
    with an appropriate value according to the attribute description. In case direct PAF code is given, then you can
    directly use it along with the rest of the given input. Only return the PAF code in the correct syntax and format.
              PAF MANUAL 
              ----------
              Every set of set instructions must be enclosed in an activity tag :
              <activity id="activity_name">
               -
               -
               -
              </activity>
            
              The activity can be given an appropriate name which represents the actions in it. Simply replace the 'activity_name' 
              in the id attribute with an appropriate name which describes what the activity is doing.
              Now the content inside the activity tag would be the individual functionality. Each functionality
              be a simple tag like <click xpath=""></click>, <input xpath="" value=""></input> which form the
              building blocks of PAF. Now let us explore some PAF tags with their corresponding functionality.

              To do a click action :
              <click xpath="xpath_value"></click>
              Here the xpath attribute represents the xpath of the element you want to click on. 'Replace xpath_value'
              with the xpath of the respective element.

              To input some text into a textbox :
              <input xpath="xpath_value" value="value_to_be_entered">
              xpath attribute is the xpath of the textbox you want to enter your text in.
              The value attribute represents the text you want to enter in the textfield.

              To wait for a specified amount of time in ms :
              <wait time="time_in_ms"></wait>
              Where the time attribute is the time in ms. A wait tag should not appear consecutively. If such an input appears, 
              just add up the wait times and return it as one wait tag with the combined wait time.

              To wait till the page has loaded :
              <WaitForPageLoad/>
              A wait tag should not appear immediately before or after a WaitForPageLoad.

              To double click on an element :
              <dblClick xpath="xpath_value"></dblClick>
              The xpath attribute is the xpath of the element you need to double click on

              To scroll to a particular element :
              <scroll xpath="xpath_value"></scroll>
              Where xpath is the element to be scrolled to.

              To get the text of an element :
              <getText xpath="xpath_value" variable="variable_name"></getText>
              The xpath attribute represents the xpath of the element whose text is to be read.
              The variable attribute represents an appropriate name for the variable in which the text is to be 
              stored. If there are multiple variables in a single activity, each variable name must be unique.

              Sometimes, some values will be required to be saved in order to be used in other tags like
              validation, etc. This is the variable tag : 
              <variable keyName="variable_name" value="variable_value">
              Here, keyName represents an appropriate name for the variable with respect to its intent for storing
              or the content stored in it. 
              value attribute represents the value of the variable stored. When the value of another variable is to
              be called, it can be called in an attribute in the format - attribute equals dollar sign open and close curly 
              braces with the variable named enclosed in the open and closed curly braces.

              To perform validations, the validation tag is used in conjunctions with a valGroup.
              First, we need to define the appropriate valGroup which will be then referenced by the validation.
              Let us look at the various valGroups - 
                1. To validate that a certain element exists in the UI :
                   <valGroup groupId="group-id">
                      <validate xpath="xpath_value" exists="true/false" passMsg="An appropriate pass message to indicate why this is considered as a passed case" failMsg="A corresponding fail message to explain in case the condition fails">
                   </valGroup
                   groupId is an appropriate and unique name given to the valGroup     
              
                   Here xpath represents the xpath of the element we want to verify in the UI.
                   exists can be equal to true or false, depending on whether we want to check if the element exists or not in the UI.
                   passMsg should be the message in case the condition passes to explain what is being validated.
                   failMsg should be the message in case the condition fails.

              Include the valGroup outside of the <activity> ONLY. To call the valGroup within the activity, use the validation tag :
                <validation valGroupIds="group-id">
              Here, the valGroupIds must have the same group id as the vlGroup it is referencing.

              """)
    
    # Make the API call to GPT-4
    response = openai.ChatCompletion.create(
        deployment_id=deployment_id,
        model=gpt_model,
        temperature=0,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": question}
        ],
    )

    return response



def gpt_call_2(openai, gpt_model, deployment_id, question):
    # Define the prompt for GPT-4
    prompt = (f"""
    The below content gives information about an XML framework named PAF. In PAF, each tag or a group of tags in
    some cases, represent a functionality. Use the below information to generate the PAF code for the user query  
    Some attributes for each tag will be given. If an attribute is not given then please fill the attribute value,  
    with an appropriate value according to the attribute description. In case direct PAF code is given, then you can
    directly use it along with the rest of the given input. Only return the PAF code in the correct syntax and format.
              
              PAF MANUAL 
              ----------

              To do a click action :

              To wait till the page has loaded :
              <WaitForPageLoad/>

              To get the text of an element :
              <getText xpath="xpath_value" variable="variable_name"></getText>
              The xpath attribute represents the xpath of the element whose text is to be read.
              The variable attribute represents an appropriate name for the variable in which the text is to be 
              stored. If there are multiple variables in a single activity, each variable name must be unique.

              Sometimes, some values will be required to be saved in order to be used in other tags like
              validation, etc. This is the variable tag : 
              <variable keyName="variable_name" value="variable_value">
              Here, keyName represents an appropriate name for the variable with respect to its intent for storing
              or the content stored in it. 
              value attribute represents the value of the variable stored. When the value of another variable is to
              be called, it can be called in an attribute in the format - attribute equals dollar sign open and close curly 
              braces with the variable named enclosed in the open and closed curly braces.

              To perform validations, the validation tag is used in conjunctions with a valGroup.
              First, we need to define the appropriate valGroup which will be then referenced by the validation.
              Let us look at the various valGroups - 
                1. To validate that a certain element exists in the UI :
                   <valGroup groupId="group-id">
                      <validate xpath="xpath_value" exists="true/false" passMsg="An appropriate pass message to indicate why this is considered as a passed case" failMsg="A corresponding fail message to explain in case the condition fails">
                   </valGroup
                   groupId is an appropriate and unique name given to the valGroup     
              
                   Here xpath represents the xpath of the element we want to verify in the UI.
                   exists can be equal to true or false, depending on whether we want to check if the element exists or not in the UI.
                   passMsg should be the message in case the condition passes to explain what is being validated.
                   failMsg should be the message in case the condition fails.

              To call the valGroup, use the validation tag :
                <validation valGroupIds="group-id">
              Here, the valGroupIds must have the same group id as the vlGroup it is referencing.

              """)
    
    # Make the API call to GPT-4
    response = openai.ChatCompletion.create(
        deployment_id=deployment_id,
        model=gpt_model,
        temperature=0,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": question}
        ],
    )

    return response


def gpt_call_flow(openai, gpt_model, deployment_id, question):
    # Define the prompt for GPT-4
    prompt = (f"""
                Convert the given activities from the PAF framework into flows to be used.

              """)
    
    # Make the API call to GPT-4
    response = openai.ChatCompletion.create(
        deployment_id=deployment_id,
        model=gpt_model,
        temperature=0,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": question}
        ],
    )

    return response

# Start the tkinter main loop
if __name__ == "__main__":
    root.mainloop()
