from flask import Blueprint, render_template
from app import mongo

results_bp = Blueprint('results', __name__, url_prefix='/results')

##############################################################################
# 6) REZULTATI 
##############################################################################
@results_bp.route('/')
def results():
    all_analysis_results = list(mongo.db.analysis_results.find())

    for analysis_doc in all_analysis_results:
        for r in analysis_doc.get("ranking", []):
            score_val = r.get("score")
            if isinstance(score_val, dict) and "$numberDouble" in score_val:
                try:
                    r["score"] = float(score_val["$numberDouble"])
                except (ValueError, TypeError):
                    r["score"] = 0.0
            elif isinstance(score_val, str):
                try:
                    r["score"] = float(score_val)
                except ValueError:
                    r["score"] = 0.0

    return render_template(
        'results.html',
        analysis_results=all_analysis_results
    )
