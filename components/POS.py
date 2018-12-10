#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  9 15:18:56 2018

@author: Shrey
"""

import argparse
from stanfordcorenlp import StanfordCoreNLP
import json

def get_args():
    parser = argparse.ArgumentParser(description='POS module')
    parser.add_argument('--sentence', metavar='SENTENCE', dest='sentence', \
                        help='sentence for POS', required=True, default='unk')
    
    parser.add_argument('--host', metavar='HOST', dest='host', \
                        help='host for stanford core nlp', required=True, default='unk')
    parser.add_argument('--port', metavar='PORT', dest='port', \
                        help='port for stanford core nlp', required=True, default='unk')

    args = parser.parse_args()
    return args

def pos_tags(statement, nlp):
    
    sentence_tags = nlp.pos_tag(statement)
    
    to_replace_verbs = []
    to_replace_verbphrases = []
    to_replace_adjectives = []
    to_replace_adjphrases = []
    to_replace_nouns = []
    to_replace_nounphrases = []
    
    verb_check = 0
    noun_check = 0
    adj_check = 0

    for (i, j) in sentence_tags: # Here verb checks are activated after a verb is discovered, so pair of verbs as verbphrases? Check Logic.
        
        
      if(verb_check == 1):
        verbphrase = verb + '_' + i
        to_replace_verbphrases.append((verbphrase, i))
        verb_check = 0 

      if(noun_check == 1):
        nounphrase = noun + '_' + i
        to_replace_nounphrases.append((nounphrase, i))
        noun_check = 0 

      if(adj_check == 1):
        adjphrase = adj + '_' + i
        to_replace_adjphrases.append((adjphrase, i))
        adj_check = 0 

      if(j == 'VBD' or j=='VBZ' or j == 'VBP' or j == 'VBN' or j == 'VBG' or j == 'VB'):
        to_replace_verbs.append(i)
        verb = i
        verb_check = 1

      if(j == 'NN' or j=='NNS' or j == 'NNP' or j == 'NNPS'):
        to_replace_nouns.append(i)
        noun = i
        noun_check = 1

      if(j == 'JJ'):
        to_replace_adjectives.append(i)
        adj = i
        adj_check = 1
    
    
    print (json.dumps((to_replace_verbs, 
            to_replace_verbphrases,
            to_replace_adjectives,
            to_replace_adjphrases,
            to_replace_nouns,
            to_replace_nounphrases)))
    
    
if __name__ == "__main__":
    args = get_args()
    nlp = StanfordCoreNLP(args.host, port=int(args.port))
    sentence = args.sentence
    pos_tags(sentence, nlp)