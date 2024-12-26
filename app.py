import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
import pandas as pd
import numpy as np
from bson.objectid import ObjectId

# pyDecision za MCDA metode
from pyDecision.algorithm import topsis_method, saw_method  # npr. WSM = SAW

# Naloži ENV spremenljivke iz .env
load_dotenv()

app = Flask(__name__)

##############################################################################
# Povezava z DB: Nastavi povezavo z MongoDB iz ENV
##############################################################################

mongo_uri = os.getenv("MONGO_URI")
app.config["MONGO_URI"] = mongo_uri

app.secret_key = "moja-super-sekretna-gesla1237864"

mongo = PyMongo(app)

##############################################################################
# HELPER FUNKCIJE ZA PARSANJE
##############################################################################

def parse_dollar_value(value_str):
    """
    Odstrani $ in vejice ter pretvori v float.
    Primer: "$648,125" -> 648125.0
    Če vrednost ni ustrezna, vrne None.
    """
    if not value_str:
        return None
    # Odstranimo $ in presledke, ter zamenjamo vejice
    clean_str = value_str.replace('$', '').replace(',', '')
    try:
        return float(clean_str)
    except ValueError:
        return None

def parse_percentage(value_str):
    """
    Odstrani % in pretvori v float.
    Primer: "32.8%" -> 32.8
    Če je "-", vrne 0 ali None (po izbiri).
    """
    if not value_str or value_str.strip() == '-':
        return 0.0
    clean_str = value_str.replace('%', '').replace(',', '')
    try:
        return float(clean_str)
    except ValueError:
        return None

def parse_int(value_str):
    """
    Npr. "2,100,000" -> 2100000
    """
    if not value_str:
        return None
    clean_str = value_str.replace(',', '')
    try:
        return int(clean_str)
    except ValueError:
        return None

##############################################################################
# 1) UVODNA STRAN
##############################################################################

@app.route('/')
def index():
    return render_template('index.html')

##############################################################################
# 2) PODJETJA
##############################################################################

@app.route('/companies', methods=['GET'])
def companies():
    # GET - prikaži vsa podjetja
    all_companies = list(mongo.db.companies.find())
    return render_template('companies.html', companies=all_companies)

##############################################################################
# 3) KRITERIJI
##############################################################################

@app.route('/criteria', methods=['GET', 'POST'])
def criteria():
    if request.method == 'POST':
        # 1) Preberemo izbrane ID-je iz obrazca (checkbox: name="selected_criteria")
        selected_ids = request.form.getlist("selected_criteria")  # vrne seznam stringov

        # 2) Pridobimo vse kriterije iz baze
        all_criteria = list(mongo.db.criteria.find({}))

        # 3) Sprehodimo se in za vsak kriterij določimo "include_to_analysis" = True/False
        from bson.objectid import ObjectId
        for crit in all_criteria:
            crit_id_str = str(crit["_id"])
            if crit_id_str in selected_ids:
                # Uporabnik je ta kriterij označil
                mongo.db.criteria.update_one(
                    {"_id": crit["_id"]},
                    {"$set": {"include_to_analysis": True}}
                )
            else:
                # Ni označen
                mongo.db.criteria.update_one(
                    {"_id": crit["_id"]},
                    {"$set": {"include_to_analysis": False}}
                )

        flash("Izbira kriterijev je uspešno shranjena!✅")
        return redirect(url_for('criteria'))

    else:
        # GET -> pridobimo vse kriterije in jih pošljemo v predlogo
        all_criteria = list(mongo.db.criteria.find())
        return render_template('criteria.html', criteria=all_criteria)


##############################################################################
# 4) UTEŽI
##############################################################################

@app.route('/weights', methods=['GET', 'POST'])
def weights():
    if request.method == 'POST':
        # Shranimo uteži iz obrazca
        all_criteria = list(mongo.db.criteria.find())
        for c in all_criteria:
            crit_id = str(c["_id"])
            # Ime polja npr. weight_<crit_id>
            w_val = request.form.get(f"weight_{crit_id}", None)
            if w_val is not None:
                # Upsert zapis
                mongo.db.weights.update_one(
                    {"id_kriterija": crit_id},
                    {
                        "$set": {
                            "name": c["name"],
                            "id_kriterija": crit_id,
                            "weight_value": float(w_val)
                        }
                    },
                    upsert=True
                )
        flash("Uteži so uspešno nastavljeni!✅")
        return redirect(url_for('weights'))
    else:
        # GET
        all_criteria = list(mongo.db.criteria.find())
        # Za vsak kriterij poiščemo utež
        for c in all_criteria:
            w_doc = mongo.db.weights.find_one({"id_kriterija": str(c["_id"])})
            if w_doc:
                c["weight_value"] = w_doc.get("weight_value", 0.0)
            else:
                c["weight_value"] = 0.0
        return render_template('weights.html', criteria=all_criteria)

