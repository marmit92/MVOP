from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import mongo

criteria_bp = Blueprint('criteria', __name__, url_prefix='/criteria')

##############################################################################
# KRITERIJI
##############################################################################
@criteria_bp.route('/', methods=['GET', 'POST'])
def criteria():
    if request.method == 'POST':
        # Preberemo izbrane ID-je iz obrazca (checkbox: name="selected_criteria")
        selected_ids = request.form.getlist("selected_criteria")  # vrne seznam stringov
        # Pridobimo vse kriterije iz baze
        all_criteria = list(mongo.db.criteria.find())
        
        # Sprehodimo se in za vsak kriterij določimo "include_to_analysis" = True/False
        for crit in all_criteria:
            crit_id_str = str(crit["_id"])
            include = crit_id_str in selected_ids
            # Uporabnik je ta kriterij označil
            mongo.db.criteria.update_one(
                {"_id": crit["_id"]},
                {"$set": {"include_to_analysis": include}}
            )

        flash("Izbira kriterijev je uspešno shranjena!✅")
        return redirect(url_for('criteria.criteria'))

    else:
        # GET -> pridobimo vse kriterije in jih pošljemo v predlogo
        all_criteria = list(mongo.db.criteria.find())
        return render_template('criteria.html', criteria=all_criteria)
