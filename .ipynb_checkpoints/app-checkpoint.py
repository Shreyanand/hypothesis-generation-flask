from flask import Flask, render_template, request
app = Flask(__name__)
from nltk.corpus import wordnet
import pymysql
import configparser
from stanfordcorenlp import StanfordCoreNLP
import gensim
import json

config = configparser.ConfigParser()
config.read("config.txt")
word2vec_path = config.get("configuration","word2vec_path")
stanford_corenlp_path = config.get("configuration","stanford_corenlp_path")
print(stanford_corenlp_path)


pymysql.install_as_MySQLdb()
# Connect to DB
mydbhost = config.get("configuration","mydbhost")
mydbuser = config.get("configuration","mydbuser")
mydbpasswd = config.get("configuration","mydbpasswd")
mydbdb = config.get("configuration","mydbdb")

nlp = StanfordCoreNLP(stanford_corenlp_path)
print('Core NLP instance')
# Importing word2vec to find similarity and neighboring words
model = gensim.models.KeyedVectors.load_word2vec_format(word2vec_path, binary=True, limit=500000) 
print('Word 2 Vec model ready')

def sentiments(word, nlp):
    """ This function calls Stanford Core Nlp's sentiment annotator
    
        Args:
            word (String): The input word for setiment detection
            nlp (StanfordCoreNLP): Core nlp instance for sentiment detection
        Returns:
            String : Sentiment value: Very negative; Negative; Neutral; 
            postive; Very positive
    """
    try:
        sjson = nlp.annotate(word,properties={'annotators': 'sentiment','outputFormat': 'json','timeout': 1000})
        res = json.loads(sjson)
        sval = res["sentences"][0]["sentiment"]
        return(sval)
    except json.decoder.JSONDecodeError as e:
        print (e)
        
    


@app.route("/")
def main():
  print('Main Page opened')
  return render_template('index.html')


@app.route('/generate',methods=['POST'])
def generate():
    print("Generating alternatives")
    statement = request.form['stmnt']
    alt = []
    alt_stmnts = []
    for i in request.form:
        if i != "stmnt": 
            opt = request.form.getlist(i)
            for j in opt:
                if i != j:
                    alt.append((i, j))
            
#        statement = statement.replace(i, request.form[i])
#    print (statement)
    from itertools import chain, combinations
    def all_subsets(ss):
        return chain(*map(lambda x: combinations(ss, x), range(0, len(ss)+1)))
    
    asubs = set(all_subsets(alt))
    print(len(asubs)) 
    for subset in asubs:
        nustat = statement
        for i in subset:
            nustat = nustat.replace(i[0],i[1])
        alt_stmnts.append( (nustat, sentiments(nustat, nlp)) ) 
    
    return render_template ('generate.html', 
                       statements = set(alt_stmnts))
    