##############################################################################
# 5) IZBIRA METODE
##############################################################################

@app.route('/methods', methods=['GET', 'POST'])
def methods():
    if request.method == 'POST':
        # 1) Preberemo izbrana podjetja (checkbox)
        selected_ids = request.form.getlist("selected_companies")

        # Primer: zahteva vsaj 5 izbranih
        if len(selected_ids) < 5:
            flash("Prosimo, izberite vsaj 5 podjetij za analizo!", "error")
            return redirect(url_for('methods'))

        # 2) Nastavimo include_to_analysis=True/False v 'companies' zbirki
        all_companies = list(mongo.db.companies.find({}))
        for comp in all_companies:
            comp_id_str = str(comp["_id"])
            if comp_id_str in selected_ids:
                mongo.db.companies.update_one(
                    {"_id": comp["_id"]},
                    {"$set": {"include_to_analysis": True}}
                )
            else:
                mongo.db.companies.update_one(
                    {"_id": comp["_id"]},
                    {"$set": {"include_to_analysis": False}}
                )

        # 3) Preberemo izbrano metodo (npr. AHP, TOPSIS, PROMETHEE itd.)
        chosen_method = request.form.get("method")

        # Lahko tukaj izvedete takojšnji izračun MCDA,
        # ali pa ga naredite kasneje v /results. V tem primeru le flash in redirect:
        flash(f"Uspešno izbrali {len(selected_ids)} podjetij in metodo {chosen_method}!", "success")

        return redirect(url_for('results', method=chosen_method))

    else:
        # GET: Prikažemo seznam podjetij
        all_companies = list(mongo.db.companies.find())
        return render_template('methods.html', companies=all_companies)


##############################################################################
# 6) REZULTATI 
##############################################################################
@app.route('/results')
def results():
    # 1) Preberemo izbran method iz query param (npr. "?method=TOPSIS")
    method = request.args.get('method', 'TOPSIS')

    # Debug
    print(f"[DEBUG] Izbrana metoda: {method}")

    # 2) Najdemo shranjen rezultat v "analysis_results" za to metodo
    analysis_doc = mongo.db.analysis_results.find_one({"method": method})

    if analysis_doc:
        # Če obstaja zapis
        ranking = analysis_doc.get("ranking", [])
        
        # Če "score" ni neposredno float, temveč dict {"$numberDouble": "..."},
        # ga pretvorimo v float, da ga lahko uporabimo v grafih, tabelah ipd.
        for r in ranking:
            score_val = r.get("score")
            if isinstance(score_val, dict) and "$numberDouble" in score_val:
                r["score"] = float(score_val["$numberDouble"])
            # Drugače, če je score že float ali int, ostane nespremenjen

    else:
        # Ni nič v bazi -> prikažemo dummy podatke ali javljamo napako
        flash(f"Ni najdenih rezultatov za metodo {method}. Prikaz DEMO podatkov.", "info")
        ranking = [
            {"company": "Demo 1", "score": 0.85},
            {"company": "Demo 2", "score": 0.75},
            {"company": "Demo 3", "score": 0.72},
            {"company": "Demo 4", "score": 0.65},
        ]

    # 3) V analysis_doc so morda še polja "matrix_html", "weights_used", ...
    if analysis_doc:
        matrix_html = analysis_doc.get("matrix_html", "<p>Matrika ni na voljo.</p>")
        weights = analysis_doc.get("weights_used", [])
    else:
        matrix_html = "<p>Matrika DEMO.</p>"
        weights = [0.25, 0.25, 0.25, 0.25]

    # 4) Priprava podatkov za morebitni graf (Chart.js ipd.)
    chart_labels = [item["company"] for item in ranking]
    chart_data   = [item["score"]   for item in ranking]

    # 5) Pokličemo predlogo "results.html" in pošljemo spremenljivke
    return render_template(
        'results.html',
        method=method,
        matrix=matrix_html,
        weights=weights,
        results=ranking,
        chart_labels=chart_labels,
        chart_data=chart_data
    )


##############################################################################
# ZAGON APLIKACIJE
##############################################################################

if __name__ == '__main__':
    app.run(debug=True)
