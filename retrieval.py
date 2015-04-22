#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import argv
try: import cPickle as pickle
except: import pickle
from postings_operations import postings_operations 
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

# Próxima clase -> Hay que eliminar stopwords y hacer stemming si se indica como parámetro #
# Imprimir texto y snippets cuando sea necesario #

# USAGE #
def usage(): print """Usage: python retrieval.py fichero_indice opciones\n
    -> fichero_indice: Indica el fichero de donde se cargará el indice
    -> opciones: Indica si se eliminaran stopwords (0), stemming(1) o los 2 (2)\n"""

def load_object(source):
	with open(source,'rb') as fd:
		obj = pickle.load(fd)
	return obj
	# obj = (doc-hash,noticia-term,notice-title-index,notice-date-index,notice-category-index,notice-hash) #
	# doc-hash: identificador doc - nombre de documento (relacion numero de dcumento con su fichero) #
	# noticia-term: termino-(docID,posID) (sobre el texto de la noticia) #
	# notice-title-index: lo mismo pero solo en el titulo #
	# notice-date-index: lo mimso pero con fecha #
	# notice-category-index: lo mismo pero sobre categoria #
	# notice-hash: buscas posicion de noticia- informacion asociada (titulo,...) #
	
def take_posting_list(term, search,index):
	obj = []
	try:
		if(search == "text" or search == ""): obj = index[1][term]
		elif(search == "headline"): obj = index[2][term]
		elif(search == "date"): obj = index[3][term]
		elif(search == "category"): obj = index[4][term]
	except KeyError as ke: return []
	finally: return obj

def show_results(posting_list_result,index):
	# Si no hay resultados, mostrar mensaje de no resultados #
		if len(posting_list_result)==0:
			print "[-] There aren't results for that search."
		# Si solo hay una o 2 noticias relevantes, mostrar el título y el cuerpo de la noticia #
		elif len(posting_list_result) in range(1,3):
			for noticeid in posting_list_result:
				print index[5][noticeid[1]][0][1] # Mostrar titulo
				# Mostrar cuerpo de la noticia ¿? #
		# Si hay entre 3 y 5 noticias relevantes, mostrar el título y un snippet del cuerpo que contenga los términos #
		elif len(posting_list_result) in range(3,6):
			for noticeid in posting_list_result:
				print index[5][noticeid[1]][0][1] # Mostrar titulo
				# Mostrar snippet de la noticia ¿? #
		# Si hay más de 5 noticias relevantes, mostrar el título de las 10 primeras #
		else:
			c = 0
			for noticeid in posting_list_result:
				if c>10: break;
				print index[5][noticeid[1]][0][1] # Mostrar titulo
				
def retriever(index_file, deleting):
	query,term1,term2,op,posting_list_result,posting_list_aux,search1,search2 = None,"","","",[],[],"",""
	index = load_object(index_file)
	while(True):
		query = raw_input("What are you looking for? -> ").lower().split(" ")
		if(query==['']): print "[-] You are looking for nothing."; break
		term1 = query.pop(0)
		if(":" in term1): 
			search1 = term1.split(":")[0]
			term1 = term1.split(":")[1]
		else: search1 = ""
		posting_list_result = take_posting_list(term1,search1,index)
		while(not query == []):
			op = query.pop(0);
			if(query[0]=="not"): op += query.pop(0)
			term2 = query.pop(0)
			if(":" in term2): 
				search2 = term2.split(":")[0]
				term2 = term2.split(":")[1]
			else : search2 = ""
			posting_list_aux = take_posting_list(term2,search2,index)
			posting_list_result = postings_operations._parse_operation(op,posting_list_result, posting_list_aux)
		show_results(posting_list_result,index)

# Entry point #
if __name__ == "__main__":
	if len(argv)<3 or int(argv[2]) not in [0,1,2]: usage(); exit()
	retriever(argv[1],int(argv[2]))
	#retriever("indexfile2","")
