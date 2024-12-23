
import os
from flask import Flask, render_template, jsonify
from flask_pymongo import PyMongo
from dotenv import load_dotenv

# Naloži ENV spremenljivke iz .env datoteke
load_dotenv()

# Pridobi MONGO_URI iz ENV spremenljivk
mongo_uri = os.getenv("MONGO_URI")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Glavna stran

# Povezava z MongoDB Atlas
app.config["MONGO_URI"] = mongo_uri
mongo = PyMongo(app) 

@app.route('/companies', methods=['GET'])
def get_companies():
    # Pridobi vse podatke iz zbirke "companies"
    companies = list(mongo.db.five_hundred.find({}, {"_id": 0}))
    return jsonify(companies)

if __name__ == '__main__':
    app.run(debug=True)
