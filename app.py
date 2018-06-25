from flask import Flask, render_template, json, request
app = Flask(__name__)

@app.route("/")
def main():
  return render_template('index.html')

@app.route('/explore',methods=['POST'])
def explore():
    # read the posted values from the UI
    _statement = request.form['inputStatement']
    print(_statement)
 
    # validate the received values
    if _statement:
        return json.dumps({'html':'<span>All fields good !!</span>'})
    else:
        return json.dumps({'html':'<span>Enter the required fields</span>'})
  
if __name__ == "__main__":
  app.run() 

