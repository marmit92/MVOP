from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import mongo
import numpy as np
import pandas as pd
from pyDecision.algorithm import topsis_method
import locale
from datetime import datetime
from app.helpers import parse_number
from app.promethee import promethee
from bson.objectid import ObjectId

methods_bp = Blueprint('methods', __name__, url_prefix='/methods')

##############################################################################
# IZBIRA METODE
##############################################################################
@methods_bp.route('/', methods=['GET', 'POST'])
def methods():
    if request.method == 'POST':
        # Preberemo izbrana podjetja (checkbox)
        selected_ids = request.form.getlist("selected_companies")
        # Zahteva vsaj 5 izbranih
        if len(selected_ids) < 3:
            flash("Prosimo, izberite vsaj 3 podjetij za analizo!", "danger")
            return redirect(url_for('methods.methods'))
        
        # 2) Nastavimo include_to_analysis=True/False v 'companies' zbirki
        all_companies_ita = list(mongo.db.companies.find({}))
        for comp in all_companies_ita:
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
        
        # Preberemo izbrano metodo (AHP, TOPSIS, PROMETHEE ali WSM)
        chosen_method = request.form.get("method")
        # Preberemo poimenovanje analize
        analysis_name = request.form.get("analysis_name")

        # Prikaže le podjetja, kriterije in uteži, ki imajo include_to_analysis=True.         
        all_criteria = list(mongo.db.criteria.find({"include_to_analysis": True}))
        excluded_criteria_ids = [str(c["_id"]) for c in all_criteria]
        all_weights = list(mongo.db.weights.find({"id_kriterija": {"$in": excluded_criteria_ids}}))
        all_companies = list(mongo.db.companies.find({"_id": {"$in": [ObjectId(cid) for cid in selected_ids]}}))

        weights_dict = {w['id_kriterija']: w['weight_value'] for w in all_weights}
        weights = [weights_dict.get(str(c["_id"]), 0.0) for c in all_criteria]
        weight_sum = sum(weights)
        if weight_sum == 0:
            flash("Vsota uteži je 0. Prosimo, preverite uteži.", "danger")
            return redirect(url_for('methods.methods'))
        weights = [w / weight_sum for w in weights]

        sorted_criteria = sorted(all_criteria, key=lambda c: c["name"])

        criteria_mapping = {
            "prihodek": "Prihodek",
            "dobiček": "Dobiček",
            "finančna sredstva": "Finančna sredstva",
            "sprememba dobička": "Sprememba dobička",
            "sprememba prihodkov": "Sprememba prihodkov",
            "število zaposlenih": "Število zaposlenih"
        }

        decision_matrix = []
        company_names = []
        for comp in all_companies:
            row = []
            for c in sorted_criteria:
                cname = c["name"].strip().lower().replace("\t", "")
                key = criteria_mapping.get(cname, None)
                if key:
                    val = parse_number(comp.get(key))
                else:
                    val = 0
                if val is None:
                    val = 0
                row.append(val)
            decision_matrix.append(row)
            company_names.append(comp["Ime podjetja"])
        decision_matrix = np.array(decision_matrix, dtype=int)
        print("[DEBUG-Decision Matrix:]", decision_matrix, "[Company Names]:", company_names)

        benefit = ["max" if c.get("type", "").lower() == "korist" else "min" for c in sorted_criteria]
        print("[DEBUG-BENEFIT!]: Benefit list:", benefit)

        matrix_html = pd.DataFrame(decision_matrix, index=company_names, columns=[c["name"].strip() for c in sorted_criteria]).to_html(justify="inherit", classes='table table-striped table-hover border-primary table-sm')

        match chosen_method: 
            case"TOPSIS":
                try:
                    topsis_res = topsis_method(decision_matrix, weights, benefit, graph=False, verbose=False)
                    print("[DEBUG-TOPSIS-RESULT]: TOPSIS Results:", topsis_res)
                    sorted_indices = np.argsort(-topsis_res)
                
                    ranking = [{"company": company_names[idx], "score": round(float(topsis_res[idx]), 2)} for idx in sorted_indices]
                except Exception as e:
                    flash(f"Napaka pri izvajanju TOPSIS metode: {str(e)}", "danger")
                    return redirect(url_for('methods.methods'))
            case "PROMETHEE":                
                try:
                    promethee_result = promethee(weights, benefit, [[company_names[i]] + list(decision_matrix[i]) for i in range(len(company_names))])
                    ranking = [{"company": alt, "score": round(promethee_result["net_flows"][alt], 2)} for alt in promethee_result["rankings"]]
                    print("[DEBUG-PROMETHEE-RESULT]:", promethee_result)
                except Exception as e:
                    flash(f"Napaka pri izvajanju PROMETHEE metode: {str(e)}", "danger")
                    return redirect(url_for('methods.methods'))
                
            case _:
                flash("Neznana metoda izbrane analize.", "danger")
                return redirect(url_for('methods.methods'))

        locale.setlocale(locale.LC_TIME, 'sl_SI.UTF-8')
        formatted_date = datetime.now().strftime("[%d.%m.%Y]_[%H:%M:%S]")

        analysis_doc = {
            "analysis_name": f"[{analysis_name}]_[{chosen_method}]_{formatted_date}",
            "method": chosen_method,
            "criteria_chosen_to_analysis": [str(c["name"]) for c in sorted_criteria],
            "weights": weights,
            "companies_chosen": [str(x["Ime podjetja"]) for x in all_companies],
            "decision_matrix": decision_matrix.tolist(),
            "ranking": ranking,
            "matrix_html": matrix_html
        }

        mongo.db.analysis_results.insert_one(analysis_doc)

        flash(f"Uspešno izbrali {len(selected_ids)} podjetij in metodo {chosen_method}! ✅", "success")
        return redirect(url_for('results.results'))
    else:
        all_companies = list(mongo.db.companies.find())
        return render_template('methods.html', companies=all_companies, active_tab='methods')
