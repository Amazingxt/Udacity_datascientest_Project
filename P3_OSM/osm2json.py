#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
import pprint
import re
import json
import codecs
from itertools import chain
from collections import defaultdict, Counter

filename = 'barcelona_spain.osm' # Choice barcelona in Spain

def count_tags(filename):
    ''' 
    Use the iterative parsing to process the map file and 
    find out not only what tags are there, but also how many.
    '''
    tags = {}
    context = ET.iterparse(filename)
    for event,elem in context:
        if elem.tag not in tags:
            tags[elem.tag] = 1
        else:
            tags[elem.tag] += 1

    return tags

# Check the "k" value for each "<tag>" 
# and see if there are any potential problems
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def key_type(element, keys):
    if element.tag == "tag":
        if element.get("k") is None:
            pass
        elif lower.match(element.get("k")):
            keys["lower"] += 1
        elif lower_colon.match(element.get("k")):
            keys["lower_colon"] += 1
        elif problemchars.match(element.get("k")):
            keys["problemchars"] += 1
        else:
            keys["other"] += 1
        
    return keys

def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys, element

_, element = process_map(filename)
street_type_re = re.compile(r'^\b\S+\.?', re.IGNORECASE)
expected = ["Carrer", "Avinguda", "Sant", "Drive", "Court", "Place", "Square", "Lane", "Road", 
             "Trail", "Parkway", "Commons"]
# UPDATE THIS VARIABLE
mapping = {"Avda":"Avenida",
            "Avda.":"Avenida",
            "Av.":"Avenida",
            "Ave.":"Avenida",
            "Torent":"Torrent",
            "C":"Carrer",
            "C.":"Carrer",
            "C./":"Carrer",
            "C/":"Carrer",
            "Calle":"Carrer",
            "C/Sant":"Carrer",
            "C/Torrassa":"Carrer",
            "Caller":"Carrer",
            "Camí":"Camino",
            "Cami":"Camino",
            "Camp":"Campus",
            "Carretera":"Ctra",
            "Carre":"Carrer",
            "Carrar":"Carrer",
            "Carrier":"Carrer",
            "Cl":"Carrer Del",
            "Cr":"Carrer",
            "Crta":"Ctra",
            "Ctra.":"Ctra",
            "De":"Del",
            "Dels":"Del",
            "Dr.":"Doctor",
            "Passadís":"Passatge",
            "Paseo":"Passeig",
            "Pg":"Passeig",
            "Pg.":"Passeig",
            "Pl":"Placa",
            "Pla":"Placa",
            "Pl,":"Placa",
            "Pº":"Paseo",
            "Ramble":"Rambla",
            "Viaducte":"Viaducto"
            }

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name) 


def is_street_name(element):
    return (element.attrib['k'] == "addr:street")


words_of_street = []
def audit(filename):
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(filename, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):     
                    # Capital the first letter of every word              
                    audit_street_type(street_types, tag.attrib['v'].title()) 

                    tag = tag.attrib['v'].title().split()
                    words_of_street.append(tag)
    return street_types


def update_name(name, mapping):

    name = name.split()
    for i,j in enumerate(name):
        if j in mapping:
            name[i] = mapping[j]
    name = " ".join(name)
            
    return name

# def clean_name(element):
# 	if element.tag == "node" or element.tag == "way":
# 		for tag in element.iter("tag"):
# 			if is_street_name(tag):
# 				tag.attrib['v'] = update_name(tag.attrib['v'].title())

# cleanname = clean_name(element)								

st_types = audit(filename)
#pprint.pprint(dict(st_types))

def make_wordcloud(words_of_street):
    '''
    Make wordcloud of tag['v'] by the tag['k'] = 'addr:street'
    ''' 
    from wordcloud import WordCloud
    from os import path
    d = path.dirname(__file__)

    word_of_street = list(chain(*words_of_street))
    count = Counter(word_of_street)
    street_wordcloud = WordCloud().generate_from_frequencies (dict(count))
    street_wordcloud.to_file(path.join(d, "streetmapfreq.jpg"))

mwc = make_wordcloud(words_of_street)


CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        node["type"] = element.tag
        created = {}
        addres = {}
        nd = []
        ref = 0
        ad = 0
        pos = 0
        ADDRES = ["city", "housenumber","postcode","street"]
        for attr in element.attrib:
            if attr in CREATED:
                created[attr] = element.get(attr)
            elif attr == "lat":
                pos += 1
                lat = float(element.get(attr))
            elif attr == "lon":
                pos += 1
                lon = float(element.get(attr))
            else :
                node[attr] = element.get(attr)
        for tag in element.iter("nd"):
            ref += 1
            nd.append(tag.get("ref"))
        for tag in element.iter("tag"):
            if problemchars.match(tag.get("k")):
                pass
            elif lower_colon.match(tag.get("k")):
                
                #addres[tag.get("k").split(":")[1]] = tag.get("v")
                if tag.get("k").split(":")[1] in ADDRES:
                    ad += 1 # note if there is information about address
                    if tag.get("k").split(":")[1] == "street":
                        addres["street"] = update_name(tag.get("v"), mapping)
                    else:
                        addres[tag.get("k").split(":")[1]] = tag.get("v")
                
            elif lower.match(tag.get("k")):
                node[tag.get("k")] = tag.get("v")
            else:
                pass
       
        node["created"] = created
        if ad:
            node["address"] = addres
        if pos:
            node["pos"] = [lat,lon]
        if ref:
            node["node_refs"] = nd
        return node
    else:
        return None


def generate_json(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in.split(".")[0])
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

data = generate_json(filename)
pprint.pprint(data[1200000:1200005])
            
                


#tags = count_tags(filename)
#pprint.pprint(tags)
# keys = process_map(filename)
# pprint.pprint(keys)
    



    

