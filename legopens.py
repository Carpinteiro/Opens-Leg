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
import json
from time import sleep
import re

class Test(object):
	username = 'doctest'
	password = 'doctest'

config = {}
diretorias = []
folders_down = []
lista_de_extensoes = []

#login em opensubtitles, devolve o token deles
def first():
	token = opens.login('bad@mail.com', 'badpassword')
	assert token == None
	token = opens.login(Test.username, Test.password)
	assert type(token) == str

#ler o mypath do config
def getMyPath():
	with open('config.json') as handle:
		config.update(json.load(handle))
		my_path = config['diretoria']
		return my_path

#ler linguagens
def read_languages():
	with open('config.json') as handle:
		config.update(json.load(handle))
		Language = config['linguagens']
		return Language

#this hash function receives the name of the file and returns the hash code
def hashFile(name):
	try:

		longlongformat = 'q'  # long long
		bytesize = struct.calcsize(longlongformat)

		f = open(name, "rb")

		filesize = os.path.getsize(name)
		assert long(filesize)

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
#obter o tamanho do ficheiro para o request ao opensubtitles
def videoSize(name):
	a = os.getcwd() 
	size = os.path.getsize(name)
	return size

# dada uma diretoria : se encontra pastas cria o tuplo. Se encontra ficheiros verifica se tem legenda ou nao
def get_all_files(DiretoriaToSearch):
	folder = os.listdir(DiretoriaToSearch)
	files = []
	movie_list = []
	for file in folder:
		# se for uma pasta cria um tuplo (diretoria + nome pasta)
		if (os.path.isdir(file) and file and file != ".git"):
			tuplo = (DiretoriaToSearch,file)
			folders_down.append(tuplo)
		#se for um ficheiro
		else:
			files.append(file)

	for f in files:
		ext = f.split(".")
		#sem_ext e a extensao
		sem_ext = ext.pop(len(ext) - 1)
		#nf e o nome do ficheiro sem extensao
		nf = f[:-4]
		if (sem_ext == 'mkv' or sem_ext == 'mp4' or sem_ext == 'avi'):
			check = nf + '.srt'
			os.chdir(DiretoriaToSearch)
			if not (os.path.isfile(check)):
				print "Não existe legenda para : ", nf
				movie_list.append(f)
	return movie_list
#Efetuar download para pastas existentes nos niveis abaixo -> folders_down	
def do_recursive_downloads():
	language = read_languages()
	while len(folders_down) != 0:
		for tuplo in folders_down:
			n = 0
			diretoria = tuplo[n]
			nome_pasta = tuplo[n+1]
			together = diretoria + '/' + nome_pasta
			os.chdir(together)
			y = get_all_files(together)
			
			if len(y) != 0:
				print "\nLista de filmes sem legenda na pasta:"+together
				print y
				createArraySubtitlesId(y,language,together)
				folders_down.remove(tuplo)
			else:
				folders_down.remove(tuplo)
				
				
