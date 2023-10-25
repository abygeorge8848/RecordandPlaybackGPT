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

nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

recorded_actions = []

patterns = [
    [{"LEMMA": {"IN": ["get", "extract", "fetch", "retrieve"]}}, 
     {"OP": "*"},  # This will match 0 or more tokens in between
     {"LOWER": {"IN": ["text", "value", "content"]}}],
]

matcher.add("GET_TEXT", patterns)

# Start Chrome
chrome_options = Options()
chrome_options.add_argument("--disable-web-security")  # THIS IS UNSAFE FOR REGULAR BROWSING
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

paused_time_total= 0
paused_at = None

instruction_frame = None
instruction_entry = None

driver = webdriver.Chrome(options=chrome_options)
actions = ActionChains(driver)


def process_instruction():
    instruction = instruction_entry.get()
    doc = nlp(instruction)
    
    print("Instruction:", instruction)
    print("Tokens:", [token.text for token in doc])
    print("Lemmas:", [token.lemma_ for token in doc])
    # Find matches in the doc
    matches = matcher(doc)
    print(f"The match result is : {matches}")
    # If there's a match, it indicates the user wants to retrieve text
    if matches:
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


def fetch_text_instruction():
    xpath = driver.execute_script("return window.clickedElementXPath || '';")
    if xpath:
        print(f'<getText xpath="{xpath}"></getText>')
        driver.execute_script(f"window.recordedEvents.push(['getText', '{xpath}', Date.now()]);")
        # Reset after processing
        driver.execute_script("window.clickedElementXPath = null;")
    else:
        messagebox.showwarning("Action Recorder", "No element selected. Please try again.")



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


def hide_instruction_entry():
    global instruction_frame
    if instruction_frame:
        instruction_frame.destroy()


def get_xpath(element):
    # A simple way to get xpath, might need refining
    return driver.execute_script("""
        function getElementXPath(element) {
            if (element && element.id) 
                return 'id("' + element.id + '")';
            else 
                return driver.execute_script('xpath', 'ancestor-or-self::*', element);
        }
        return getElementXPath(arguments[0]);
    """, element)


def record_action(action_type, element, value=None):
    xpath = get_xpath(element)
    if action_type == 'input':
        recorded_actions.append(f'<input xpath="{xpath}" value="{value}"></input>')
    else:
        recorded_actions.append(f'{action_type} : {xpath}')


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

def stop_and_show_records():
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
                print(f'<wait time="{wait_time}"></wait>')

            if event_type == "click":
                print(f'<{event_type} xpath="{xpath}"></{event_type}>')
                prev_event_was_input = False
                if combined_input:
                    print(f'<input xpath="{combined_xpath}" value="{combined_input}"></input>')
                    combined_input = None
                    combined_xpath = None
            elif event_type == "input":
                char = others[0]
                if prev_event_was_input and xpath == combined_xpath:
                    combined_input += char
                else:
                    if combined_input:
                        print(f'<input xpath="{combined_xpath}" value="{combined_input}"></input>')
                        # print(f"input : {combined_xpath}, {combined_input}")
                    combined_input = char
                    combined_xpath = xpath
                prev_event_was_input = True
            elif event_type == "getText":
                print(f'<getText xpath="{xpath}"></getText>')

            last_time = timestamp
        # Print any remaining combined input after loop ends
        if combined_input:
            print(f'<input xpath="{combined_xpath}" value="{combined_input}"></input>')

        driver.quit()

def get_recorded_events():
    # Retrieve the events from JavaScript side
    return driver.execute_script("return window.recordedEvents || [];")

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

# If you want to show the instructions on startup, call this:
# show_instruction_entry()

root.mainloop()