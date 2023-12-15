import subprocess
import os
import time



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
