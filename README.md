# Hypothesis Generation
We present an approach for automated hypothesis generation that can help the analyst explore the space of possibilities.

# Running the Code 

## Setting up Stanford Core Nlp Server

* Set up the Stanford's core nlp server instance on localhost:9000
* Follow instructions here: https://www.khalidalnajjar.com/setup-use-stanford-corenlp-server-python/
* Install python 3 and the package "stanfordcorenlp" using pip
* Install flask

## Running the web application

* Set up the Stanford's core nlp server
* Open jupyter and run each cell in the app.ipynb notebook
* Install missing packages imported in the first cell using magic commands `!pip install <package>`
Note: app.py is the python version of notebook but it's not updated.

## Running Components

* Run the following line to run any component
* `python <path to component> --sentence <Input Sentence> --host <corenlp host> --port <corenlp port>`
* Eg. `python NER.py --sentence "John works for Google." --host "http://localhost" --port 9000`
