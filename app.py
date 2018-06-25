from flask import Flask, render_template, json, request, redirect, url_for
app = Flask(__name__)

#Importing configuration
import configparser
config = configparser.ConfigParser()
config.read("config.txt")

word2vec_path = config.get("configuration","word2vec_path")
stanford_corenlp_path = config.get("configuration","stanford_corenlp_path")


import pymysql
pymysql.install_as_MySQLdb()

# Connect
mydbhost = config.get("configuration","mydbhost")
mydbuser = config.get("configuration","mydbuser")
mydbpasswd = config.get("configuration","mydbpasswd")
mydbdb = config.get("configuration","mydbdb")

# importing StandfordCoreNLP to tokenize, tag, and ner
from stanfordcorenlp import StanfordCoreNLP
# Tree syntax of natural language: http://www.cs.cornell.edu/courses/cs474/2004fa/lec1.pdf

# Importing word2vec to find similarity and neighboring words
import gensim
from gensim.models import Word2Vec

model = gensim.models.KeyedVectors.load_word2vec_format(word2vec_path, binary=True, limit=500000) 

@app.route("/")
def main():
  return render_template('index.html')

@app.route('/explore',methods=['POST'])
def explore():

    nlp = StanfordCoreNLP(stanford_corenlp_path)

    # read the posted values from the UI
    statement = request.form['inputStatement']

    sentence_tokens = nlp.word_tokenize(statement)
    sentence_tags = nlp.pos_tag(statement)
    sentence_ner = nlp.ner(statement)
    # sentence_parse = nlp.parse(statement)
    # sentence_dependency = nlp.dependency_parse(statement)

    to_replace_ners = []
    to_replace_verbs = []
    to_replace_verbphrases = []
    to_replace_adjectives = []
    to_replace_adjphrase = []

    for (i, j) in sentence_ner: 
      if(j != 'O'): 
        to_replace_ners.append((i, j))

    verb_check = 0
    adj_check = 0

    for (i, j) in sentence_tags: 
      if(verb_check == 1):
        verbphrase = verb + '_' + i
        to_replace_verbphrases.append((verbphrase, i))
        verb_check = 0 

      if(j == 'VBD' or j=='VBZ' or j == 'VBP' or j == 'VBN'):
        to_replace_verbs.append(i)
        adj = j
        adj_check = 1

    nlp.close()

    topk = 10
    replacement_ners = []
    replacement_verbs = []
    replacement_verbphrases = []
    replacement_nouns = []
    replacement_adjectives = []
    
    for (i, j) in to_replace_ners:
        try:
            similar_ners = model.most_similar([i, j.lower()], [], topk)
            replacement_ners.append((i, similar_ners))
        except KeyError as e:
            print(e)
    
    print(replacement_ners)
        
    for verb in to_replace_verbs:
        try: 
            similar_verbs = model.most_similar(verb, [], topk)
            replacement_verbs.append((verb,similar_verbs))
        except KeyError as e:
            print(e)
 
    print(replacement_verbs)
    
    for (verbphrase, nn) in to_replace_verbphrases:
        try:
            similar_verbphrases = model.most_similar([verbphrase, nn], [], topk)
            replacement_verbphrases.append((verbphrase, similar_verbphrases))
        except KeyError as e:
            print(e)
    
    print(replacement_verbphrases)
    
    for (verbphrase, nn) in to_replace_verbphrases:
        try:
            similar_nouns = model.most_similar(nn, [], topk)
            replacement_nouns.append((nn, similar_nouns))
        except KeyError as e:
            print(e)
    
    print(replacement_nouns)
    
    for adjective in to_replace_adjectives: 
        try: 
            similar_adjectives = model.most_similar(adjective, [], topk)
            replacement_adjectives.append((adjective, similar_adjectives))
        except KeyError as e:
            print(e)
        
    print(replacement_adjectives)
    
    return render_template('explore.html', statement = statement, replacement_ners = replacement_ners, replacement_verbs = replacement_verbs, replacement_nouns = replacement_nouns, replacement_adjectives = replacement_adjectives)
    #return redirect(url_for('main', statement = _statement))
 
    # validate the received values
    # if _statement:
        # return json.dumps({'html':'<span>All fields good !!</span>'})
    # else:
        # return json.dumps({'html':'<span>Enter the required fields</span>'})
		
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=80) 

