#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 17:42:34 2018

@author: shrey
"""

import argparse
from stanfordcorenlp import StanfordCoreNLP
import json

def get_args():
    parser = argparse.ArgumentParser(description='NER module')
    parser.add_argument('--sentence', metavar='SENTENCE', dest='sentence', \
                        help='sentence for NER', required=True, default='unk')
    
    parser.add_argument('--host', metavar='HOST', dest='host', \
                        help='host for stanford core nlp', required=True, default='unk')
    parser.add_argument('--port', metavar='PORT', dest='port', \
                        help='port for stanford core nlp', required=True, default='unk')

    args = parser.parse_args()
    return args


args = get_args()
nlp = StanfordCoreNLP(args.host, port=int(args.port))
sentence = args.sentence


def ners(sentence, nlp):
    sentence_ner = nlp.ner(sentence + ' dummy')
    to_replace_ners = []
    org = ''
    kind = ''
    for (i, j) in sentence_ner: #i = NCSU, j = ORGANISATION; i = bent, j = 0
        if(j == 'O'):
            if org != '': 
                to_replace_ners.append((org[1:], kind))
                org = ''
            else:
                pass
        else:
            org = org + "_" + i
            kind = j
    #print (sentence_ner)   
    print (json.dumps(to_replace_ners))
    
ners(sentence, nlp)
nlp.close()