@app.route('/explore',methods=['POST'])
def explore():
    
    # importing StandfordCoreNLP to tokenize, tag, and ner
    # Tree syntax of natural language: http://www.cs.cornell.edu/courses/cs474/2004fa/lec1.pdf


    # print("In Explore")
    # print("StanfordCoreNLP path:", stanford_corenlp_path)
    

    # read the posted values from the UI
    statement = ''
    print('explore')
    if request.form.get('inputStatement', None):
        statement = request.form['inputStatement']
        print(statement)
    
    
    #sentence_tokens = nlp.word_tokenize(statement)
    sentence_tags = nlp.pos_tag(statement)
    sentence_ner = nlp.ner(statement)
    statement_sentiment = "Sentiment of the query is: " + sentiments(statement, nlp)
    print(statement_sentiment)
    # sentence_parse = nlp.parse(statement)
    # sentence_dependency = nlp.dependency_parse(statement)

    to_replace_ners = []
    to_replace_verbs = []
    to_replace_verbphrases = []
    to_replace_adjectives = []
    to_replace_adjphrases = []
    to_replace_nouns = []
    to_replace_nounphrases = []

    for (i, j) in sentence_ner: 
      if(j != 'O'): #i = NCSU, j = ORGANISATION; i = sent, j = 0
        to_replace_ners.append((i, j))

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

      if(j == 'VBD' or j=='VBZ' or j == 'VBP' or j == 'VBN' or j == 'VBG'):
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


    ## These are using W2V, currently used.
    topk = 10
    replacement_ners = []
    replacement_verbs = []
    replacement_verbphrases = []
    replacement_nouns = []
    replacement_nounphrases = []
    replacement_adjectives = []
    replacement_adjphrases = []
	
    
    ## Connect to Wikipedia Database of instance and class. 
    ## For each ner, find similar ners using W2V and append to replacement_ners
    ## For each similar ner, find it's category from simple types Wikipedia Database
    
    connection = pymysql.connect(host=mydbhost, user=mydbuser, passwd=mydbpasswd, db=mydbdb)
    ner_categories = []
	
    for (i, j) in to_replace_ners:
        try:
            similar_ners = model.most_similar([i, j.lower()], [], topk)
            senti_ners = []
            #nlp = StanfordCoreNLP(stanford_corenlp_path)
            for (similar_ner, score) in similar_ners:
                print(similar_ner)
                senti_ners.append([similar_ner, score, sentiments(similar_ner, nlp)])
                connection = pymysql.connect(host=mydbhost, user=mydbuser, passwd=mydbpasswd, db=mydbdb)
                try:
                  with connection.cursor() as cursor:
#			        # Execute SQL select statement
#                    query = "SELECT instance, class FROM simple_types where instance like CONCAT('%', '"+ similar_ner + "' ,'%')"
#                    cursor.execute(query)
#						
#                    # Get the number of rows in the resultset
#                    numrows = cursor.rowcount
#                    # Get and display one row at a time
#                    for x in range(0, numrows):
#                      row = cursor.fetchone()
#                      print(row[0], "-->", row[1])
#                      ner_categories.append((i, row[1]))
                      pass
                # Close the connection
                finally:
                  # Close connection.
                  connection.close()
            replacement_ners.append((i, senti_ners))
        except KeyError as e:
            print(e)
    
    print("Alternative NERs" + str(replacement_ners))
    
    
    ## Use W2V for replacing nouns, verbs, adj verbphrases, nounphrases, and adj phrases
    
    for verb in to_replace_verbs:
        try: 
            similar_verbs = model.most_similar(verb, [], topk)
            senti_verbs = [[i, j, sentiments(i, nlp)] for (i, j) in similar_verbs]
            replacement_verbs.append((verb, senti_verbs))
        except KeyError as e:
            print(e)
            
    print("Alternative Verbs" +  str(replacement_verbs))
            
    for (verbphrase, nn) in to_replace_verbphrases:
        try:
            similar_verbphrases = model.most_similar([verbphrase, nn], [], topk)
            replacement_verbphrases.append((verbphrase, similar_verbphrases))
        except KeyError as e:
            print(e)
    
    print("Alternative Verb Phrases" + str(replacement_verbphrases))
 
    for noun in to_replace_nouns:
        try:
            similar_nouns = model.most_similar(noun, [], topk)
            senti_nouns = [[i, j, sentiments(i, nlp)] for (i, j) in similar_nouns]
            replacement_nouns.append((noun, senti_nouns))
        except KeyError as e:
            print(e)
    
    print("Alternative Noun" + str(replacement_nouns))
    
    for (nounphrase, nn) in to_replace_nounphrases:
        try:
            similar_nounphrases = model.most_similar([nounphrase, nn], [], topk)
            replacement_nounphrases.append((nounphrase, similar_nounphrases))
        except KeyError as e:
            print(e)
    
    print("Alternative Noun Phrases" + str(replacement_nounphrases))
    
    for adjective in to_replace_adjectives: 
        try: 
            similar_adjectives = model.most_similar(adjective, [], topk)
            senti_adjectives = [[i, j, sentiments(i, nlp)] for (i, j) in similar_adjectives]
            replacement_adjectives.append((adjective, senti_adjectives))
        except KeyError as e:
            print(e)
        
    print("Alternative Adjectives" + str(replacement_adjectives))
    
    for (adjphrase, nn) in to_replace_adjphrases:
        try:
            similar_adjphrases = model.most_similar([adjphrase, nn], [], topk)
            replacement_adjphrases.append((adjphrase, similar_adjphrases))
        except KeyError as e:
            print(e)
    
    print("Alternative Adjectives" + str(replacement_adjphrases))
    
