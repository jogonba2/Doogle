#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: Jose & Alberto #

from glob import glob
from sys import argv
from re import sub,findall,match,compile,DOTALL
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
try: from cPickle import dump,HIGHEST_PROTOCOL
except: from pickle import dump,HIGHEST_PROTOCOL


# USAGE #
def usage(): print """Usage: python indexer.py directorio fichero_indice stopwords stemming\n
\t-> directorio: Indica el directorio de los documentos\n\t-> fichero_indice: Indica el fichero donde se salvara el indice
\t-> stopwords: Indica si se eliminaran stopwords [SI\NO]\n\t-> stemming: Indica si se realizara stemming [SI\NO]\n
-> Las opciones stopwords y stemming incrementaran el coste temporal de la indexacion\n
"""

# Elimina caracteres no alfanumericos #
def delete_non_alphanumeric(text): return sub("\W"," ",text)

# Extrae los terminos del texto, cortando por \t, \n y espacios "
def term_extractor(text,stopwords,stemming): 
	l = process_list(findall(r"[\w']+",text))
	if stopwords == 1:  l = remove_stopwords(l)
	if stemming  == 1:  l = make_stemming(l,SnowballStemmer("spanish"))
	return l
	
# Eliminar caracteres nulos y pasa a minusculas los terminos de la lista #
def process_list(l): return [term.lower() for term in l if term!=""]

# Extrae la lista de noticias para un documento dado #
def extract_notices(doc): return doc.split("<DOC>")

# Dada una noticia notice, extrae la informacion data requerida #
def extract_notice_data(notice,data): return match(compile(".*<"+data+">(.*)</"+data+">.*",DOTALL),notice).group(1)

# Anyade cada termino term de la lista l al diccionario d dado y su identificador de noticia#
def add_to_dict(d,l,ident):
	for term in l: 
		if term not in d: d[term] = [ident] 
		else: d[term].append(ident)
	return d
	
# Eliminar stopwords #
def remove_stopwords(text, language='spanish'): return [w for w in text if w.lower() not in stopwords.words(language)]

# Hacer stemming a cada palabra de la lista l #
def make_stemming(text,stemmer): return [stemmer.stem(word) for word in text]

# Guarda un objeto serializado en el fichero dest #
def save_object(object,dest): 
	with open(dest,'wb') as fd: dump(object,fd,HIGHEST_PROTOCOL)
	
def indexer(path,index_file,stopwords,stemming):
	doc_hash     		  = {}
	notice_hash	 		  = {}
	notice_terms_index    = {}
	notice_title_index    = {}
	notice_date_index     = {}
	notice_category_index = {}
	docs  			      = glob(path+"/*.sgml")
	docid 				  = 0
	posid 				  = 0
	stopwords = 1 if stopwords == "si" else 0
	stemming  = 1 if stemming  == "si" else 0
	for doc_file in docs:
		with open(doc_file,"r") as fd: doc = fd.read()
		doc_hash[docid]           = doc_file ;
		notices 			      = extract_notices(doc)[1:]
		for notice in notices:
			notice_title    	  = extract_notice_data(notice,"TITLE")
			notice_date    		  = extract_notice_data(notice,"DATE")
			notice_category 	  = extract_notice_data(notice,"CATEGORY")
			notice_text     	  = extract_notice_data(notice,"TEXT")
			notice_text_terms     = term_extractor(delete_non_alphanumeric(notice_text),stopwords,stemming)
			notice_title_terms    = term_extractor(delete_non_alphanumeric(notice_title),stopwords,stemming)
			notice_date_terms     = term_extractor(delete_non_alphanumeric(notice_date),stopwords,stemming)
			notice_category_terms = term_extractor(delete_non_alphanumeric(notice_category),stopwords,stemming)
			notice_terms_index    = add_to_dict(notice_terms_index,notice_text_terms,(docid,posid))
			notice_title_index    = add_to_dict(notice_title_index,notice_title_terms,(docid,posid))
			notice_date_index     = add_to_dict(notice_date_index,notice_date_terms,(docid,posid))
			notice_category_index = add_to_dict(notice_category_index,notice_category_terms,(docid,posid))
			notice_hash           = add_to_dict(notice_hash,[posid],(docid,notice_title,notice_date,notice_category))
			posid += 1
		docid += 1
	save_object((doc_hash,notice_terms_index,notice_title_index,notice_date_index,notice_category_index,notice_hash),index_file)
		
# Entry point #
if __name__ == "__main__":
	if len(argv)<5 or argv[3].lower() not in ["si","no"] or argv[4].lower() not in ["si","no"]: usage(); exit()
	indexer(argv[1],argv[2],argv[3].lower(),argv[4].lower())
