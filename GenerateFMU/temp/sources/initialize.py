'''
OpenFOAM Domus FMU - Initialize
Created on 15/11/2024

@authors: Rodrigo Pasti (FMU OpenFOAM) / Walter Mazuroski (FMU Model)
'''

from dataclasses import fields
from post_process import PostProcessData
import json
import time
from wsl_docker_runner import start_dockerd, import_container, start_and_run_script_in_container, create_runtime_container
from read_xml import Parametro, ReadXML
from pathlib import Path
from vr_utils import VRResolver
import shutil
import os
import csv

# define enum to retrive value and vr from dictionaries
_value = 0
_vr = 1

realOutSize = 104
intOutSize = 0
boolOutSize = 0
strOutSize = 0
outputReal = tuple()
outputRealVR = tuple()

#you can use this function to call inputs by defined value reference(VR)

def copy_dir(origem, destino):
    # Cria o diretório de destino se não existir
    os.makedirs(destino, exist_ok=True)

    # Itera sobre todos os itens do diretório de origem
    for item in os.listdir(origem):
        caminho_origem = os.path.join(origem, item)
        caminho_destino = os.path.join(destino, item)

        # Copia arquivos e diretórios recursivamente
        if os.path.isdir(caminho_origem):
            shutil.copytree(caminho_origem, caminho_destino, dirs_exist_ok=True)
        else:
            shutil.copy2(caminho_origem, caminho_destino)


def criar_arquivo_parametros(nome_arquivo, params):
	nome_arquivo = nome_arquivo / "simu.py"
	conteudo = f"""# Domain - times greater than the highest building
domainExpansionXY = {params.domainExpansionXY.value}
domainExpansionZ = {params.domainExpansionZ.value}
paddingDomain = {params.paddingDomain.value}

# Mesh 
cells = {int(params.cells.value)}
refinementBox = {int(params.refinementBox.value)}
refinementSurface1 = {int(params.refinementSurface1.value)}
refinementSurface2 = {int(params.refinementSurface2.value)}
surfaceLayers = {int(params.surfaceLayers.value)}
eMeshLevel = {int(params.eMeshLevel.value)}

# Velocity - from Domus
velo = [{params.wind_velocity.value}, 0, 0]

# Weather Temperature
T = {params.externalTemperature.value + 273.15}

# Wall temperature
Tw = 292.15

# Floor temperature
Tf = {params.floorTemperature.value}

# Demand power for heating from Domus - air conditionning system 
# Including the power at gradient 'gradient        uniform <value>;'
rejectedHeat = 122.0 # [W/m2]

# Sensors - distance from the wall
projectionDistance = {params.projectionDistance.value} #[m]

# Simulation
interval = {int(params.simulation_interval.value)}
endTime = {params.simulation_endTime.value}
deltat = {params.simulation_deltat.value}

"""
	with open(nome_arquivo, "w") as arquivo:
		arquivo.write(conteudo)
	print(f"Arquivo '{nome_arquivo}' criado com sucesso.")


#if you want variables available in the 'state', you must declare then as `global`

