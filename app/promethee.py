import numpy as np
import pandas as pd

def promethee(weights, criteria, alternatives):
    """
    Implementacija metode PROMETHEE.

    Parametri:
        weights (list): Uteži za kriterije (seštevek mora biti 1).
        criteria (list): Seznam kriterijev s tipi ("max" ali "min").
        alternatives (list): Seznam alternativ z vrednostmi po kriterijih.

    Vrne:
        dict: Neto tokovi (phi) za alternative in njihove razvrstitve.
    """
    # Preverjanje vhodnih podatkov
    if len(weights) != len(criteria):
        raise ValueError("Število uteži mora ustrezati številu kriterijev.")

    num_criteria = len(criteria)
    num_alternatives = len(alternatives)

    # Ekstrakcija vrednosti matrike kriterijev
    decision_matrix = np.array([alt[1:] for alt in alternatives])

    # Normalizacija matrike (odvisno od vrste kriterija)
    normalized_matrix = np.zeros_like(decision_matrix, dtype=float)

    for j in range(num_criteria):
        if criteria[j] == "max":
            max_val = decision_matrix[:, j].max()
            min_val = decision_matrix[:, j].min()
            normalized_matrix[:, j] = (decision_matrix[:, j] - min_val) / (max_val - min_val)
        elif criteria[j] == "min":
            max_val = decision_matrix[:, j].max()
            min_val = decision_matrix[:, j].min()
            normalized_matrix[:, j] = (max_val - decision_matrix[:, j]) / (max_val - min_val)

    # Izračun razlik med alternativami
    difference_matrix = np.zeros((num_alternatives, num_alternatives, num_criteria))

    for i in range(num_alternatives):
        for k in range(num_alternatives):
            difference_matrix[i, k] = normalized_matrix[i] - normalized_matrix[k]

    # Izračun preferenčnih funkcij
    preference_matrix = np.maximum(difference_matrix, 0)

    # Agregacija preferenc
    aggregated_preference = np.zeros((num_alternatives, num_alternatives))

    for i in range(num_alternatives):
        for k in range(num_alternatives):
            aggregated_preference[i, k] = np.sum(preference_matrix[i, k] * weights)

    # Izračun odhajajočih (phi+) in prihajajočih tokov (phi-)
    leaving_flows = aggregated_preference.sum(axis=1) / (num_alternatives - 1)
    entering_flows = aggregated_preference.sum(axis=0) / (num_alternatives - 1)

    # Neto tokovi
    net_flows = leaving_flows - entering_flows

    # Razvrstitev alternativ
    rankings = sorted([(alternatives[i][0], flow) for i, flow in enumerate(net_flows)], 
                      key=lambda x: x[1], reverse=True)

    return {
        "net_flows": dict(rankings),
        "rankings": [alt[0] for alt in rankings]
    }