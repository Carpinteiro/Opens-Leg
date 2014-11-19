# -*- coding: latin-1 -*-
import os.path
import hashlib
import sys
import urllib2
import requests
import urllib
import urllib2
import glob
import json
from os import listdir
from os.path import isfile, join
import collections
import traceback
from urllib2 import Request, urlopen, URLError, HTTPError
import shutil

my_path = ""
config ={}

# função que basicamente faz o controlo de pastas e cria e move as pastas para se organizarem
def get_all_series():
	#global season_number
	directorio_organizar = my_path + "Series"
	#print directorio_organizar
	os.chdir(directorio_organizar)
	retval = os.getcwd()
	#series é a lista com todas as pastas dentro da pasta Series
	series = os.listdir(directorio_organizar)
	#print retval
	#print "Pastas contidas dentro das series:"
	#print series
	for pastas in series:
		lista_do_nome = pastas.split(".")
		#se nao for uma pasta so com o nome da serie
		if not len(lista_do_nome) == 1:
			nome_da_serie = lista_do_nome[0]
			#print "nome_da_serie:"
			#print nome_da_serie
			season_number = ""
			episode_number = ""
			#info é a parte do nome onde está a temporada e o episódio
			info = lista_do_nome[1]
			#print info
			#percorrer a informação da serie
			for index in range(len(info)):
				#print "info[index"
				#print info[index]
				if (info[index] == 'S'):
					season_number += info[index]
					season_number += info[index+1]
					season_number += info[index+2]
					#print season_number

				elif(info[index] == 'E'):
					episode_number = info[index]
					episode_number += info[index+1] 
					episode_number += info[index+2]
					#print episode_number
				else:
					print "parsing"
				#print season_number
				#print episode_number
			#se nao existir a pasta com o nome da serie
			if not os.path.exists(nome_da_serie):
				os.mkdir(nome_da_serie)
				entrar_dentro_da_pasta = directorio_organizar + '/'+nome_da_serie
				#print entrar_dentro_da_pasta
				os.chdir(entrar_dentro_da_pasta)

				onde_estou = os.getcwd()
				primeiro_nivel = entrar_dentro_da_pasta +'/'+ season_number
				segundo_nivel = primeiro_nivel + '/' + episode_number

				#print "onde estou"
				#print onde_estou
				#print "season_number"
				#print season_number
				os.mkdir(season_number)
				os.chdir(primeiro_nivel)
				os.mkdir(episode_number)
				os.chdir(directorio_organizar)
				shutil.move(pastas,segundo_nivel)
			
			#se ja existir a pasta com o nome da serie
			
			else:
				entrar_dentro_da_pasta = directorio_organizar + '/'+nome_da_serie
				primeiro_nivel = entrar_dentro_da_pasta +'/'+ season_number
				segundo_nivel = primeiro_nivel + '/' + episode_number
				os.chdir(entrar_dentro_da_pasta)
				#se ainda nao existir pasta para aquela season
				if not os.path.exists(season_number):
					os.mkdir(season_number)
					os.chdir(primeiro_nivel)
					os.mkdir(episode_number)
					os.chdir(directorio_organizar)
					shutil.move(pastas,segundo_nivel)
				#ou se ja existe, simplesmente desce de nivel
				else:
					try:
						os.chdir(primeiro_nivel)
						os.mkdir(episode_number)
						os.chdir(directorio_organizar)
						shutil.move(pastas,segundo_nivel)
					except Exception, e:
						print "Ja existe Esse ficheiro"

				#print "EXISTE"
				#if not os.path.exists()
			
#ler my path
def read_configurations():
	return config['diretoria']

def main(argv):
	if len(sys.argv) != 1:
		print "Usage: python organize.py"
	else:
		print "Se você quiser que eu lhe organize as séries por favor crie uma pasta VAZIA com o nome'Series'"
		print "E copie para a pasta todas as pastas de séries que foram criadas quando foi feito o download\n\n"
		print "Independemente da série peço por favor, para Escrever o nome da série,separado por um ponto,da temporada e episódio"
		print "Exemplo: Californication.S07E05.720p.HDTV.x264-2HD"
		print "Exemplo: Game of Thrones.S02E01\n\n"


		global my_path
		with open('config.json') as handle:
			config.update(json.load(handle))
		my_path = read_configurations()

		get_all_series()


if __name__ == '__main__':
	main(sys.argv[1:])