## Experiment with wordnet for replacing verbs, nouns, and adjectives
## Not yet used.
#    replacement_verbs_synonyms = []
#    replacement_verbs_antonyms = []
#    replacement_adjectives_synonyms = []
#    replacement_adjectives_antonyms = []
#    replacement_nouns_synonyms = []
#    replacement_nouns_antonyms = [] 
#    for verb in to_replace_verbs:
#        for syn in wordnet.synsets(verb): 
#            for l in syn.lemmas():
#                replacement_verbs_synonyms.append(l.name())
#                if l.antonyms():
#                    #print('L.Antonyms:', l.antonyms())
#				    #replacement_verbs_antonyms.append(l.antonyms()[0].name())
#                    for m in l.antonyms():
#                        replacement_verbs_antonyms.append(m.name())
#
#    print('Replacement Verb Synonyms', set(replacement_verbs_synonyms))
#    print('Replacement Verb Antonyms', set(replacement_verbs_antonyms))
#
#	
#    for noun in to_replace_nouns:
#        for syn in wordnet.synsets(noun): 
#            for l in syn.lemmas():
#                replacement_nouns_synonyms.append(l.name())
#                if l.antonyms():
#                    #print('L.Antonyms:', l.antonyms())
#                    #replacement_nouns_antonyms.append(l.antonyms()[0].name())
#                    for m in l.antonyms():
#                        replacement_nouns_antonyms.append(m.name())
#					
#    print('Replacement Noun Synonyms', set(replacement_nouns_synonyms))
#    print('Replacement Noun Antonyms', set(replacement_nouns_antonyms))		
#
#	
#    for adjective in to_replace_adjectives:
#        for syn in wordnet.synsets(adjective): 
#            for l in syn.lemmas():
#                replacement_adjectives_synonyms.append(l.name())
#                if l.antonyms():
#                    #print('L.Antonyms:', l.antonyms())
#                    #replacement_adjectives_antonyms.append(l.antonyms()[0].name())
#                    for m in l.antonyms():
#                        replacement_adjectives_antonyms.append(m.name(
#					
#    print('Replacement Adj Synonyms', set(replacement_adjectives_synonyms))
#    print('Replacement Adj Antonyms', set(replacement_adjectives_antonyms))	

#    nlp.close()
    print("Analysis complete")
    return render_template ('explore.html', 
                           statement = statement,
                           statement_sentiment = statement_sentiment,
                           replacement_ners = replacement_ners,
                           replacement_verbs = replacement_verbs,
                           replacement_verbphrases = replacement_verbphrases,
                           replacement_nouns = replacement_nouns,
                           replacement_nounphrases = replacement_nounphrases,
                           replacement_adjectives = replacement_adjectives,
                           replacement_adjphrases = replacement_adjphrases,
                           ner_categories = ner_categories)
    #return redirect(url_for('main', statement = _statement))
 
    # validate the received values
    # if _statement:
        # return json.dumps({'html':'<span>All fields good !!</span>'})
    # else:
        # return json.dumps({'html':'<span>Enter the required fields</span>'})
		
if __name__ == "__main__":
  #!export FLASK_ENV=development
  app.run(host='0.0.0.0', port=5000, debug=True)
