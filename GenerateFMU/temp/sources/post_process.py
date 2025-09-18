'''
Created on 15/11/2024

@authors: Rodrigo Pasti / Micaell
'''


import os


class PostProcessData:
    def __init__(self, dir_path):

        self.dir_path = str(dir_path)
        self.global_array_T = []
        self.dict_T = {}
        self.array_hct = []
        self.array_hct_patch = []
        self.T_searcher()

    def mean_T(self, file_path):
        # Opening files
        with open(file_path, 'r') as file:
            lines = file.readlines()

        for i, line in enumerate(lines):
            # Start reading from '# Time' to ensure it reads the lines and columns the right way
            if '# Time' in line:
                data_startpoint = i + 1
                break
        else:
            print(f"Cannot find '# Time' at: {file_path}")
            return None
                 
        #data = np.genfromtxt(lines[data_startpoint:], delimiter=None, comments='#')
                
        data = []
        for line in lines[data_startpoint:]:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()  # splits by whitespace
            numbers = [float(p) for p in parts]
            data.append(numbers)

        last_line_data = data[-1]
        print("DATA <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        print(file_path)
        print(data)
        print(last_line_data)
        mean_value = 0
        n_values = 0
        for i in range(1, len(last_line_data)):
            if last_line_data[i] > 0.01:
                mean_value = mean_value + last_line_data[i]
                n_values = n_values + 1
        
        if n_values==0:
            mean_value = 0
        else:
            mean_value = mean_value/n_values
     
        return mean_value

       

    def T_searcher(self):
        for root, dirs, files in os.walk(self.dir_path):
            for file_name in files:
                # Search for files that start with 'T'
                if file_name.startswith("T"):
                    file_path_T = os.path.join(root, file_name)
                    zone = root.replace("\\","/").split("/")[-2]
                    t_mean = self.mean_T(file_path_T)
                    if t_mean is not None:
                        self.global_array_T.append(t_mean)
                        self.dict_T[zone.replace("sample_near_","")] = float(t_mean) #Converte de numpy.float64 para float
                        
    
   
    def extract_htc(self, filename):
        try:
            bigger_it = 0
            # Walk through the directory and subdirectories to find thc
            for root, dirs, files in os.walk(self.dir_path):
                for file_name in files:
                    if file_name.startswith("wall"):
                        value = float(root.replace("\\","/").split("/")[-1])
                        if value < bigger_it:
                            continue
                        bigger_it = value
                        file_path = os.path.join(root, file_name)
            print("FLE PATH IN HTC")
            print(file_path)
            with open(file_path, "r") as f:
                lines = f.readlines()

            # If no line starting with "# Time" is found, raise an error
            start_index = None
            for i, line in enumerate(lines):
                if line.startswith("# Time"):
                    start_index = i
                    break

            if start_index is None:
                raise ValueError(f"Cannot find '# Time' in: {file_path}")
           
            self.dict_hct = {}
            for i in range(start_index + 1, len(lines)):
                splited_data = lines[i].split()
                self.dict_hct[splited_data[1]] = float(splited_data[-1])               

        except FileNotFoundError:
            print("File not found:", filename)
        except ValueError as e:
            print("Error processing file:", filename, ":", e)

   
'''
# Example usage
#file_dir = "C:\\Users\\franc\\workspace\\1_buildings_with_only_fluid_domain_25_10_2024\\postProcessing\\"
file_dir = "/mnt/c/Users/franc/workspace/1_buildings_with_only_fluid_domain_25_10_2024/postProcessing/"
#file_dir = "/mnt/c/Users/franc/workspace/datasets/postProcessing/"
post_process_data = PostProcessData(file_dir)
post_process_data.T_searcher()

list_zones_objects = ["cobertura_7-Zona_10", "cobertura_7-Zona_11"]

print(post_process_data.dict_T)
'''
'''
outputReal = []
outputRealVR = []
i = 0 
for domus_obj in list_zones_objects:
    outputReal.append(post_process_data.dict_T[domus_obj])
    outputRealVR.append(i)
    i = i + 1
outputReal = tuple(outputReal)
outputRealVR = tuple(outputRealVR)
print(outputReal)
print(outputRealVR)


# Extract the second column of strings
#post_process_data.extract_patch_column("wallHeatTransferCoeff.dat")
post_process_data.extract_htc("wallHeatTransferCoeff.dat")
#post_process_data.hct_dict()
print(post_process_data.dict_hct)

#print(global_generator.global_array_T)
#print(global_generator.dict_T)
# Check extracted data
#print("\narray_hct_patch:", global_generator.array_hct_patch[0])
#print("\nArray check:", global_generator.array_hct[0])

'''