#metodo que vai para cada ficheiro sem legenda apanhar o ID da mesma, fazer o download , e descodificar e organizar por pasta(chama o download e o manage)
def createArraySubtitlesId(filesWithNoLegend,LanguageChoosen,diretoria_Actual):
	array = []
	for file in filesWithNoLegend:
		if type(file).__name__ == 'unicode':
			novo = unicodedata.normalize('NFKD', file).encode('ascii','ignore')
			c = (searchSubtitlesToIDSubtitle(videoSize(novo), hashFile(novo),LanguageChoosen))
		elif type(file).__name__ == 'str':
			dir_act = os.getcwd()
			os.chdir(dir_act)
			c = (searchSubtitlesToIDSubtitle(videoSize(file), hashFile(file),LanguageChoosen))

		if c is None:
			print "Não Conseguimos arranjar legenda para:" + novo
		else:
			d = (searchSubtitlesToImdbId(videoSize(file), hashFile(file)))
			e = (get_informations(videoSize(file), hashFile(file), LanguageChoosen))
			NomeParaPasta = e[2]
			#Manage ao nome vindo da API para criar a pasta com o nome da Serie-> '"Breaking Bad" Mas'
			getAspa = e[3]
			aspa2 = getAspa.find('"',1)
			firstCheck = getAspa[1:aspa2]
			
			#NumeroEpisodio
			thirdCheck = e[0]

			#Ver se é filme ou um episódio de uma série
			typeOfVideo = getTypeOfVideo(d)
			if typeOfVideo == 'movie' or typeOfVideo == 'game':
				#download da legenda para o ficheiro
				x = downloadSubtitle(c)
				#get para obter a codificação
				enconde = x.get('data')
				#manage à codificação e ao ficheiro html
				manageSubtitleDownloaded(enconde,novo,e)
				array.append(enconde)

			elif typeOfVideo == 'episode':
				#pasta inicial das series
				chk = my_path + '/SeriesFromMyProgram'
				#criar pasta Series
				if not (os.path.exists(chk)):
					os.makedirs(chk)
				toMove = diretoria_Actual + "/"+ file				
				#checkar se a série já lá existe
				chk2 = chk +"/"+firstCheck
				#Pasta com nome da série + pasta "Temporadas"
				if not(os.path.exists(chk2)):
					os.makedirs(chk2)
				chk3 = chk2 + "/" + "Temporada " + str(NomeParaPasta)
				if not(os.path.exists(chk3)):
					os.makedirs(chk3)
				chk4 = chk3 + "/" +"Episodio "+ str(thirdCheck)
				if not(os.path.exists(chk4)):
					os.makedirs(chk4)
				shutil.move(toMove,chk4)

				x = downloadSubtitle(c)
				#get para obter a codificação
				enconde = x.get('data')
				#manage à codificação e ao ficheiro html
				os.chdir(chk4)
				manageSubtitleDownloaded(enconde,novo,e)
				os.chdir(diretoria_Actual)
				array.append(enconde)
			



		
	return array
#Perguntar à api do Imdb se é filme ou série por causa das organizações
def getTypeOfVideo(ImdbIdOpenSubtitles):
	ImdbApiArray = []
	urlApiImdb = 'http://www.omdbapi.com/'
	
	#manage Imdb id to this api
	filled = str(ImdbIdOpenSubtitles).zfill(7)
	toSend = 'tt'+filled

	parameters = {'i': toSend, 'plot': 'short', 'r': 'json'}
	r = requests.get(urlApiImdb,params = parameters)
	a = r.json()
	tipo = unicodedata.normalize('NFKD', a.get('Type')).encode('ascii','ignore')
	return tipo


def downloadSubtitle(idLegenda):
	data = opens.download_subtitles([idLegenda])
	# data [0 ] e data [1] tem a mesma coisa
	return data[0]

#tal como o metodo diz , descodifica a legenda codificada, e faz a gestão dos ficheiros
def manageSubtitleDownloaded(SubtitleStringEncoded, NomeDoFilme,ListaWithInformationForOneFile):
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
	os.remove(actual + '/' + NomeDoFilme + '.txt')
	
	create = actual + '/'+ leg
	legenda = leg + '.srt'
	
	if not os.path.exists(create):
		os.makedirs(create)
		shutil.move(NomeDoFilme, create)
		shutil.move(legenda,create)
	#HTML
	createFileHtml(ListaWithInformationForOneFile,create)
	#Criar pasta e mexer para lá os ficheiros
		

# Get o id da legenda par download
def searchSubtitlesToIDSubtitle(size, videoHash,LanguageChoosen):
	while True:
		try:
			data = opens.search_subtitles([{'sublanguageid': LanguageChoosen, 'moviehash': videoHash, 'moviebytesize': size}])
			if not isinstance(data,bool):
				id_sub = int(data[0].get('IDSubtitleFile'))
				return id_sub
			else:
				break
			
		except OverflowError:
			print "Legenda não encontrada na Base de Dados"
			return -1
		
