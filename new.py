# -*- coding: latin-1 -*-
#!/usr/bin/env python
# coding: utf-8
# to do:
#ir buscar o imdb_id e verificar se a implementação do download que fiz está bem feita
# começar a criar html atraves do id do imdb para ver se bate certp*/

#o que o professor fez: 
#criou um .gz temporário com o base64decode e de seguida gunzip aquele ficheiro e a legenda limpinha

import sys, struct, os
from os import path

from pythonopensubtitles.opensubtitles import OpenSubtitles

opens = OpenSubtitles()
from pythonopensubtitles.utils import File
import zlib
import base64
import subprocess
import gzip


class Test(object):
	username = 'doctest'
	password = 'doctest'


def first():
	token = opens.login('bad@mail.com', 'badpassword')
	assert token == None
	token = opens.login(Test.username, Test.password)
	assert type(token) == str
	print "Token:\n" + token


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


def searchSubtitlesToImdbId(size, videoHash, Language):
	#data = opens.search_subtitles([{'sublanguageid': Language, 'moviehash': videoHash, 'moviebytesize': size}])
	#data = opens.search_subtitles([{'query': 'South Park', 'season': 1, 'episode': 1,'sublanguageid': 'por'}])
	data = opens.search_subtitles([{'sublanguageid': Language, 'moviehash': videoHash, 'moviebytesize': size}])
	#print "ola"
	#print data[0]
	imdb_id = int(data[0].get('IDMovieImdb'))
	#id_sub = int(data[0].get('IDSubtitleFile'))
	assert type(imdb_id) == int
	#print imdb_id
	return imdb_id


def searchSubtitlesToIDSubtitle(size, videoHash, Language):
	data = opens.search_subtitles([{'sublanguageid': Language, 'moviehash': videoHash, 'moviebytesize': size}])
	id_sub = int(data[0].get('IDSubtitleFile'))
	#print "ID da legenda", id_sub
	return id_sub


def videoSize(name):
	size = os.path.getsize(name)
	#assert type(size) == str
	#assert long(size)
	return size

def downloadSubtitle(idLegenda):
	data = opens.download_subtitles([idLegenda])
	#print data[0]
	# data [0 ] e data [1] tem a mesma coisa
	return data[0]

def gzinflate(base64_string):
	compressed_data = base64.decodestring(base64_string)
	return zlib.decompress(compressed_data, -15)

def manageSubtitleDownloaded(SubtitleStringEncoded,NomeDoFilme):
	#decode base 64 Ao Data
	stringDecoded= base64.decodestring(SubtitleStringEncoded)
	#escrever a String decoded para mais tarde ser UNGZIP
	fh = open(NomeDoFilme +'.txt', 'wb')
	fh.write(stringDecoded)
	fh.close()
	#UNGZIP
	f = open(NomeDoFilme +'.txt', 'rb')
	decompressed_data=zlib.decompress(f.read(), 16+zlib.MAX_WBITS)
	file_content = f.read()
	print "estive"
	print file_content
	f.close()
	#ESCREVER PARA O FICHEIRO DA LEGENDA E APAGAR O TEMP
	fl = open(NomeDoFilme +'.srt','wb')
	fl.write(decompressed_data)
	fl.close()
	actual = os.getcwd()
	print actual
	os.remove(actual+'/'+NomeDoFilme +'.txt')







def main(argv):
	if len(sys.argv) != 1:
		print "Usage: python legendas.py"
		sys.exit(1)
	else:
		first()
		#print "HashFile:"+hashFile('breakdance.avi')
		#print "VideoSize:",videoSize('breakdance.avi')
		hashValue= hashFile('Live.Free.Or.Die.Hard[2007]DvDrip-aXXo.avi')
		sizeValue = videoSize('Live.Free.Or.Die.Hard[2007]DvDrip-aXXo.avi')
		#print"ID do Imdb:",(searchSubtitlesToImdbId(b, a, 'por'))
		#print"ID da legenda:",(searchSubtitlesToIDSubtitle(b, a, 'por'))
		c = (searchSubtitlesToIDSubtitle(sizeValue, hashValue, 'por'))
		x = downloadSubtitle(c)
		#print (x)
		#print "Value : %s" %  x.get('data')
		enconde = x.get('data')
		#print enconde
		print len(enconde)
		print type(enconde)
		manageSubtitleDownloaded(enconde,'Live.Free.Or.Die.Hard[2007]DvDrip-aXXo')
		stringDecoded = base64.decodestring(enconde)
		#print len(stringDecoded)
		#print type(stringDecoded)
		#print stringDecoded
		#gzinflate(enconde)
		#ungziped_str = zlib.decompressobj().decompress('x\x9c' + stringDecoded)
		#String     = gzinflate(substr(base64.b64decode(enconde,10)))
		#print "StringDecoded:"

		'''
		fh = open('imageToSave.txt', 'wb')
		fh.write(stringDecoded)
		fh.close()


		#f_in = open('imageToSave.txt', 'rb')
		#f_out = gzip.open('file.txt.gz', 'wb')
		#f_out.writelines(f_in)
		#f_out.close()
		#f_in.close()

		f = open('imageToSave.txt', 'rb')
		decompressed_data=zlib.decompress(f.read(), 16+zlib.MAX_WBITS)
		file_content = f.read()
		print file_content
		f.close()

		f1 = open('legenda.srt','wb')
		f1.write(decompressed_data)
		f1.close()
		'''






if __name__ == "__main__":
	main(sys.argv[1:])