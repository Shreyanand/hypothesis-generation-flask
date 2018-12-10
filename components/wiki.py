#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  9 22:02:17 2018

@author: Shrey
"""

import argparse
import json
import pymysql
import configparser


def get_args():
    parser = argparse.ArgumentParser(description='wiki module')
    parser.add_argument('--replace', metavar='REPLACE', dest='replace', \
                        help='replace with  W2V alternatives', required=True, default='unk')
    
    parser.add_argument('--host', metavar='HOST', dest='host', \
                        help='host for stanford core nlp', required=True, default='unk')
    parser.add_argument('--port', metavar='PORT', dest='port', \
                        help='port for stanford core nlp', required=True, default='unk')
    
    parser.add_argument('--configpath', metavar='PATH', dest='configpath', \
                        help='path for database config file', required=True, default='unk')

    args = parser.parse_args()
    return args


def wiki_ontology(to_replace_ners):
    ner_categories = []
    
    for ner in to_replace_ners:
        connection = pymysql.connect(host=mydbhost, user=mydbuser, passwd=mydbpasswd, db=mydbdb)
        ne = ner[0]
        try:
            with connection.cursor() as cursor:
                query = "SELECT instance, class FROM simple_types where instance like CONCAT('%', '"+ ne + "' ,'%')"
                cursor.execute(query)
                #numrows = cursor.rowcount
                rep = []
                for x in range(0, 10): #top 10 results from wikicat
                    row = cursor.fetchone()
                    if row:
                        supernym = row[1][9:-1].replace('_', ' ')
                        rep.append([supernym, 0, 0])
                if rep:
                    ner_categories.append((ne.replace('_', ' '), rep))
        finally:
          connection.close()
                    
    print (ner_categories)


if __name__ == "__main__":
    args = get_args()
    replace = json.loads(args.replace)   ##a ='--replace \'' + json.dumps(NER) +  '\' --host "http://localhost" --port 9000 --configpath "/Users/shrey/hypothesis-generation-flask/config.txt" '
    to_replace_ners = replace
    configpath = args.configpath
    config = configparser.ConfigParser()
    config.read(configpath)
    mydbhost = config.get("configuration","mydbhost")
    mydbuser = config.get("configuration","mydbuser")
    mydbpasswd = config.get("configuration","mydbpasswd")
    mydbdb = config.get("configuration","mydbdb")
    wiki_ontology(to_replace_ners)
