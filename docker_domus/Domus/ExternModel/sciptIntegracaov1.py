###
### This file is generated automatically by Domus
###
import os
import sys
import salome
import math
import time

salome.salome_init()
theStudy = salome.myStudy

import salome_notebook
notebook = salome_notebook.NoteBook(theStudy)

###
### SMESH component
###

import  SMESH, SALOMEDS
from salome.smesh import smeshBuilder

#Definindo constantes para as coordenadas
X = 0
Y = 1
Z = 2
Epsilon = 1e-6

def GetModulo(coord):
	return math.sqrt((coord[X] * coord[X]) + (coord[Y] * coord[Y]) + (coord[Z] * coord[Z]));

def GetAngle(normal,eixo):
	teta = (math.acos(-normal[eixo] / GetModulo(normal)))
	angle = math.pi - teta
	return angle

def CalculaNormalDaFace(malha,grupoface):
	pontoMalha = malha.GetNodeXYZ(grupoface.GetNodeIDs()[1])
	face = malha.FindElementsByPoint(pontoMalha[X],pontoMalha[Y],pontoMalha[Z], SMESH.FACE, grupoface )
	normal = malha.GetFaceNormal(face[0])
	mag = math.sqrt(sum(normal[i]*normal[i] for i in range(len(normal))))
	unitNormal =  [ normal[i]/mag  for i in range(len(normal)) ]
	return [unitNormal, pontoMalha]


def Rotaciona(ponto, angulo, eixo):
	pontoRotacionado = [0,0,0]
	c = math.cos(angulo);
	s = math.sin(angulo);
	t = 1.0 - c;

	pontoRotacionado[X] = ( (t*eixo[X]*eixo[X] + c)*ponto[X]         + (t*eixo[X]*eixo[Y] - s*eixo[Z])*ponto[Y] + (t*eixo[X]*eixo[Z] + s*eixo[Y])*ponto[Z])
	pontoRotacionado[Y] = ( (t*eixo[X]*eixo[Y] + s*eixo[Z])*ponto[X] + (t*eixo[Y]*eixo[Y] + c)*ponto[Y]         + (t*eixo[Y]*eixo[Z] - s*eixo[X])*ponto[Z])
	pontoRotacionado[Z] = ( (t*eixo[X]*eixo[Z] - s*eixo[Y])*ponto[X] + (t*eixo[Y]*eixo[Z] + s*eixo[X])*ponto[Y] + (t*eixo[Z]*eixo[Z] + c)*ponto[Z])
	return pontoRotacionado

def CalculaAjusteFace(malha,grupoface,x,y,z):
	[unitNormal, pontoMalha] = CalculaNormalDaFace(malha,grupoface)
	v = x-pontoMalha[0],y-pontoMalha[1], z-pontoMalha[2]
	dist = sum(i*j for i,j in zip(v,unitNormal))
	return [unitNormal, dist]

def EncontraManchaFace(grupoface,file):
	#startEM = time.time()
	faces = set()
	#calcula normal da face inclinada
	[normal, pontoMalha] = CalculaNormalDaFace(Malha,grupoface)
	#se for uma face inclinada, rotaciona e projeta
	coplanar = 0
	for i in range(0,3):
		print abs(normal[i])
		if abs(normal[i]) < Epsilon: 
			coplanar = coplanar + 1
		
	#if (normal[X] != 0) and (normal[Y] != 0) and (normal[Z] != 0):
	if coplanar < 2:
		faces = RotateAndProjectFace(file,grupoface)
	else:
		fist = 1
		#faceAux = Malha.CreateEmptyGroup( SMESH.NODE, 'FaceAux' )		
		with open(file) as f:
			for line in f:
				coord = line.split()
				#ajusta ponto importado - pode ser que as faces nao estejam exatamente sobrepostas
				ponto = float("{0:.2f}".format(float(coord[X]))),float("{0:.2f}".format(float(coord[Y]))),float("{0:.2f}".format(float(coord[Z])))
				#faceAux.Add([Malha.AddNode(ponto[X],ponto[Y],ponto[Z])])
				if fist == 1:
					fist = 0
					[unitNormal, dist]= CalculaAjusteFace(Malha,grupoface,ponto[X],ponto[Y],ponto[Z])
				pnew = ponto[X]-unitNormal[X]*dist, ponto[Y]-unitNormal[Y]*dist, ponto[Z]-unitNormal[Z]*dist
				# Find faces at the point
				newFaces = Malha.FindElementsByPoint(pnew[X],pnew[Y],pnew[Z], SMESH.FACE, grupoface )
				faces.update(newFaces)
	#endEM = time.time()
	#print '	Time finding sunspot: ' + str(endEM - startEM)
	return list(faces)

