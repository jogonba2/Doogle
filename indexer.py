#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: Jose & Alberto #

from sys import argv,stdin
try: import cPickle as pickle
except: import pickle
from postings_operations import postings_operations 
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from re import sub,findall
from time import time

STOPWORDS = [x for x in stopwords.words('spanish')]
STEMMER   = SnowballStemmer("spanish")

# USAGE #
def usage(): print """Usage: python retrieval.py fichero_indice opciones\n
    -> fichero_indice: Indica el fichero de donde se cargará el indice
    -> opciones: Indica si no se hara nada (0), stopwords (1), stemming(2) o los 2 (3)\n"""

def load_object(source):
	with open(source,'rb') as fd:
		obj = pickle.load(fd)
	return obj
	# obj = (doc-hash,noticia-term,notice-title-index,notice-date-index,notice-category-index,notice-hash) #
	# index[0] -> doc-hash: identificador doc - nombre de documento (relacion numero de dcumento con su fichero) #
	# index[1] -> noticia-term: termino-(docID,posID) (sobre el texto de la noticia) #
	# index[2] -> notice-title-index: lo mismo pero solo en el titulo #
	# index[3] -> notice-date-index: lo mimso pero con fecha #
	# index[4] -> notice-category-index: lo mismo pero sobre categoria #
	# index[5] -> notice-hash: buscas posicion de noticia- informacion asociada (titulo,...) #
	# index[6] -> notice-text: texto de la noticia #
	
def take_posting_list(term, search,index):
	obj = []
	try:
		if(search   == "text" or search == ""): obj = index[1][term]
		elif(search == "headline"): obj = index[2][term]
		elif(search == "date"): obj = index[3][term]
		elif(search == "category"): obj = index[4][term]
	except KeyError as ke: return []
	finally: return obj
	
# Eliminar stopwords de la query#
def remove_stopwords(text, language='spanish'): return [w for w in text if w.lower() not in STOPWORDS]

# Hacer stemming a cada palabra de la query #
def make_stemming(text,stemmer): return [stemmer.stem(word) for word in text if word!="headline" and word!="date"]

#Comprobar si la query tiene todas las operaciones necesarias, y devolver la query correspondiente #
def correct_operations(query):
	query_op, term1,term2 = [query.pop(0)],"",""
	while(not query == []):
		term1= query.pop(0)
		aux = query_op[-1]
		if(aux=="and" or aux=="or" and term1=="not"): query_op.append(term1)
		elif(aux=="not"): query_op.append(term1)
		elif(aux=="headline" or aux=="text" or aux=="category" or aux=="date"): query_op.append(term1)
		elif(term1=="and" or term1=="or" and not aux=="and" and not aux=="or" and not aux=="not"): query_op.append(term1)
		else:
			query_op.append("and")
			query_op.append(term1)
	return query_op
	
#Comprobar si la query está correctamente formada, y devolver la query correcta #
def take_correct_query(query):
	query_correct,term1,term2 = [],"",""
	while(not query==[]):
		term1 = query.pop(0)
		if(not query==[] and term1=="headline" or term1=="text" or term1=="category" or term1=="date"):
			term2 = query.pop(0)
			if(term2=="and" or term2=="or"):
				if(not query==[] and query[0]=="not"): query.pop(0)
			else: 
				query_correct.append(term1+":"+term2)
				if(not query==[]):query_correct.append(query.pop(0))
				if(not query==[] and query[0]=="not"): query_correct.append(query.pop(0))
		elif(term1=="and" or term1=="or"):
			if(query_correct[-1]== "and" or query_correct=="or"):
				if(not query==[] and query[0]!="and" and query[0]!="or"): query_correct.append(query.pop(0))
				else: query.pop(0)
		else: 
			query_correct.append(term1)
			if(not query==[]):query_correct.append(query.pop(0))
			if(not query==[] and query[0]=="not"): query_correct.append(query.pop(0))
	return query_correct
	
