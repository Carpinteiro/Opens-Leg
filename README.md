Opensubtitles -Legendas Automáticas
=========
>Programa que dada uma diretoria e uma linguagem , verirfica todos os ficheiros de vídeo sem legenda nessa diretoria e restantes hierarquicamente abaixo, e obtém a legenda para os mesmos , tal como uma página html com uma breve informação acerca do filme/série ,a sua foto,bem como o link para o imdb.

####Programa testado em:

  - Linux Mint 64 Bits
  - Linux Mint 32 Bits
  - Elementary Os 64 bits

### Api's utilizadas para recolha de informação e desenvolvimento do projecto



* [OpenSubtitles] - Api do famoso site de legendas fornecida para desenvolvedores
* [Imdb] - Serviço Web grátis para obter informações sobre filmes/séries

### Requisitos para funcionar:
* Python 2.7.6
* Sistema Operativo Linux (Não testado para todos)
* Ter o gestor de pacotes do python instalado:

```sh
$ sudo apt-get install python-pip
```

```sh
$ sudo pip install requests
```

### Ficheiro config.json:

```sh
{
	"diretoria": "/diretoria_onde_o_utilizador_decidir_que_o_programa_ira_executar",
	"linguagens" : "por"
}
```
####Dica para obter a diretoria correcta: 
```sh
$ pwd
```
####Exemplo:
```sh
/home/carpinteiro/xpto
```

####Execução:
```sh
$ cd /home/carpinteiro/xpto
$ python legopens.py
```

##José Carpinteiro 

###Universidade de Évora



[Imdb]:http://www.omdbapi.com/
[OpenSubtitles]:http://trac.opensubtitles.org/projects/opensubtitles/wiki/XMLRPC
