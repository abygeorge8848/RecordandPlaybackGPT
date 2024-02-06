import subprocess
import os
import time
import glob
import webbrowser
from set_paths import project_path, lib_path, java_home, edge_path, dependencies, refresh_class_path


def run_file():
    project_name = project_path.split("/")[-1]
    print(f"The project name is : {project_name}")
    # Run the refreshClassPath batch file with the project name as input
    process = subprocess.Popen(['cmd.exe', '/c', refresh_class_path], stdin=subprocess.PIPE, text=True)
    process.stdin.write(project_name + '\n')
    process.stdin.close()
    result = process.wait()
    if result != 0:
        print("Failed to run refreshClassPath batch file.")
        return

    # Change to the directory of your Java project
    os.chdir(project_path)

    # Set environment variables
    os.environ['JAVA_HOME'] = java_home
    classpath_entries = [os.environ.get('CLASSPATH', ''), './bin', lib_path] + dependencies
    os.environ['CLASSPATH'] = ';'.join(classpath_entries)

    # Define the full path to the java executable
    java_executable = os.path.join(java_home, 'bin', 'java')
    # Define the Java command to run your project
    java_command = f'{java_executable} com.tr.boot.TestRobot'
    time.sleep(2)
    # Run the command
    process = subprocess.Popen(java_command, shell=True)
    process.wait()
    return 1


def report_open():
    # List all files in the directory
    summary_report_path = project_path + '/report/summary_report'
    files = glob.glob(os.path.join(summary_report_path, '*.html'))
    if not files:
        print("No HTML files found in the directory.")
        return

    # Find the most recently created HTML file
    most_recent_file = max(files, key=os.path.getctime)

    # Open the most recently created HTML file in Microsoft Edge
    webbrowser.register('edge', None, webbrowser.BackgroundBrowser(edge_path))
    webbrowser.get('edge').open_new_tab(most_recent_file)

    print(f"Opened the most recently created HTML file: {most_recent_file}")

