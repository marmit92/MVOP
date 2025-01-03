from flask import Flask
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os

mongo = PyMongo()

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')      # Poti do predlog in datotek

    # Naloži ENV spremenljivke iz .env
    load_dotenv()

    # Konfiguracija MongoDB
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    app.secret_key = os.getenv("SECRET_KEY", "moja-super-sekretna-786454557")

    # Inicializacija MongoDB
    mongo.init_app(app)

    # Registracija Blueprints
    from .routes.main import main_bp
    from .routes.analysis import analysis_bp
    from .routes.companies import companies_bp
    from .routes.criteria import criteria_bp
    from .routes.weights import weights_bp
    from .routes.methods import methods_bp
    from .routes.results import results_bp
    from .routes.intro import intro_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(companies_bp)
    app.register_blueprint(criteria_bp)
    app.register_blueprint(weights_bp)
    app.register_blueprint(methods_bp)
    app.register_blueprint(results_bp)
    app.register_blueprint(intro_bp)

    return app
