
from flask import Flask
from flask import request
from flask import render_template
from zillow_api import creat_html

app = Flask(__name__)

@app.route('/')
def my_form():
    return render_template("form.html")

@app.route('/', methods=['POST'])
def my_form_post():

    zipcode = request.form['Zipcode']
    api_key = request.form['API_KEY']
    return creat_html (zipcode, api_key)

if __name__ == '__main__':
    app.run()
