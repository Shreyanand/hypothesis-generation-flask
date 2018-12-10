#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  9 16:12:52 2018

@author: root
"""

import argparse
from stanfordcorenlp import StanfordCoreNLP
import json

def get_args():
    parser = argparse.ArgumentParser(description='Sentiment module')
    parser.add_argument('--sentence', metavar='SENTENCE', dest='sentence', \
                        help='sentence for sentiment analysis', required=True, default='unk')
    
    parser.add_argument('--host', metavar='HOST', dest='host', \
                        help='host for stanford core nlp', required=True, default='unk')
    parser.add_argument('--port', metavar='PORT', dest='port', \
                        help='port for stanford core nlp', required=True, default='unk')

    args = parser.parse_args()
    return args

def sentiments(word, nlp):
    """ This function calls Stanford Core Nlp's sentiment annotator
    
        Args:
            word (String): The input word or sentence for setiment detection
            nlp (StanfordCoreNLP): Core nlp instance for sentiment detection
        Returns:
            String : Sentiment value: Very negative; Negative; Neutral; 
            postive; Very positive
    """
    try:
        sjson = nlp.annotate(word,properties={'annotators': 'sentiment','outputFormat': 'json','timeout': 1000})
        res = json.loads(sjson)
        sval = res["sentences"][0]["sentiment"]
        print(json.dumps(sval))
    except json.decoder.JSONDecodeError as e:
        print (e)
        
if __name__ == "__main__":
    args = get_args()
    nlp = StanfordCoreNLP(args.host, port=int(args.port))
    sentence = args.sentence
    sentiments(sentence, nlp)