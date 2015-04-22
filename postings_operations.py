#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: Jose & Alberto #

class postings_operations:
	
	@staticmethod
	def _intersection(l1,l2): return list(set(l1).intersection(set(l2)))
	
	@staticmethod
	def _union(l1,l2): return list(set(l1).union(set(l2)))
	
	@staticmethod
	def _not_intersection(l1,l2): return list(set(l1).difference(set(l2)))				
	
	@staticmethod
	def _parse_operation(op,l1,l2):
		if   op=="andnot": return postings_operations._not_intersection(l1,l2)
		elif op=="and":	   return postings_operations._intersection(l1,l2)
		else:			   return postings_operations._union(l1,l2)	
