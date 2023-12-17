import subprocess
import os
import time
import glob
import webbrowser



def run_file():
    # Change to the directory of your Java project
    project_path = r"C:/Users/u1138322/PAF/ProjectContainer/SampleProject"
    os.chdir(project_path)

    # Set environment variables
    java_home = r'C:/Users/u1138322/PAF/jdk-9.0.4'  # Use a raw string for Windows path
    os.environ['JAVA_HOME'] = java_home
    os.environ['CLASSPATH'] = ';'.join([os.environ.get('CLASSPATH', ''), './bin', 'C:/Users/u1138322/PAF/PAF-Framework/lib/*'])

    # Define the full path to the java executable
    java_executable = os.path.join(java_home, 'bin', 'java')

    # Define the Java command to run your project
    java_command = f'{java_executable} com.tr.boot.TestRobot'

    time.sleep(2)
    # Run the command
    process = subprocess.Popen(java_command, shell=True)
    process.wait()

    # Return a message indicating completion
    return 1




def report_open():
    # List all files in the directory
    files = glob.glob(os.path.join("C:/Users/u1138322/PAF/ProjectContainer/SampleProject/report/summary_report", '*.html'))
    if not files:
        print("No HTML files found in the directory.")
        return

    # Find the most recently created HTML file
    most_recent_file = max(files, key=os.path.getctime)

    # Open the most recently created HTML file in Microsoft Edge
    edge_path = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"  # Path to Microsoft Edge
    webbrowser.register('edge', None, webbrowser.BackgroundBrowser(edge_path))
    webbrowser.get('edge').open_new_tab(most_recent_file)

    print(f"Opened the most recently created HTML file: {most_recent_file}")