def show_results(posting_list_result,index,query_terms,query_time):
	# Si no hay resultados, mostrar mensaje de no resultados #
	if len(posting_list_result)==0:
		print "[-] There aren't results for terms: ",query_terms
		
	# Si solo hay una o 2 noticias relevantes, mostrar el título y el cuerpo de la noticia #
	elif len(posting_list_result) in range(1,3):
		for noticeid in posting_list_result: print index[5][noticeid[1]][0][1],"\n",index[6][noticeid],"\n\n"
								
	# Si hay entre 3 y 5 noticias relevantes, mostrar el título y un snippet del cuerpo que contenga los términos #
	elif len(posting_list_result) in range(3,7):
		context= 5
		for noticeid in posting_list_result:
			notice_title = index[5][noticeid[1]][0][1]
			print notice_title,"\n"
			notice_text = index[6][noticeid]
			notice_text = findall(r"[\w']+",notice_text)
			max_pos,min_pos = 0,float('inf')
			for term in query_terms:
				try:
					term_pos = notice_text.index(term)
					if term_pos > max_pos: max_pos = term_pos
					if term_pos < min_pos: min_pos = term_pos
				except ValueError as ve: print ve
				
			left_context  = min_pos-context if min_pos-context>=0 else 0
			right_context = max_pos+context
			print " ".join(notice_text[left_context:right_context])+"\n\n"
									
	# Si hay más de 5 noticias relevantes, mostrar el título de las 10 primeras #
	else:
		c = 0
		for noticeid in posting_list_result:
			if c>10: break;
			print index[5][noticeid[1]][0][1] # Mostrar titulo	
			c += 1
	print len(posting_list_result),"results in",query_time,"ms\n"
# Extrae los terminos de la consulta #
def extract_query_terms(query):
	terms = []
	for term in query.split(" "):
		if ":" not in term:
			if term not in ["and","or","not"]: terms.append(term)
		else: terms.append(term.split(":")[1])
	return terms

# Elimina caracteres no alfanumericos #
def delete_non_alphanumeric(text): return sub(u"[^\wáéíóúñçàèìòù]",u" ",text)

def retriever(index_file, deleting):
	query,term1,term2,op,posting_list_result,posting_list_aux,search1,search2 = None,"","","",[],[],"",""
	index = load_object(index_file)	
	while(True):
		query = delete_non_alphanumeric(raw_input("What are you looking for? -> ").replace(":"," ").lower().decode("utf-8")).split(" ")		
		print "\n"
		init_time = time()		
		query = correct_operations(query)
		print "Correct query:",query
		if(deleting   == 1): query = remove_stopwords(query)
		elif(deleting == 2): query = make_stemming(query, STEMMER)
		elif(deleting == 3): query = make_stemming(remove_stopwords(query), STEMMER)
		if(query==['']): print "[-] You are looking for nothing.\n"; break
		query = take_correct_query(query)
		print "Processed query:",query		
		query_terms = extract_query_terms(" ".join(query))
		if query==[]: print "[-] Words removed because they are stopwords, run another query.\n" ; continue			
		term1 = query.pop(0)
		if(":" in term1): 
			search1 = term1.split(":")[0]
			term1 = term1.split(":")[1]
		else: search1 = "text"
		posting_list_result = take_posting_list(term1,search1,index)
		while(not query == []):			
			op = query.pop(0);
			if(query[0]=="not"): op += query.pop(0)
			term2 = query.pop(0)
			if(":" in term2): 
				search2 = term2.split(":")[0]
				term2 = term2.split(":")[1]
			else : search2 = "text"
			posting_list_aux = take_posting_list(term2,search2,index)
			posting_list_result = postings_operations._parse_operation(op,posting_list_result, posting_list_aux)
		end_time = time()
		show_results(posting_list_result,index,query_terms,(end_time-init_time))

# Entry point #
if __name__ == "__main__":
	if len(argv)<3 or int(argv[2]) not in [0,1,2,3]: usage(); exit()
	retriever(argv[1],int(argv[2]))
