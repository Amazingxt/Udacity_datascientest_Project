#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pymongo
from pymongo import MongoClient
import datetime
import pprint
#$ mongod

client = MongoClient('localhost', 27017)

db = client["test-database"]

#collection is just like the tables in relational database.
collection = db["test-collection"]

post = {"author":"Mike",
		"text":"My first bolg post",
		"tags":["mongodb", "python", "pymongo"],
		"date":datetime.datetime.utcnow()}

posts = db.posts
post_id = posts.insert_one(post).inserted_id
print(post_id)
name = db.collection_names(include_system_collections=False)
print(name)
pprint.pprint(posts.find_one())