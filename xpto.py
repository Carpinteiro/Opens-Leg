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

class Test(object):
	username = 'doctest'
	password = 'doctest'

config = {}
diretorias = []
diretorias_down = []
lista_de_extensoes = []

#login em opensubtitles, devolve o token deles
def first():
	token = opens.login('bad@mail.com', 'badpassword')
	assert token == None
	token = opens.login(Test.username, Test.password)
	assert type(token) == str
	print "Token:\n" + token

#ler o mypath do config
def getMyPath():
	with open('config.json') as handle:
		config.update(json.load(handle))
		#print config["diretoria"]
		my_path = config['diretoria']
		return my_path

#ler linguagens
def read_languages():
	with open('config.json') as handle:
		config.update(json.load(handle))
		#print config["diretoria"]
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

def videoSize(name):
	a = os.getcwd()
	print "ONDE TOU getting videoSize:",a 
	size = os.path.getsize(name)
	return size

# dada uma diretoria : se encontra pastas cria o tuplo. Se encontra ficheiros verifica se tem legenda ou nao
def get_all_files(DiretoriaToSearch):
	diretoria = os.listdir(DiretoriaToSearch)
	ficheiros = []
	lista_de_filmes = []
	for file in diretoria:
		# se for uma pasta cria um tuplo (diretoria + nome pasta)
		if (os.path.isdir(file) and file != "Series" and file != ".git"):
			tuplo = (DiretoriaToSearch,file)
			#print "vou adicionar este tuplo a lista das diretorias down",tuplo
			diretorias_down.append(tuplo)
		#se for um ficheiro
		else:
			ficheiros.append(file)

	for f in ficheiros:
		ext = f.split(".")
		#sem_ext e a extensao
		sem_ext = ext.pop(len(ext) - 1)
		#nf e o nome do ficheiro sem extensao
		nf = f[:-4]
		#print sem_ext
		if (sem_ext == 'mkv' or sem_ext == 'mp4' or sem_ext == 'avi'):
			check = nf + '.srt'
			os.chdir(DiretoriaToSearch)
			if not (os.path.isfile(check)):
				print "Não existe legenda para : ", nf
				lista_de_filmes.append(f)
	#print 'Diretorias a sair do get all files :', diretorias_down
	return lista_de_filmes
	
def do_recursive_downloads():
	language = read_languages()
	#print "\nDiretorias inicias para checkar:",diretorias_down
	while len(diretorias_down) != 0:
		#print "Tamanho da Lista",len(diretorias_down)
		for tuplo in diretorias_down:
			n = 0
			diretoria = tuplo[n]
			nome_pasta = tuplo[n+1]
			together = diretoria + '/' + nome_pasta
			#print "Together:",together
			os.chdir(together)
			y = get_all_files(together)
			
			if len(y) != 0:
				print "\nLista de filmes sem legenda na pasta:"+together
				print y
				createArraySubtitlesId(y,language,together)
				diretorias_down.remove(tuplo)
				#print "Depois de removido com ficheiros para sacar legenda:",diretorias_down
			else:
				diretorias_down.remove(tuplo)
				#print "Depois de removido sem ficheiros para sacar legenda:",diretorias_down
				
			#print "Ciclo Das diretorias :",diretorias_down
				
				
#metodo que vai para cada ficheiro sem legenda apanhar o ID da mesma, fazer o download , e descodificar e organizar por pasta
def createArraySubtitlesId(filesWithNoLegend,LanguageChoosen,diretoria_Actual):
	array = []
	for file in filesWithNoLegend:
		if type(file).__name__ == 'unicode':
			#print "myvar is unicode!"
			novo = unicodedata.normalize('NFKD', file).encode('ascii','ignore')
			c = (searchSubtitlesToIDSubtitle(videoSize(novo), hashFile(novo),LanguageChoosen))
			#print "C:",c
			d = (searchSubtitlesToImdbId(videoSize(file), hashFile(file)))
			#print "D:",d
			e = (get_informations(videoSize(file), hashFile(file), LanguageChoosen))
			print "\n\n\Informações",e
		elif type(file).__name__ == 'str':
			#print "myvar is a string!"
			dir_act = os.getcwd()
			os.chdir(dir_act)
			c = (searchSubtitlesToIDSubtitle(videoSize(file), hashFile(file),LanguageChoosen))
			print "C:",c
			d = (searchSubtitlesToImdbId(videoSize(file), hashFile(file)))
			print "D:",d
			e = (get_informations(videoSize(file), hashFile(file), LanguageChoosen))
			print "\n\n\n\n\n\n\n Informações\n\n\n\n\n",e 
			
		#download da legenda para o ficheiro
		x = downloadSubtitle(c)
		#get para obter a codificação
		enconde = x.get('data')
		#manage à codificação e ao ficheiro html
		manageSubtitleDownloaded(enconde,file,e)
		array.append(enconde)
	return array

