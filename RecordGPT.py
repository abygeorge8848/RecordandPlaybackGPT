# First part of the code: Recording User Actions on Web UI
import spacy
from spacy.matcher import Matcher
import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import time
import math

from openai_auth import get_token

# Load NLP model
nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

# Initialize list to store recorded actions
recorded_actions = []

paused_time_total= 0
paused_at = None

instruction_frame = None
instruction_entry = None



# Initialize Chrome driver and options
chrome_options = Options()
chrome_options.add_argument("--disable-web-security")  # THIS IS UNSAFE FOR REGULAR BROWSING
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=chrome_options)
actions = ActionChains(driver)


def process_instruction():

    deployment_id, gpt_model, embedding_model, openai = get_token()

    instruction = instruction_entry.get()
    raw_response = gpt_call(openai, gpt_model, deployment_id, instruction)
    
    tag_found = raw_response.choices[0]["message"]["content"]
    # If there's a match, it indicates the user wants to retrieve text
    if "getText" in tag_found or "validation" in tag_found:
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
        # Give user a brief moment to click the element they want to get text from
        root.after(2000, fetch_text_instruction)


def get_xpath(element):
    return driver.execute_script("""
        function getElementXPath(element) {
            if (element.id) {
                return 'id("' + element.id + '")';
            }
            var pathSegments = [];
            for (; element && element.nodeType === Node.ELEMENT_NODE; element = element.parentNode) {
                var segment = element.localName || null;
                if (!segment) {
                    continue;
                }
                segment = segment.toLowerCase();
                var siblings = [];
                var sibling = element.parentNode.firstChild;
                do {
                    if (sibling.nodeType === Node.DOCUMENT_TYPE_NODE) {
                        continue;
                    }
                    if (sibling.nodeName === element.nodeName) {
                        siblings.push(sibling);
                    }
                } while (sibling = sibling.nextSibling);
                if (siblings.length > 1) {
                    segment += '[' + (siblings.indexOf(element) + 1) + ']';
                }
                pathSegments.unshift(segment);
            }
            return pathSegments.length ? './' + pathSegments.join('/') : null;
        }
        return getElementXPath(arguments[0]);
    """, element)



def fetch_text_instruction():
    xpath = driver.execute_script("return window.clickedElementXPath || '';")
    if xpath:
        print(f'<getText xpath="{xpath}"></getText>')
        driver.execute_script(f"window.recordedEvents.push(['getText', '{xpath}', Date.now()]);")
        # Reset after processing
        driver.execute_script("window.clickedElementXPath = null;")
    else:
        messagebox.showwarning("Action Recorder", "No element selected. Please try again.")



# Set up listeners
def set_up_listeners():
    # Injecting JS to add click and input event listeners
    js_script = """
        if (!window.hasInjected) {
            window.recordedEvents = [];
            window.hasInjected = true;
            window.isPaused = false;

            document.addEventListener('click', function(e) {
            if (window.isPaused) return;  // Add this condition
                var xpath = computeXPath(e.target);
                window.recordedEvents.push(['click', xpath, Date.now()]);
            });

            document.addEventListener('keypress', function(e) {
                if (window.isPaused) return;  // Add this condition
                var xpath = computeXPath(e.target);
                window.recordedEvents.push(['input', xpath, Date.now(), e.key]);
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
        }
    """
    
    result = driver.execute_script(js_script)
    print(f"Script injection result: {result}")



# Modify record_action function to store actions in a structured format
def record_action(action_type, element, value=None):
    xpath = get_xpath(element)
    if action_type == 'input':
        recorded_actions.append({'type': 'input', 'xpath': xpath, 'value': value})
    else:
        recorded_actions.append({'type': action_type, 'xpath': xpath})


# Loop to continuously check for user inactivity
def start_recording():
    global driver, actions, start_time, last_time
    url = url_entry.get()
    driver = webdriver.Chrome()
    driver.get(url)
    actions = ActionChains(driver)
    set_up_listeners()
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

# Function to format recorded actions for GPT-4
def format_actions_for_gpt4():
    descriptions = []
    #print(f"\n\n format_actions_for_gpt4 : {recorded_actions} \n\n")
    for action in recorded_actions:
        if action['type'] == 'click':
            descriptions.append(f'click xpath="{action["xpath"]}"')
        elif action['type'] == 'input':
            descriptions.append(f'input xpath="{action["xpath"]}" with the value "{action["value"]}"')
        # Add other action types as needed
    return ", ".join(descriptions)

# Modify stop_and_show_records to call GPT-4 script
def stop_and_show_records():
    gpt_input = ""
    global driver, last_time, paused_time_total
    if driver:
        recorded_events = driver.execute_script("return window.recordedEvents || [];")
        print(f"Recorded events: {recorded_events}\n\n\n")

        last_time = start_time
        prev_event_was_input = False
        combined_input = None
        combined_xpath = None
        for event in recorded_events:
            event_type, xpath, timestamp, *others = event

            # Print wait only if previous event wasn't input or current event is not input
            if not prev_event_was_input or event_type != "input":
                wait_time = abs(math.ceil((timestamp - last_time - paused_time_total) / 1000.0)) * 1000
                paused_time_total=0
                #print(f'<wait time="{wait_time}"></wait>')
                gpt_input += f"wait : time={wait_time}, "

            if event_type == "click":
                #print(f'<{event_type} xpath="{xpath}"></{event_type}>')
                gpt_input += f"click : xpath={xpath}, "
                prev_event_was_input = False
                if combined_input:
                    #print(f'<input xpath="{combined_xpath}" value="{combined_input}"></input>')
                    gpt_input += f"input : xpath={combined_xpath} and value={combined_input}, "
                    combined_input = None
                    combined_xpath = None
            elif event_type == "input":
                char = others[0]
                if prev_event_was_input and xpath == combined_xpath:
                    combined_input += char
                else:
                    if combined_input:
                        pass
                        #print(f'input : xpath="{combined_xpath}" value="{combined_input}" ')
                        #print(f"input : {combined_xpath}, {combined_input}")
                        gpt_input += f"input : xpath={xpath} value={combined_input}"
                    combined_input = char
                    combined_xpath = xpath
                prev_event_was_input = True
            elif event_type == "getText":
                #print(f'<getText xpath="{xpath}"></getText>')
                gpt_input += f"get text xpath={xpath}"
                pass

            last_time = timestamp
        # Print any remaining combined input after loop ends
        if combined_input:
            #print(f'input : xpath="{combined_xpath}" value="{combined_input}" ')
            pass

        driver.quit()
    
    # Call GPT-4 script with formatted actions
    formatted_actions = format_actions_for_gpt4()
    get_PAF_code(gpt_input)
    

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
    print("\n\n\n The PAF code equavalent is : \n\n")
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
            
              The activity can be named anything. Simply replace the 'activity_name' in the id attribute 
              with an appropriate name which describes what the activity is doing.
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
              Where the time attribute is the time in ms.

              To wait till the page has loaded :
              <WaitForPageLoad/>

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

# Start the tkinter main loop
if __name__ == "__main__":
    root.mainloop()
