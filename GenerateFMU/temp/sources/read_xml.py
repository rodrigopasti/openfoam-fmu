'''
Created on 11/05/2025

@authors: Rodrigo Pasti 
'''

from typing import Optional, Tuple
import xml.etree.ElementTree as ET
from dataclasses import dataclass

@dataclass
class Parametro:
    name: str
    vr: int
    value: float = 0.0

    def __repr__(self):
        return f"{self.name} (VR: {self.vr}, Valor: {self.value})"

@dataclass
class ParametrosMalha:
    elapsedTime: Optional[Parametro] = None
    time_interval_cosim: Optional[Parametro] = None
    wind_velocity: Optional[Parametro] = None
    domainExpansionXY: Optional[Parametro] = None
    domainExpansionZ: Optional[Parametro] = None
    paddingDomain: Optional[Parametro] = None
    cells: Optional[Parametro] = None
    refinementBox: Optional[Parametro] = None
    refinementSurface1: Optional[Parametro] = None
    refinementSurface2: Optional[Parametro] = None
    surfaceLayers: Optional[Parametro] = None
    eMeshLevel: Optional[Parametro] = None
    externalTemperature: Optional[Parametro] = None
    floorTemperature: Optional[Parametro] = None
    projectionDistance: Optional[Parametro] = None
    simulation_interval: Optional[Parametro] = None
    simulation_endTime: Optional[Parametro] = None
    simulation_deltat: Optional[Parametro] = None

class ReadXML:
    def __init__(self):
        '''
        
        '''

    def get_domus_vars(self):
        '''
        #Obter os nomes de zonas e objetos vindos do XML da FMU. A ordem deve coincidir com o XML
        '''

        # dataclasse de parametros de simulação
        params = ParametrosMalha()

        tree = ET.parse('../../modelDescription.xml')
        root = tree.getroot()
        #print(root)
        list_objects_external_temp_surface = []
        list_objects_heat_rejection = []
        list_objects_bc_external_temp = []
        list_objects_conv_coeff = []
        for child in root.iter("ModelVariables"):
            for child2 in child:
                if "External surface temperature(oC)" in child2.attrib["description"]:
                    list_objects_external_temp_surface.append((child2.attrib["name"],int(child2.attrib["valueReference"])))
                elif "Zone heat rejection" in child2.attrib["description"]:
                    list_objects_heat_rejection.append((child2.attrib["name"],int(child2.attrib["valueReference"])))
                elif "Boundary condition external temperature(oC)" in child2.attrib["description"]:
                    list_objects_bc_external_temp.append((child2.attrib["name"],int(child2.attrib["valueReference"])))
                elif "External convention coefficient(W/m2K)" in child2.attrib["description"]:
                    list_objects_conv_coeff.append((child2.attrib["name"],int(child2.attrib["valueReference"])))
                elif "time_interval_cosim" in child2.attrib["description"]:
                    params.time_interval_cosim = Parametro(child2.attrib["name"],int(child2.attrib["valueReference"]))
                elif "Elapsed Time" in child2.attrib["name"]:
                    params.elapsedTime = Parametro(child2.attrib["name"],int(child2.attrib["valueReference"]))
                elif "Weather wind speed" in child2.attrib["name"]:
                    params.wind_velocity = Parametro(child2.attrib["name"],int(child2.attrib["valueReference"]))
                elif "domainExpansionXY" in child2.attrib["description"]:
                    params.domainExpansionXY = Parametro(child2.attrib["name"],int(child2.attrib["valueReference"]))
                elif "domainExpansionZ" in child2.attrib["description"]:
                    params.domainExpansionZ = Parametro(child2.attrib["name"],int(child2.attrib["valueReference"]))
                elif "paddingDomain" in child2.attrib["description"]:
                    params.paddingDomain = Parametro(child2.attrib["name"],int(child2.attrib["valueReference"]))
                elif "cells" in child2.attrib["description"]:
                    params.cells = Parametro(child2.attrib["name"],int(child2.attrib["valueReference"]))
                elif "refinementBox" in child2.attrib["description"]:
                    params.refinementBox = Parametro(child2.attrib["name"],int(child2.attrib["valueReference"]))
                elif "refinementSurface1" in child2.attrib["description"]:
                    params.refinementSurface1 = Parametro(child2.attrib["name"],int(child2.attrib["valueReference"]))
                elif "refinementSurface2" in child2.attrib["description"]:
                    params.refinementSurface2 = Parametro(child2.attrib["name"],int(child2.attrib["valueReference"]))
                elif "surfaceLayers" in child2.attrib["description"]:
                    params.surfaceLayers = Parametro(child2.attrib["name"],int(child2.attrib["valueReference"]))
                elif "eMeshLevel" in child2.attrib["description"]:
                    params.eMeshLevel = Parametro(child2.attrib["name"],int(child2.attrib["valueReference"]))
                elif "External temperature" in child2.attrib["description"]:
                    params.externalTemperature = Parametro(child2.attrib["name"],int(child2.attrib["valueReference"]))
                elif "floorTemperature" in child2.attrib["description"]:
                    params.floorTemperature = Parametro(child2.attrib["name"],int(child2.attrib["valueReference"]))
                elif "projectionDistance" in child2.attrib["description"]:
                    params.projectionDistance = Parametro(child2.attrib["name"],int(child2.attrib["valueReference"]))
                elif "simulation_interval" in child2.attrib["description"]:
                    params.simulation_interval = Parametro(child2.attrib["name"],int(child2.attrib["valueReference"]))
                elif "simulation_endTime" in child2.attrib["description"]:
                    params.simulation_endTime = Parametro(child2.attrib["name"],int(child2.attrib["valueReference"]))    
                elif "simulation_deltat" in child2.attrib["description"]:
                    params.simulation_deltat = Parametro(child2.attrib["name"],int(child2.attrib["valueReference"]))                                                    

        return list_objects_external_temp_surface, list_objects_heat_rejection, list_objects_bc_external_temp, list_objects_conv_coeff, params