# Get o imdb id do ficheiro
def searchSubtitlesToImdbId(size, videoHash):
	while True:
		try:
			data = opens.search_subtitles([{'moviehash': videoHash, 'moviebytesize': size}])
			if not isinstance(data,bool):
				imdb_id = int(data[0].get('IDMovieImdb'))
				assert type(imdb_id) == int
				return imdb_id
			else:
				break
		except OverflowError:
			print "Legenda não encontrada nãoa base de dados"
#get as outras Informacoes
def get_informations(size,videoHash,LanguageChoosen):
	retorno = []
	while True:
		try:
			data = opens.search_subtitles([{'sublanguageid': LanguageChoosen, 'moviehash': videoHash, 'moviebytesize': size}])
			if not isinstance(data,bool):
				serieEpisode = int(data[0].get('SeriesEpisode'))
				tuplo = ('SeriesEpisode',serieEpisode)
				retorno.append(serieEpisode)
				
				ImdbRating = float(data[0].get('MovieImdbRating'))
				tuplo1 = ('MovieImdbRating',ImdbRating)
				ImdbRating1 =round(ImdbRating,2)
				retorno.append(ImdbRating1)
				
				serieSeason = int(data[0].get('SeriesSeason'))
				tuplo2 = ('SeriesSeason',serieSeason)
				retorno.append(serieSeason)
				
				AnotherNomeOrigin = (data[0].get('MovieName'))
				tuplo4 = ('MovieName',AnotherNomeOrigin)
				retorno.append(AnotherNomeOrigin)
				
				idDoSiteImdb = int(data[0].get('IDMovieImdb'))
				tuplo5 = ('IDMovieImdb',idDoSiteImdb)
				retorno.append(idDoSiteImdb)
				
				AnoFilme = int(data[0].get('MovieYear'))
				tuplo6 = ('MovieYear',AnoFilme)
				retorno.append(AnoFilme)

				return retorno
			else:
				break
		except OverflowError:
			print "Legenda não encontrada na Base de Dados"
			return -1
