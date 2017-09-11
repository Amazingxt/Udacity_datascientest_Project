#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pprint

def get_db():

	from pymongo import MongoClient
	client = MongoClient("localhost:27017")
	db = client.map_of_spain
	return db

def in_query():
	"""
	query what you want to know by structure sentence like:
	query = {"manufacturer":"Ford Motor Company","assembly":{"$in":['England','Manchester']}}
	return query(every document) or query_count(count of document).
	"""

	# initialise query and query_count
	query = {}
	query_count = {}

	# # count numbers of nodes and ways 
	# query_count = {"type":"node"}
	# query_count = {"type":"way"}

	# numbers of specially appointed nodes
	query_count = {#"shop":{"$exists":1},
				   #"atm" :{"$exists":1},
				   #"firehydrant":{"$exists":1},
				   #"public_transport":{"$exists":1},
				   "phone":{"$exists":1}				   
				   }
	return query, query_count

def make_pipeline():


	pipeline = [#{"$group":{"_id":"$natural","nums":{"$sum":1}}}
			     {"$unwind":"$address"},
			     {"$project":{postcode:1}}
			   ]
	return pipeline

def tweet_sources(db, pipeline):

	return [doc for doc in db.barcelona.aggregate(pipeline)]

def phone_clean(db):
	"""
	clean phone_numbers to format just like '934417526'
	"""
	documents = db.barcelona.find({"phone":{"$exists":1}})
	for document in documents:
		phone = document["phone"]
		if "(" in phone:
			phone = phone.replace("(", "")
			phone = phone.replace(")", "")
		if "+34" in phone:
			phone = phone.replace("+34", "")
		if phone[:2] == "34":
			phone = phone.replace("34", "")
		if "-" in phone:
			phone = phone.replace("-", "")
		if "+" in phone:
			phone = phone.replace("+", "")
		phone = "".join(phone.split())
		if "." in phone:
			phone = "".join(phone.split("."))
		db.barcelona.update({"phone":document["phone"]},{"$set":{"phone":phone}})


def get_result():

	db = get_db()
	query, query_count = in_query()
	# result = db.barcelona.find(query)
	result = 1
	result_count = db.barcelona.find(query_count)
	result_aggr = 1
	#pipeline = make_pipeline()
	#result_aggr = tweet_sources(db, pipeline)

	return result, result_count, result_aggr

db = get_db()
phone_clean = phone_clean(db)
result, result_count, result_aggr = get_result()
#print(result, result_count, result_aggr)
for i in result_count:
	pprint.pprint(i["phone"])