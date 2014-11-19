# -*- coding: latin-1 -*-
# install wget , requests
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

import sys, struct, os
from os import path

from pythonopensubtitles.opensubtitles import OpenSubtitles
from symbol import for_stmt
from parted import filesystem

opens = OpenSubtitles()
from pythonopensubtitles.utils import File
import zlib
import base64
import subprocess
import gzip
import unicodedata




class Test(object):
	username = 'doctest'
	password = 'doctest'

#my_path = "/home/carpinteiro/WorkSpace/Python/"
config = {}
#config = 'config.txt'
linguagens = 'linguagens.txt'
diretorias = []
#lista_de_filmes = []
lista_de_legendas = []
lista_de_extensoes = []
#verificar se o ficheiro existe
'''if not os.path.isfile(HASHES_FILE):
		logger.info("hash file does not exist yet")
		return'''


def first():
	token = opens.login('bad@mail.com', 'badpassword')
	assert token == None
	token = opens.login(Test.username, Test.password)
	assert type(token) == str
	print "Token:\n" + token


#this hash function receives the name of the file and returns the hash code
def hashFile(name):
	try:

		longlongformat = 'q'  # long long
		bytesize = struct.calcsize(longlongformat)

		f = open(name, "rb")

		filesize = os.path.getsize(name)
		#cast para String para passar como parametro depois
		#assert type(filesize) == str
		assert long(filesize)
		#print filesize

		hash = filesize

		if filesize < 65536 * 2:
			return "SizeError"

		for x in range(65536 / bytesize):
			buffer = f.read(bytesize)
			(l_value,) = struct.unpack(longlongformat, buffer)
			hash += l_value
			hash = hash & 0xFFFFFFFFFFFFFFFF  #to remain as 64bit number

		f.seek(max(0, filesize - 65536), 0)
		for x in range(65536 / bytesize):
			buffer = f.read(bytesize)
			(l_value,) = struct.unpack(longlongformat, buffer)
			hash += l_value
			hash = hash & 0xFFFFFFFFFFFFFFFF

		f.close()
		returnedhash = "%016x" % hash
		assert type(returnedhash) == str
		return returnedhash

	except(IOError):
		return "IOError"

def videoSize(name):
	a = os.getcwd()
	print "ONDE TOU :",a 
	size = os.path.getsize(name)
	#assert type(size) == str
	#assert long(size)
	return size


# Get the imdb id do ficheiro
def searchSubtitlesToImdbId(size, videoHash):
	#data = opens.search_subtitles([{'sublanguageid': Language, 'moviehash': videoHash, 'moviebytesize': size}])
	#data = opens.search_subtitles([{'query': 'South Park', 'season': 1, 'episode': 1,'sublanguageid': 'por'}])
	data = opens.search_subtitles([{'moviehash': videoHash, 'moviebytesize': size}])
	#print "ola"
	#print data[0]
	imdb_id = int(data[0].get('IDMovieImdb'))
	#id_sub = int(data[0].get('IDSubtitleFile'))
	assert type(imdb_id) == int
	#print imdb_id
	return imdb_id


# Get the sub id to download
def searchSubtitlesToIDSubtitle(size, videoHash,LanguageChoosen):
	while True:
		try:
			data = opens.search_subtitles([{'sublanguageid': LanguageChoosen, 'moviehash': videoHash, 'moviebytesize': size}])
			id_sub = int(data[0].get('IDSubtitleFile'))
			print "ID da legenda", id_sub
			return id_sub
		except OverflowError:
			print "Legenda não encontrada na Base de Dados"
			return -1
			
		

#verifica se o ficheiro existe
def find_file_extension(filename):
	return os.path.isfile(filename)

#ler linguagens
def read_languages():
	with open('config.json') as handle:
		config.update(json.load(handle))
		#print config["diretoria"]
		Language = config['linguagens']
		return Language


#fazer o download de legendas para a lista de videos sem legenda
def getMyPath():
	with open('config.json') as handle:
		config.update(json.load(handle))
		#print config["diretoria"]
		my_path = config['diretoria']
		return my_path

#fazer o download de ficheiros que estejam noutras pastas na mesma diretoria
def do_recursive_downloads():
	print "Diretorias restantes:",diretorias
	language = read_languages()
	actual = os.getcwd()
	print "Actual:", actual
	
	if len(diretorias) == 0:
		return
	
	for dire in diretorias:
		novadir =  actual + '/' + dire
		print "Novadir:",novadir
		#mudar e verificacao que mudou a diretoria
		os.chdir(novadir)
		retval = os.getcwd()
		print "Directory changed successfully %s" % retval
		#lista com os filmes a sacar da nova diretoria
		y = get_all_files(retval)
		print y
		if len(y) == 0:
			diretorias.remove(dire)
			print "\nLista de filmes sem legenda mais abaixo:\n"
			print y	
		else:
			print "\nLista de filmes sem legenda mais abaixo:\n"
			print y
			diretorias.remove(dire)
			n = createArraySubtitlesId(y,language)
		