def CreateCloneFace(malhaAux,grupoface,linkFaces):
	#startCC = time.time()
	#Duplica e mapeia face que vai ser projetada
	facesAux = set()
	grupoAux = malhaAux.CreateEmptyGroup( SMESH.FACE, 'grupoClone' ) 
	for ids in grupoface.GetIDs():
		numNodes = Malha.GetElemNbNodes(ids)
		id = []
		for i in range(0,numNodes):
			pontoAux = Malha.GetNodeXYZ(Malha.GetElemNodes(ids)[i])
			id.append(malhaAux.AddNode(pontoAux[X],pontoAux[Y],pontoAux[Z]))
		newFaces = malhaAux.AddFace(id)
		linkFaces[newFaces] = ids
		facesAux.add(newFaces)

	grupoAux.Add(list(facesAux))
	#endCC = time.time()
	#print '			Time cloning face: ' + str(endCC - startCC)
	return grupoAux

def CreateGroupOfNodesMalhaAux(malhaAux,file):
	#Encontra mancha na face selecionada
	#startCG = time.time()
	#faceInclinada = malhaAux.CreateEmptyGroup( SMESH.NODE, 'FaceInclinada' )
	faceInclinada = []
	#Le arquivo de pontos
	with open(file) as f:
		for line in f:
			coord = line.split()
			#ajusta ponto importado - pode ser que as faces nao estejam exatamente sobrepostas
			ponto = float("{0:.2f}".format(float(coord[X]))),float("{0:.2f}".format(float(coord[Y]))),float("{0:.2f}".format(float(coord[Z])))
			#Cria um grupo de nodes
			faceInclinada.append([ponto[X], ponto[Y], ponto[Z]])
	#endCG = time.time()
	#print '			Time creating group of nodes: ' + str(endCG - startCG)
	return faceInclinada

def RotateAndProjectFace(file,grupoface):
	#startR = time.time()
	malhaAux = smesh.Mesh()
	linkFaces = {}
	faces = set()
	grupoAux = CreateCloneFace(malhaAux,grupoface,linkFaces)
	faceInclinada = CreateGroupOfNodesMalhaAux(malhaAux,file)
	#calcula normal da face inclinada
	ponto = faceInclinada[0]
	[unitNormal, dist]= CalculaAjusteFace(malhaAux,grupoAux,ponto[0],ponto[1],ponto[2])
	#Obtem angulo de rotacao
	angleY = GetAngle(unitNormal,1)
	#calcula angulo rotacao
	if unitNormal[X] > 0:
		angRotaciona = math.pi+angleY
	else:
		angRotaciona = math.pi-angleY
	#rotaciona planos
	malhaAux.RotateObject( grupoAux, SMESH.AxisStruct( 0, 0, 1, 0, 0, 1 ), angRotaciona, 0 )
	#malhaAux.RotateObject( faceInclinada, SMESH.AxisStruct( 0, 0, 1, 0, 0, 1 ), angRotaciona, 0 )
	#projeta plano com faces em Y , coloquei valor 10 soh para facilitar visualizacao em debug
	for id in grupoAux.GetNodeIDs():
		ponto = malhaAux.GetNodeXYZ(id)
		malhaAux.MoveNode( id, ponto[X], 10, ponto[Z] )
	#projeta conjuntos de pontos do sunspot em Y e procura pelas faces
	for ponto in faceInclinada:
		#rotaciona
		pontoR = Rotaciona(ponto, angRotaciona, [0, 0, 1])
		faceAux = malhaAux.FindElementsByPoint(pontoR[X],10,pontoR[Z], SMESH.FACE, grupoAux )
		for face in faceAux:
			faceOrig = linkFaces[face]
			faces.add(faceOrig)
	#endR = time.time()
	#print '		Time rotating: ' + str(endR - startR)
	return list(faces)

def FindGroup(grupos,nameFace):
	grupoface = 0
	#find target group faces 
	for grupo in grupos:
		ind = grupo.GetName().find(nameFace.upper())
		if (ind >= 0) :
			grupoface = grupo
	return grupoface
	
smesh = smeshBuilder.New(theStudy)