#criar o html e o css respetivo
def createFileHtml(ListaWithInformationForOneFile,DiretoriaComPastaFilme):
	n = 0
	serieEpisode = 'Serie Episode:'
	imdbRating = 'Imdb Rating:'
	serieSeason = 'Serie Season'
	nameMovie = 'Movie :'
	movieYear = 'Movie Year:'
	#EpisodioDaSerie
	es = ListaWithInformationForOneFile[n]
	#ImdbRating
	ir = ListaWithInformationForOneFile[n+1]
	#pequena Conversao
	ir1 = ("{:.1f}".format(ir))
	#TemporadaDaSerie
	ts = ListaWithInformationForOneFile[n+2]
	#NomeFilme/NomeEpisodio
	nm = ListaWithInformationForOneFile[n+3]
	#ImdbID
	imi = ListaWithInformationForOneFile[n+4]
	#AnoFilme / Série
	yr = ListaWithInformationForOneFile[n+5]

	NomeFicheiro = nm+'.html'
	fileHtml = open(os.path.join(DiretoriaComPastaFilme, NomeFicheiro), "w")
	Inf = getImdbInfApi(imi)
	#Descrição do filme
	dsc = Inf[n]
	#Imagem Do poster do filme
	im = Inf[n+1]
	#Actores Principais Do filme
	ap = Inf[n+2]
	#Director
	dr = Inf[n+3]
	#Prémios
	aw = Inf[n+4]


	message = """<html lang = "pt">
	<head>
		<link rel="stylesheet" href="style.css">
		<meta charset = "utf-8">
		<title>Information</title>
	</head>
	<body>
		
		<div id="header">
			<div itemscope itemtype="http://schema.org/Movie">
				<h1 itemprop="name">%s</h1>
			</div>
		</div>

		<div id ="desc">
			<h2>%s</h2>
		</div>
		
		<div id="section">
			<div itemscope itemtype="http://schema.org/Movie">
				<span><p><b>Director:</b> %s</p></span>
				<span><p><b>Actores Principais:</b> %s</p></span>
			  	<p><b>Temporada:</b> %d </p>
			  	<p><b>Episodio:</b>%d</p>
			  	<p><b>ImdbRating:</b>%s</p>
			  	<p><b>AnoFilme:</b>%d</p>
			  	<p><b>Premios:</b>%s</p>
			  	<p><b>Link Do Imdb:</b><a href="http://www.imdb.com/title/tt%d/">IMDB</a></p>
			</div>  	
		</div>
		<div id="image">
			<img src = %s>
		</div>

		<div id="footer">
			José Carpinteiro º Universidade de Évora
		</div>
		<div id="footerImage">
			<img src = "https://gesdoc.uevora.pt/img/logo_ue_auth.jpg">
		</div>
		  	

	</body>
	</html>"""%(nm,dsc,dr,ap,ts,es,ir1,yr,aw,imi,im)
	fileHtml.write(message)
	fileHtml.close()

	fileCss = open(os.path.join(DiretoriaComPastaFilme, 'style.css'), "w")
	messageCss = """#header {
    text-align: center;
    font-size:large;
    
}
#desc {
    line-height:30px;
    border: 5px solid navy;
    background-color:#eeeeee;
    text-align:center;
    padding:5px; 
}
#section {
	font-size:20px;
    width:350px;
    float:left;
    padding:10px; 
}
#image {
	padding:5px;
	width:500px;
	margin-left: auto;
    margin-right: auto;
}
#footer {
    margin-top: 100px;
    background-color:black;
    color:white;
    clear:both;
    text-align:center;
    padding:5px; 
}
#footerImage {
	width = 350;
	text-align:center;
	float:bottom;
	margin-top:10 px
}"""

	fileCss.write(messageCss)
	fileCss.close()

	

def getImdbInfApi(ImdbId):
	ImdbApiArray = []
	urlApiImdb = 'http://www.omdbapi.com/'
	
	#manage Imdb id to this api
	filled = str(ImdbId).zfill(7)
	toSend = 'tt'+filled

	parameters = {'i': toSend, 'plot': 'short', 'r': 'json'}

	r = requests.get(urlApiImdb,params = parameters)
	sleep(1)
	a = r.json()
	descr = unicodedata.normalize('NFKD', a.get('Plot')).encode('ascii','ignore')
	imagem = unicodedata.normalize('NFKD', a.get('Poster')).encode('ascii','ignore')
	actores = unicodedata.normalize('NFKD', a.get('Actors')).encode('ascii','ignore')
	director = unicodedata.normalize('NFKD', a.get('Director')).encode('ascii','ignore')
	premios = unicodedata.normalize('NFKD', a.get('Awards')).encode('ascii','ignore')
	ImdbApiArray.append(descr)
	ImdbApiArray.append(imagem)
	ImdbApiArray.append(actores)
	ImdbApiArray.append(director)
	ImdbApiArray.append(premios)
	return ImdbApiArray


def main(argv):
	if len(sys.argv) != 1:
		print "Usage: python legendas.py"
		sys.exit(1)
	else:
		first()
		global my_path
		my_path = getMyPath()
		print my_path
		linguagem = read_languages()
		print linguagem
		#check_language(linguagens)
		#languages_choosen = raw_input("I want subtitles in :")

		x = get_all_files(my_path)
		print "Pasta base lista filmes sem legenda:",x
		createArraySubtitlesId(x,linguagem,my_path)
		#print "array",novo
		do_recursive_downloads()


if __name__ == "__main__":
	main(sys.argv[1:])
