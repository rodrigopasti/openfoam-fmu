'''
OpenFOAM Domus FMU - Event Update
Created on 15/11/2024

@authors: Rodrigo Pasti (FMU OpenFOAM) / Walter Mazuroski (FMU Model)
'''
from dataclasses import fields
from post_process import PostProcessData
from read_xml import Parametro, ReadXML
import json
import time
import csv
from pathlib import Path
from vr_utils import VRResolver
from wsl_docker_runner import  start_and_run_script_in_container

# define enum to retrive value and vr from dictionaries
_name = 0
_vr = 1

realOutSize = 0
intOutSize = 0
boolOutSize = 0
strOutSize = 0
outputReal = tuple()
outputRealVR = tuple()

def main(state):
	'''
	Variáveis da FMU
	realArray -> entrada de números reais

	Saídas e suas referências:
	- outputReal,outputRealVR
	- outputInt,outputIntVR
	- outputBool,outputBoolVR
	- outputStr,outputStrVR

	'''

	# Atualiza params com valores vindos do Domus
	vr = VRResolver(boolArrayVR, boolArray, intArrayVR, intArray, realArrayVR, realArray, stringArrayVR, stringArray)	
	for field in fields(state.params):
		nome = field.name
		parametro: Parametro = getattr(state.params, nome)

		if parametro is None:
			print(f"{nome} ainda não foi inicializado. Pulando...")
			continue

		novo_valor = vr.get_real_by_vr(parametro.vr)
		if novo_valor is not None:
			novo_parametro = Parametro(parametro.name, parametro.vr, novo_valor)
			setattr(state.params, field.name, novo_parametro)				

	time_step = state.params.elapsedTime.value
	time_interval_cosim = state.params.time_interval_cosim.value
	runThisTimeStep = time_step >= time_interval_cosim and time_step % time_interval_cosim == 0

	'''
	Somente roda OpenFOAM se estiver no time step escolhido
	'''
	if runThisTimeStep == False:
		print(f"Current time-step: {time_step}")
		print("########## Interval in which the OpenFOAM will not run ##########")
	else:

		#Path raíz dos arquivos
		#Linux path
		#root_dir = "/mnt/c/Users/franc/workspace/1_buildings_with_only_fluid_domain_25_10_2024/"
		#WIndows path
		root_dir = state.root_dir
		file_path_csv = vr.get_string_by_vr(2) #Para salvar resultados

		'''
		Capturar parâmetros advindos da FMU, e separá-los em variáveis
		'''
		print("\n########## Input Information ##########")
		print("Input realArray")
		print(realArray)
		print("Input realArrayVR")
		print(realArrayVR)

		#Atribuição aos dicionário de temperatura com conversão para graus Kelvin
		dict_input_temperature_surface = {
			obj[_name]: vr.get_real_by_vr(obj[_vr]) + 273.15
			for obj in state.list_objects_external_temp_surface
		}

		dict_input_heat_rejection = {
			obj[_name]: vr.get_real_by_vr(obj[_vr])
			for obj in state.list_objects_heat_rejection
		}
		
		print("dict_input_temperature_surface")
		print(dict_input_temperature_surface)
		print("dict_input_heat_rejection")
		print(dict_input_heat_rejection)
		print(state.params)
		
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
		Rodar o OpenFOAM (second time run)
		'''
		
		'''
		Pegar cada entrada no dicionário de referências e salvar nas condições
		de contorno do OpenFOAM
		'''	
		root_dir_static = "C:/openfoam-fmu/zona1parede2/data/sources/openfoam_steadystate/"

		print("\n########## Running OpenFOAM... ##########")
		initial_time = time.time()
		container = vr.get_string_by_vr(3)
		dir_OF_proj = "openfoam_steadystate"

		cmd = ["docker", "run", "--user", "1000:1000", "-v", 
		root_dir_static + ":/"+ dir_OF_proj +"/", 
		"-w","/" + dir_OF_proj + "/",
		container, "python3", "run_second_time.py"]

		import subprocess
		p = subprocess.run(cmd, capture_output=True)
		#start_and_run_script_in_container(state.distro, state.container_name, "run_second_time.py", state.root_dir.name, state.pid)
		print("Time to OpenFOAM simulation: " + str(time.time()-initial_time))
		print("End of OpenFOAM\n")
	
	'''
	Pegar os resultados do OpenFOAM contidos nos arquivos de saída
	'''
	file_dir = state.root_dir / "postProcessing/" 
	#file_dir = root_dir + "/postProcessing/" 
	post_process_data = PostProcessData(file_dir)
	post_process_data.T_searcher()
	post_process_data.extract_htc("wallHeatTransferCoeff.dat")
	
	#if runThisTimeStep:
	print("########## Output Information ##########")
	print("post_process_data.dict_T")
	print(post_process_data.dict_T)
	print("Coeficiente de transferência de calor")
	print(post_process_data.dict_hct)
	
	print("Objetos")
	print(list(post_process_data.dict_T.keys()))
	print("quantidades")
	print(len(list(post_process_data.dict_T.keys())))
	print(state.list_objects_bc_external_temp)
	'''
	Atribuir os valores do OpenFOAM nas variáveis de saída da FMU para o Domus
	'''

	'''
	Atribuição da temperatura com conversão para graus celsius
	'''
	outputReal_list = []
	outputRealVR_list = []
	
	for domus_obj in state.list_objects_bc_external_temp:
		outputReal_list.append(post_process_data.dict_T[domus_obj[_name]] - 273.15)
		outputRealVR_list.append(domus_obj[_vr])

	'''
	Atribuição do coeficiente de transferência de calor
	'''
	for domus_obj in state.list_objects_conv_coeff:		
		outputReal_list.append(post_process_data.dict_hct[domus_obj[_name]])
		outputRealVR_list.append(domus_obj[_vr])

	global outputReal
	global outputRealVR
	global realOutSize	
	outputReal = tuple(outputReal_list)
	outputRealVR = tuple(outputRealVR_list)
	realOutSize = len(outputReal_list)
	
	if runThisTimeStep:
		print("Output outputReal")
		print(outputReal)
		print("Tamanho outputReal")
		print(len(outputReal))
		print("outputRealVR")
		print(outputRealVR)

		print("Tamanho outputRealVR")
		print(len(outputRealVR))
	
		'''
		Salvar dados  e compor base de treinamento de dados para Machine Learning
		'''
		file_name_csv = "dict_input_temperature_surface.csv"
		write_csv(file_path_csv, file_name_csv, dict_input_temperature_surface)

		file_name_csv = "dict_input_heat_rejection.csv"
		write_csv(file_path_csv, file_name_csv, dict_input_heat_rejection)

		file_name_csv = "dict_output_temperature.csv"
		write_csv(file_path_csv, file_name_csv, post_process_data.dict_T)

		file_name_csv = "dict_output_htc.csv"
		write_csv(file_path_csv, file_name_csv, post_process_data.dict_hct)

	print ('End of the event update.')
	

def write_csv(file_path_csv, file_name_csv, dataset):
	import os
	file_exists = os.path.isfile(file_path_csv+file_name_csv)
	with open(file_path_csv+file_name_csv, mode='a', newline='', encoding='utf-8') as file:
		writer = csv.DictWriter(file, fieldnames=dataset.keys())
		if not file_exists:
			writer.writeheader()		
		writer.writerow(dataset)

'''
Funções do padrão da FMU
'''	
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