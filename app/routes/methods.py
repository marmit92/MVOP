from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import mongo
import numpy as np
import pandas as pd
from pyDecision.algorithm import topsis_method, saw_method, vikor_method, macbeth_method
import locale
from datetime import datetime
from app.helpers import parse_number
from app.promethee import promethee
from bson.objectid import ObjectId

methods_bp = Blueprint('methods', __name__, url_prefix='/methods')

@methods_bp.route('/comparison', methods=['GET', 'POST'])
def comparison():
    analysis_results = list(mongo.db.analysis_results.find())
    
    # Generate HTML tables for decision matrices
    for analysis in analysis_results:
        analysis['matrix_html'] = pd.DataFrame(
            analysis['decision_matrix'],
            columns=[c.strip() for c in analysis.get('criteria_chosen_to_analysis', [])],
            index=analysis.get('companies_chosen', [])
        ).to_html(classes='table table-striped table-hover border-primary table-sm')
    
    if request.method == 'POST':
        first_index = int(request.form.get('first_analysis')) - 1
        second_index = int(request.form.get('second_analysis')) - 1
        
        first_analysis = analysis_results[first_index]
        second_analysis = analysis_results[second_index]
        
        # Check if criteria, weights, and companies match
        if (first_analysis['criteria_chosen_to_analysis'] == second_analysis['criteria_chosen_to_analysis'] and
            first_analysis['weights'] == second_analysis['weights'] and
            first_analysis['companies_chosen'] == second_analysis['companies_chosen']):
            
            # Render the comparison if valid
            return render_template(
                'comparison.html', 
                analysis_results=analysis_results, 
                first_analysis=first_analysis, 
                second_analysis=second_analysis
            )
        else:
            # Redirect with error if not valid
            flash("❌ Primerjava je dovoljena le med analizami z enakimi kriteriji, utežmi in alternativami.", "danger")
            return redirect(url_for('methods.comparison'))
    
    # Initial rendering of the comparison page
    return render_template('comparison.html', analysis_results=analysis_results)

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
            case "TOPSIS":
                try:
                    topsis_result = topsis_method(decision_matrix, weights, benefit, graph=False, verbose=False)
                    print("[DEBUG-TOPSIS-RESULT]: ", topsis_result)
                    sorted_indices = np.argsort(-topsis_result)                
                    ranking = [{"company": company_names[idx], "score": round(float(topsis_result[idx]), 2)} for idx in sorted_indices]
                except Exception as e:
                    flash(f"Napaka pri izvajanju TOPSIS metode: {str(e)}", "danger")
                    return redirect(url_for('methods.methods'))
            case "WSM":
                try:
                    wsm_result = saw_method(decision_matrix, benefit, weights, graph=False, verbose=False)
                    # Ekstrakcija drugega stolpca z uporabo np.concatenate
                    scores = np.concatenate(wsm_result[:, 1:].reshape(1, -1))
                    # Razvrstitev po ocenah v padajočem vrstnem redu
                    sorted_indices = np.argsort(-scores)
                    ranking = [{"company": company_names[idx], "score" : round(float(scores[idx]), 2)} for idx in sorted_indices]
                except Exception as e:
                    flash(f"Napaka pri izvajanju WSM metode: {str(e)}", "danger")
                    return redirect(url_for('methods.methods'))                 
            case "PROMETHEE":                
                try:
                    promethee_result = promethee(weights, benefit, [[company_names[i]] + list(decision_matrix[i]) for i in range(len(company_names))])
                    ranking = [{"company": alt, "score": round(promethee_result["net_flows"][alt], 2)} for alt in promethee_result["rankings"]]
                    print("[DEBUG-PROMETHEE-RESULT]:", promethee_result)
                except Exception as e:
                    flash(f"Napaka pri izvajanju PROMETHEE metode: {str(e)}", "danger")
                    return redirect(url_for('methods.methods'))
            case "VIKOR":
                try:
                    s, r, q, vikor_result = vikor_method(decision_matrix, weights, benefit, strategy_coefficient = 0.5, graph=False, verbose=False)
                    print("[DEBUG-VIKOR-RESULT]: ", vikor_result)
                    scores = np.concatenate(vikor_result[:, 1:].reshape(1, -1))
                    sorted_indices = np.argsort(-scores)                
                    ranking = [{"company": company_names[idx], "score": round(float(scores[idx]), 2)} for idx in sorted_indices]
                except Exception as e:
                    flash(f"Napaka pri izvajanju VIKOR metode: {str(e)}", "danger")
                    return redirect(url_for('methods.methods'))                
            case "MACBETH":
                try:
                    macbeth_result = macbeth_method(decision_matrix, weights, benefit, graph=False, verbose=False)
                    print("[DEBUG-MACBETH-RESULT]: ", macbeth_result)
                    sorted_indices = np.argsort(-macbeth_result)                
                    ranking = [{"company": company_names[idx], "score": round(float(macbeth_result[idx]), 2)} for idx in sorted_indices]
                except Exception as e:
                    flash(f"Napaka pri izvajanju MACBETH metode: {str(e)}", "danger")
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
            "weights": list(weights), 
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