def downloadSubtitle(idLegenda):
	data = opens.download_subtitles([idLegenda])
	#print data[0]
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
	print actual
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
		

# Get the sub id to download
def searchSubtitlesToIDSubtitle(size, videoHash,LanguageChoosen):
	while True:
		try:
			data = opens.search_subtitles([{'sublanguageid': LanguageChoosen, 'moviehash': videoHash, 'moviebytesize': size}])
			#print "\n\nDados:\n\n",data[0]
			id_sub = int(data[0].get('IDSubtitleFile'))
			print "ID da legenda", id_sub
			return id_sub
		except OverflowError:
			print "Legenda não encontrada na Base de Dados"
			return -1
		
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
	print "Imdb ID:",imdb_id
	return imdb_id
#get all the others Informations
def get_informations(size,videoHash,LanguageChoosen):
	retorno = []
	while True:
		try:
			data = opens.search_subtitles([{'sublanguageid': LanguageChoosen, 'moviehash': videoHash, 'moviebytesize': size}])
			
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
		except OverflowError:
			print "Legenda não encontrada na Base de Dados"
			return -1
			
def createFileHtml(ListaWithInformationForOneFile,DiretoriaComPastaFilme):
	n = 0
	print "Create Html:",DiretoriaComPastaFilme 
	serieEpisode = 'Serie Episode:'
	imdbRating = 'Imdb Rating:'
	serieSeason = 'Serie Season'
	nameMovie = 'Movie :'
	movieYear = 'Movie Year:'
	#EpisodioDaSerie
	a = ListaWithInformationForOneFile[n]
	#ImdbRating
	b = ListaWithInformationForOneFile[n+1]
	b1 = ("{:.1f}".format(b))
	print "TIPO:",b1
	print type(b1)
	#Imagem Do poster do filme
	#TemporadaDaSerie
	c = ListaWithInformationForOneFile[n+2]
	#NomeFilme/Episodio da Série
	d = ListaWithInformationForOneFile[n+3]
	#ImdbID
	e = ListaWithInformationForOneFile[n+4]
	#AnoFilme / Série
	f = ListaWithInformationForOneFile[n+5]

	#os.chdir(DiretoriaComPastaFilme)
	NomeFicheiro = d+'.html'
	fileHtml = open(os.path.join(DiretoriaComPastaFilme, NomeFicheiro), "w")
	Inf = getImdbInfApi(e)
	#Descrição do filme
	g = Inf[n]
	#Imagem Do poster do filme
	h = Inf[n+1]
	#Actores Principais Do filme
	i = Inf[n+2]
	#Director
	j = Inf[n+3]
	#Prémios
	k = Inf[n+4]


	message = """<html lang = "pt">
	<head>
		<link rel="stylesheet" href="style.css">
		<meta charset = "utf-8">
		<title>Information</title>
	</head>
	<body>
		
		<div id="header">
			<h1>%s</h1>
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
	</html>"""%(d,g,j,i,c,a,b1,f,k,e,h)
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
	#http://www.omdbapi.com/?i=tt0099423&plot=short&r=json
	ImdbApiArray = []
	urlApiImdb = 'http://www.omdbapi.com/'
	
	#manage Imdb id to this api
	filled = str(ImdbId).zfill(7)
	print filled
	toSend = 'tt'+filled
	print toSend

	parameters = {'i': toSend, 'plot': 'short', 'r': 'json'}
	#url = urlApiImdb.format(urllib.urlencode(params))
	#req = urllib2.Request(url)
	r = requests.get(urlApiImdb,params = parameters)
	print (r.url)
	sleep(1)
	a = r.json()
	print a
	#inPyth = json.loads(r.json)
	#print inPyth
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
	print "Result:",ImdbApiArray
	return ImdbApiArray
	'''
	try:
		response = urllib2.urlopen(req)
	except HTTPError,e:
		print 'The server couldn\'t fulfill the request.'
		print 'Error code: ',e.code, 'Not Found'
		return 0
	
	else:
		print response.info()
		print response.content()'''





	



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
		print "Pasta base lista filmes sem legenda:",x
		print "diretorias matches iniciais:",diretorias_down
		createArraySubtitlesId(x,linguagem,my_path)
		#print "array",novo
		do_recursive_downloads()
		#now_download_for_all_folders_down(diretorias_down,linguagem)


if __name__ == "__main__":
	main(sys.argv[1:])