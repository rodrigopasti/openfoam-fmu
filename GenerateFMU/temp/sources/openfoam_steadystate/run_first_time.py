# Main script to get the Domus geometry, export the STL and eMesh files
import subprocess
import os
import glob

def limpar_crlf_shell_scripts(diretorio="."):
    for nome in os.listdir(diretorio):
        caminho = os.path.join(diretorio, nome)
        if os.path.isfile(caminho) and '.' not in nome:
            try:
                with open(caminho, 'r', encoding='utf-8') as f:
                    primeira_linha = f.readline()
                if primeira_linha.startswith("#!"):  
                    with open(caminho, 'r', encoding='utf-8') as f:
                        conteudo = f.read()
                    conteudo = conteudo.replace('\r\n', '\n')
                    with open(caminho, 'w', encoding='utf-8') as f:
                        f.write(conteudo)
            except UnicodeDecodeError:
                # Ignora arquivos binários
                continue

# Define file name
# case_file = "Canyon_correto_com_ar_condicionado" #generated from Domus


# Define paths for Linux
# blender_executable = "/snap/bin/blender"


# blend_file = "/mnt/c/Users/franc/workspace/1_buildings_with_only_fluid_domain_25_10_2024/domusBlender_REV02_wip.blend"
# #python_script = "/home/luciano/Modelos/Blender/read_IDF_extract_STL.py"
# python_script = "/mnt/c/Users/franc/workspace/1_buildings_with_only_fluid_domain_25_10_2024/read_IDF_extract_STL.py"
# idf_file = f"/mnt/c/Users/franc/workspace/1_buildings_with_only_fluid_domain_25_10_2024/{case_file}.idf"
# stl_file = "/mnt/c/Users/franc/workspace/1_buildings_with_only_fluid_domain_25_10_2024/constant/triSurface/"
# print("Normalize the STL file path")
# # Normalize the STL file path
# stl_file = os.path.normpath(stl_file)
print("limpar_crlf_shell_scripts")
# Removes Windows-style carriage returns (\r) from all files ensuring Unix compatibility.
limpar_crlf_shell_scripts()

# Step 1: Remove existing STL and eMesh files
'''
file_extensions = ["*.stl", "*.eMesh"]
for extension in file_extensions:
    files_to_remove = glob.glob(os.path.join(stl_file, extension))
    for file in files_to_remove:
        try:
            os.remove(file)
            print(f"Deleted existing file: {file}")
        except OSError as e:
            print(f"Error deleting file {file}: {e}")
'''
# print("Run Blender with the necessary arguments")
# # Step 2: Run Blender with the necessary arguments
# command = [
#     blender_executable,
#     "--background",  # Run in background mode
#     blend_file,      # Open the .blend file
#     "--python", python_script,
#     "--",            # Custom arguments start here
#     idf_file,        # Path to IDF file
#     stl_file         # Path to export STL files
# ]
# print("Execute Blender script")
# try:
#     process = subprocess.Popen(command)
#     process.wait()
#     if process.returncode == 0:
#         print("Blender script executed successfully.")
#     else:
#         print(f"Blender script exited with return code {process.returncode}")
# except subprocess.CalledProcessError as e:
#     print(f"An error occurred while running Blender: {e}")
# except Exception as e:
#     print(f"An unexpected error occurred: {e}")

# Step 3: Run OpenFOAM setup
try:
    print("Running OpenFOAM meshAndRun...")
    process = subprocess.Popen(["./meshAndRun"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        print("meshAndRun executed successfully.")
        print(stdout)
    else:
        print(f"meshAndRun exited with return code {process.returncode}")
        print(stderr)
        print(stdout)        
except subprocess.CalledProcessError as e:
    print(f"An error occurred while running meshAndRun: {e}")
    print(stdout)    
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    print(stdout)    