#devolve uma lista com todos os filmes sem legenda e guarda as diretorias encontradas
def get_all_files(diretoriaSearch):
	diretoria = os.listdir(diretoriaSearch)
	ficheiros = []
	print "diretoria",diretoria
	lista_de_filmes = []
	for file in diretoria:
		if (os.path.isdir(file) and file != "Series"):
			diretorias.append(file)
		#se for um ficheiro
		else:
			ficheiros.append(file)
	print "Ficheiros para analisar:",ficheiros
	for f in ficheiros:
		ext = f.split(".")
		#sem_ext e a extensao
		sem_ext = ext.pop(len(ext) - 1)
		#nf é o nome do ficheiro sem extensao
		nf = f[:-4]
		#print sem_ext
		if (sem_ext == 'mkv' or sem_ext == 'mp4' or sem_ext == 'avi'):
			check = nf + '.srt'
			directoria_actual = os.getcwd()
			os.chdir(directoria_actual)
			#print check
			print "directoria_actual_get_all_files:"+'\n' , directoria_actual
			if not (os.path.isfile(check)):
				lista_de_filmes.append(f)
	#print 'Diretorias:', diretorias
	return lista_de_filmes


def gzinflate(base64_string):
	compressed_data = base64.decodestring(base64_string)
	return zlib.decompress(compressed_data, -15)

def downloadSubtitle(idLegenda):
	data = opens.download_subtitles([idLegenda])
	#print data[0]
	# data [0 ] e data [1] tem a mesma coisa
	return data[0]

#tal como o metodo diz , descodifica a legenda codificada, e faz a gestão dos ficheiros
def manageSubtitleDownloaded(SubtitleStringEncoded, NomeDoFilme):
	#decode base 64 Ao Data
	stringDecoded = base64.decodestring(SubtitleStringEncoded)
	#escrever a String decoded para mais tarde ser UNGZIP
	fh = open(NomeDoFilme + '.txt', 'wb')
	fh.write(stringDecoded)
	fh.close()
	#UNGZIP
	f = open(NomeDoFilme + '.txt', 'rb')
	decompressed_data = zlib.decompress(f.read(), 16 + zlib.MAX_WBITS)
	file_content = f.read()
	f.close()
	
	#ESCREVER PARA O FICHEIRO DA LEGENDA E APAGAR O TEMP
	leg = NomeDoFilme[:-4]
	fl = open(leg+ '.srt', 'wb')
	fl.write(decompressed_data)
	fl.close()
	actual = os.getcwd()
	print actual
	os.remove(actual + '/' + NomeDoFilme + '.txt')
	#Criar pasta e mexer para lá os ficheiros
	
	create = actual + '/'+ leg
	legenda = leg + '.srt'
	
	if not os.path.exists(create):
		os.makedirs(create)
		shutil.move(NomeDoFilme, create)
		shutil.move(legenda,create)
		
	
#metodo que vai para cada ficheiro sem legenda apanhar o ID da mesma, fazer o download , e descodificar e organizar por pasta
def createArraySubtitlesId(filesWithNoLegend,LanguageChoosen):
	#print filesWithNoLegend
	array = []
	for file in filesWithNoLegend:
		if type(file).__name__ == 'unicode':
			dir_act = os.getcwd()
			os.chdir(dir_act)
			novo = unicodedata.normalize('NFKD', file).encode('ascii','ignore')
			c = (searchSubtitlesToIDSubtitle(videoSize(novo), hashFile(novo),LanguageChoosen))
			print "myvar is unicode!"
		elif type(file).__name__ == 'str':
			print "myvar is a string!"
			dir_act = os.getcwd()
			os.chdir(dir_act)
			c = (searchSubtitlesToIDSubtitle(videoSize(file), hashFile(file),LanguageChoosen))
		
		#download da legenda para o ficheiro
		x = downloadSubtitle(c)
		#get para obter a codificação
		enconde = x.get('data')
		#manage à codificação
		manageSubtitleDownloaded(enconde,file)
		array.append(enconde)
	return array
		
		
	
def main(argv):
	if len(sys.argv) != 1:
		print "Usage: python legendas.py"
		sys.exit(1)
	else:
		first()
		my_path = getMyPath()
		print my_path
		linguagem = read_languages()
		print linguagem
		#check_language(linguagens)
		#languages_choosen = raw_input("I want subtitles in :")

		print "\nLista de filmes sem legenda:\n"
		x = get_all_files(my_path)
		print '\n'+'\n'+'\n'"Pasta_base_no_filmes:",x
		novo = createArraySubtitlesId(x,linguagem)
		#print "array",novo
        do_recursive_downloads()
		
	#raw_input("\nPress Enter to download subtitles to those movies...")

	#do_list_download(x)
	#raw_input("\nPress Enter to download other diretories...")
	#do_recursive_downloads()
	#Voltar à pasta inicial


if __name__ == "__main__":
	main(sys.argv[1:])

