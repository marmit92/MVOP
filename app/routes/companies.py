from flask import Blueprint, render_template
from app import mongo

companies_bp = Blueprint('companies', __name__, url_prefix='/companies')

##############################################################################
# PODJETJA
##############################################################################
@companies_bp.route('/', methods=['GET'])
def companies():
    # GET - prikaži vsa podjetja
    all_companies = list(mongo.db.companies.find())
    return render_template('companies.html', companies=all_companies)
