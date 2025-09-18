import subprocess
import os
import glob

# First run with Mesh and OpenFOAM setup files 
try:
    print("Running OpenFOAM...")
    process = subprocess.Popen(["./run"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        print("run executed successfully.")
        print(stdout)  # Display the output from run
    else:
        print(f"run script exited with return code {process.returncode}")
        print(stderr)  # Display the error output from run
        print(stdout)        
except subprocess.CalledProcessError as e:
    print(f"An error occurred while running run: {e}")
    print(stdout)    
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    print(stdout)