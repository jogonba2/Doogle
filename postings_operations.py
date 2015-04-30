#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: Jose & Alberto #

class postings_operations:
	
	@staticmethod
	def _intersection(l1,l2): 
		lista,i,j = [],0,0
		while(i<len(l1) and j<len(l2)):
			if (l1[i][1] == l2[j][1]): lista.append(l1[i]); j+=1; i+=1
			elif(l1[i][1] < l2[j][1]): i+=1
			else: j+=1
		return lista
	
	@staticmethod
	def _union(l1,l2): 
		lista,i,j = [],0,0
		while(i<len(l1) and j<len(l2)):
			if (l1[i][1] == l2[j][1]): lista.append(l1[i]); j+=1; i+=1
			elif(l1[i][1] < l2[j][1]): lista.append(l1[i]); i+=1
			else: lista.append(l2[j]); j+=1
		if(i==len(l1)): 
			while(j<len(l2)): lista.append(l2[j]); j+=1
		else: 
			while(i<len(l1)): lista.append(l1[i]);i+=1
		return lista
	
	@staticmethod
	def _not_intersection(l1,l2): 
		lista,i,j = [],0,0
		while(i<len(l1) and j<len(l2)):
			if (l1[i][1] == l2[j][1]): j+=1; i+=1
			elif(l1[i][1] < l2[j][1]): lista.append(l1[i]); i+=1
			else: j+=1
		if(j==len(l2)): 
			while(i<len(l1)): lista.append(l1[i]);i+=1
		return lista			
	
	@staticmethod
	def _parse_operation(op,l1,l2):
		if   op=="andnot": return postings_operations._not_intersection(l1,l2)
		elif op=="and":	   return postings_operations._intersection(l1,l2)
		else:			   return postings_operations._union(l1,l2)	