def main():
	'''
	Variáveis da FMU
	realArray -> entrada de números reais

	Saídas e suas referências:
	- outputReal,outputRealVR
	- outputInt,outputIntVR
	- outputBool,outputBoolVR
	- outputStr,outputStrVR
	
	state: salva tudo do passo anterior (foi testado e parece não funcionar)
	'''
	#Declarando as variáveis de saída para a FMU e Domus
	vr = VRResolver(boolArrayVR, boolArray, intArrayVR, intArray, realArrayVR, realArray, stringArrayVR, stringArray)

	#Path raíz dos arquivos
	print("Input stringArray", stringArray)
	print("Input stringArrayVR", stringArrayVR)

	global root_dir 
	#transient or steadystate
	global idModel
	idModel = vr.get_int_by_vr(0)
	model = 'openfoam_steadystate'
	if idModel == 1:
		model = 'openfoam_transient'
	
	root_dir = Path(__file__).resolve().parent / model
	print("ROOOT PATH <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
	print(root_dir)
	# copy stl files
	stl_files_dir = vr.get_string_by_vr(1)
	copy_dir(stl_files_dir, root_dir / 'constant/triSurface')

	'''
	Capturar parâmetros advindos da FMU, e separá-los em variáveis
	'''
	print("Input realArray")
	print(realArray)
	print("Input realArrayVR")
	print(realArrayVR)

	'''
	Ler os dados vindos do Domus e colocá-los em um dicionário 
	com referências a qual zona e objeto pertencem. 	
	'''
	#Lista de zonas de objetos da zona. A ordem na lista equivale à definição no XML da FMU
	#Essa lista é usada como referência na entrada de dados e saída de dados para o Domus
	read_xml = ReadXML()	
	global list_objects_external_temp_surface, list_objects_heat_rejection, list_objects_bc_external_temp, list_objects_conv_coeff, params
	list_objects_external_temp_surface, list_objects_heat_rejection, list_objects_bc_external_temp, list_objects_conv_coeff, params = read_xml.get_domus_vars()

	#Atribuição aos dicionário de temperatura com conversão para graus Kelvin
	dict_input_temperature_surface = {
		obj[_value]: vr.get_real_by_vr(obj[_vr]) + 273.15
		for obj in list_objects_external_temp_surface
	}

	dict_input_heat_rejection = {
		obj[_value]: vr.get_real_by_vr(obj[_vr])
		for obj in list_objects_heat_rejection
	}

	# Atualiza params com valores vindos do Domus
	for field in fields(params):
		nome = field.name
		parametro: Parametro = getattr(params, nome)

		if parametro is None:
			print(f"{nome} ainda não foi inicializado. Pulando...")
			continue

		novo_valor = vr.get_real_by_vr(parametro.vr)
		if novo_valor is not None:
			novo_parametro = Parametro(parametro.name, parametro.vr, novo_valor)
			setattr(params, field.name, novo_parametro)

	print("dict_input_temperature_surface")
	print(dict_input_temperature_surface)
	print("dict_input_heat_rejection")
	print(dict_input_heat_rejection)
	print(params)

	'''
	Salvar arquivo contendo dados de temperatura das paredes
	'''	
	with open(root_dir / "dict_input_temperature_surface.json", "w") as outfile:
		json.dump(dict_input_temperature_surface, outfile)

	'''
	Salvar arquivo contendo dados de calor rejeitado
	'''	
	with open(root_dir / "dict_input_heat_rejection.json", "w") as outfile:
		json.dump(dict_input_heat_rejection, outfile)


	'''
	salva arquivo simu.py, de parametrizações
	'''
	criar_arquivo_parametros(root_dir, params)
		
	
	'''
	Rodar o OpenFOAM (first time run)
	'''
	
	'''
	Somente roda OpenFOAM se estiver no time step escolhido
	'''
	container_image = vr.get_string_by_vr(3)
	global distro 
	distro = "Ubuntu-Minimal"
	global container_name 
	container_name = "openfoam-fmu"
	global pid
	#pid = start_dockerd(distro)
	#import_container(distro, container_image)
	
	print("Running OpenFOAM...")
	initial_time = time.time()
	root_dir_static = "C:/openfoam-fmu/zona1parede2/data/sources/openfoam_steadystate/"
	container = vr.get_string_by_vr(3)
	dir_OF_proj = "openfoam_steadystate"


	cmd = ["docker", "run", "--user", "1000:1000" ,"-v", 
	root_dir_static + ":/"+ dir_OF_proj +"/", 
	"-w","/" + dir_OF_proj + "/",
	container, "python3", "run_first_time.py"]

	#cmd = ["docker", "run", "-v", 
	#root_dir_static + ":/"+ root_dir_static +"/", 
	#"-w","/" + root_dir_static + "/",
	#container, "python3", "run_second_time.py"]
	import subprocess
	p = subprocess.run(cmd, capture_output=True)
	
	#create_runtime_container(distro, container_name, container_image, root_dir, pid)
	#start_and_run_script_in_container(distro, container_name, "run_first_time.py", root_dir.name, pid)
	print("Time to OpenFOAM simulation: " + str(time.time()-initial_time))
	print("Process return")
	print("End of OpenFOAM")

		
	
	'''
	Pegar os resultados do OpenFOAM contidos nos arquivos de saída
	'''
	file_dir = root_dir / "postProcessing/" 
	#file_dir = root_dir + "/postProcessing/" 
	print("FILE DIR...............")
	print(file_dir)
	post_process_data = PostProcessData(file_dir)
	post_process_data.T_searcher()
	post_process_data.extract_htc("wallHeatTransferCoeff.dat")
	print("post_process_data.dict_T")
	print(post_process_data.dict_T)
	print("Coeficiente de transferência de calor")
	print(post_process_data.dict_hct)
	'''
	Atribuir os valores do OpenFOAM nas variáveis de saída da FMU para o Domus
	'''

	'''
	Atribuição da temperatura com conversão para graus celsius
	'''
	outputReal_list = []
	outputRealVR_list = []
	for domus_obj in list_objects_bc_external_temp:
		#outputReal_list.append(post_process_data.dict_T[domus_obj[_value]] - 273.15)
		outputReal_list.append(280 - 273.15)
		outputRealVR_list.append(domus_obj[_vr])

		
	'''
	Atribuição do coeficiente de transferência de calor
	'''
	# for domus_obj in list_objects_conv_coeff:
	# 	outputReal_list.append(post_process_data.dict_hct[domus_obj[_value]])
	# 	outputRealVR_list.append(domus_obj[_vr])


	'''
	Salva os resultados no diretório de saída
	'''
	file_path_csv = vr.get_string_by_vr(2) #Para salvar resultados
	file_name_csv = "dict_input_temperature_surface.csv"
	write_csv(file_path_csv, file_name_csv, dict_input_temperature_surface)

	file_name_csv = "dict_input_heat_rejection.csv"
	write_csv(file_path_csv, file_name_csv, dict_input_heat_rejection)

	file_name_csv = "dict_output_temperature.csv"
	write_csv(file_path_csv, file_name_csv, post_process_data.dict_T)

	file_name_csv = "dict_output_htc.csv"
	write_csv(file_path_csv, file_name_csv, post_process_data.dict_hct)


	global outputReal
	global outputRealVR
	global realOutSize
	outputReal = tuple(outputReal_list)
	outputRealVR = tuple(outputRealVR_list)
	realOutSize = len(outputReal_list)
	print("Output outputReal")
	#print(outputReal)
	print("outputRealVR")
	#print(outputRealVR)

	print("End of FMU initialize")

def write_csv(file_path_csv, file_name_csv, dataset):
	import os
	file_exists = os.path.isfile(file_path_csv+file_name_csv)
	with open(file_path_csv+file_name_csv, mode='w', newline='', encoding='utf-8') as file:
		writer = csv.DictWriter(file, fieldnames=dataset.keys())
		if not file_exists:
			writer.writeheader()		
		writer.writerow(dataset)    
	
# defining input variables
def SetReal(value, vr):
	global realArray
	global realArrayVR
	realArray = list(value)
	realArrayVR = list(vr)
	
def SetInteger(value, vr):
	global intArray
	global intArrayVR
	intArray = list(value)
	intArrayVR = list(vr)	

def SetBoolean(value, vr):
	global boolArray
	global boolArrayVR
	boolArray = list(value)
	boolArrayVR = list(vr)	
	
def SetString(value, vr):
	global stringArray
	global stringArrayVR
	stringArray = list(value)
	stringArrayVR = list(vr)


# defining output variables
def GetReal():
	if realOutSize > 0:
		return (outputReal,outputRealVR)
	else:
		return 0
	
def GetInteger():
	if intOutSize > 0:
		return (outputInt,outputIntVR)
	else:
		return 0
		
def GetBoolean():
	if boolOutSize > 0:
		return (outputBool,outputBoolVR)
	else:
		return 0
		
def GetString():
	if strOutSize > 0:
		return (outputStr,outputStrVR)
	else:
		return 0