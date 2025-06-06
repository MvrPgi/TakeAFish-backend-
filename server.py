from flask import Flask, render_template, request
from species import get_species
from waitress import serve


app = Flask(__name__)



@app.route('/')
@app.route('/index')
def index():
    return render_template('species_picker.html')




if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)