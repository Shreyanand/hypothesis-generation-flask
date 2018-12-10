#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  9 16:36:40 2018

@author: Shrey
"""

import argparse
from stanfordcorenlp import StanfordCoreNLP
import json
import gensim

def get_args():
    parser = argparse.ArgumentParser(description='W2V module')
    parser.add_argument('--replace', metavar='REPLACE', dest='replace', \
                        help='replace with  W2V alternatives', required=True, default='unk')
    
    parser.add_argument('--host', metavar='HOST', dest='host', \
                        help='host for stanford core nlp', required=True, default='unk')
    parser.add_argument('--port', metavar='PORT', dest='port', \
                        help='port for stanford core nlp', required=True, default='unk')
    
    parser.add_argument('--w2vpath', metavar='PATH', dest='w2vpath', \
                        help='path for w2v training data', required=True, default='unk')

    args = parser.parse_args()
    return args



def w2v_similar(to_replace_ners, to_replace_verbs, to_replace_verbphrases,
    to_replace_adjectives, to_replace_adjphrases,
    to_replace_nouns, to_replace_nounphrases,  model):
    
    ## These are using W2V, currently used.
    topk = 10
    replacement_ners = []
    replacement_verbs = []
    replacement_verbphrases = []
    replacement_nouns = []
    replacement_nounphrases = []
    replacement_adjectives = []
    replacement_adjphrases = []
    
    for (i, j) in to_replace_ners:
        try:
            similar_ners = model.most_similar([i, j.lower()], [], topk)
            senti_ners = []
            for (similar_ner, score) in similar_ners:
                senti_ners.append([similar_ner, score, 0])
            replacement_ners.append((i, senti_ners))
        except KeyError as e:
            pass
            #print(e)
        
        ## Use W2V for replacing nouns, verbs, adj verbphrases, nounphrases, and adj phrases
    
    for verb in to_replace_verbs:
        try: 
            similar_verbs = model.most_similar(verb, [], topk)
            senti_verbs = [[i, j, 0] for (i, j) in similar_verbs]
            replacement_verbs.append((verb, senti_verbs))
        except KeyError as e:
            pass
            #print(e)
            
    for (verbphrase, nn) in to_replace_verbphrases:
        try:
            similar_verbphrases = model.most_similar([verbphrase, nn], [], topk)
            replacement_verbphrases.append((verbphrase, similar_verbphrases))
        except KeyError as e:
            pass
            #print(e)
    
 
    for noun in to_replace_nouns:
        try:
            similar_nouns = model.most_similar(noun, [], topk)
            senti_nouns = [[i, j, 0] for (i, j) in similar_nouns]
            replacement_nouns.append((noun, senti_nouns))
        except KeyError as e:
            pass
            #print(e)
    
    
    
    for (nounphrase, nn) in to_replace_nounphrases:
        try:
            similar_nounphrases = model.most_similar([nounphrase, nn], [], topk)
            replacement_nounphrases.append((nounphrase, similar_nounphrases))
        except KeyError as e:
            pass
            #print(e)
    
    
    
    for adjective in to_replace_adjectives: 
        try: 
            similar_adjectives = model.most_similar(adjective, [], topk)
            senti_adjectives = [[i, j, 0] for (i, j) in similar_adjectives]
            replacement_adjectives.append((adjective, senti_adjectives))
        except KeyError as e:
            pass
            #print(e)
        
    
    
    for (adjphrase, nn) in to_replace_adjphrases:
        try:
            similar_adjphrases = model.most_similar([adjphrase, nn], [], topk)
            replacement_adjphrases.append((adjphrase, similar_adjphrases))
        except KeyError as e:
            pass
            #print(e)
    
    
    
    print (replacement_ners,
            replacement_verbs,
            replacement_verbphrases,
            replacement_nouns,
            replacement_nounphrases,
            replacement_adjectives,
            replacement_adjphrases)
    
    
if __name__ == "__main__":
    args = get_args()
    replace = json.loads(args.replace)   ##a ='--replace \'' + json.dumps([NER] + POS) +  '\' --host "http://localhost" --port 9000'
    to_replace_ners = replace[0]
    to_replace_verbs = replace[1]
    to_replace_verbphrases = replace[2]
    to_replace_adjectives = replace[3]
    to_replace_adjphrases = replace[4]
    to_replace_nouns = replace[5]
    to_replace_nounphrases = replace[6]
    word2vec_path = args.w2vpath
    model = gensim.models.KeyedVectors.load_word2vec_format(word2vec_path, binary=True, limit=500000) 
    print("model ready")
    w2v_similar(to_replace_ners,
                to_replace_verbs,
                to_replace_verbphrases,
                to_replace_adjectives,
                to_replace_adjphrases,
                to_replace_nouns,
                to_replace_nounphrases, model)
    