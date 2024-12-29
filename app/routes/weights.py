from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import mongo

weights_bp = Blueprint('weights', __name__, url_prefix='/weights')

##############################################################################
# UTEŽI
##############################################################################
@weights_bp.route('/', methods=['GET', 'POST'])
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
        return redirect(url_for('weights.weights'))
    else:
        # GET
        all_criteria = list(mongo.db.criteria.find())
        for c in all_criteria:
            w_doc = mongo.db.weights.find_one({"id_kriterija": str(c["_id"])})
            c["weight_value"] = w_doc.get("weight_value", 0.0) if w_doc else 0.0
        return render_template('weights.html', criteria=all_criteria)
