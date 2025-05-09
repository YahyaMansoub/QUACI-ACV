import numpy as np

def calculate_impact_matrix(materials_data, lifespan):
    """
    Calcule la matrice d'impacts environnementaux pour chaque catégorie.
    materials_data: liste de dicts avec clés 'impact_values' (dict catégorie->valeur) et 'quantity'
    lifespan: durée de vie pour pondération
    Retourne un dict { catégorie: np.ndarray }
    """
    result = {}
    for mat in materials_data:
        values = mat.get('impact_values', {})
        qty = mat.get('quantity', 1)
        for category, base_value in values.items():
            impact = base_value * qty * lifespan
            result.setdefault(category, []).append(impact)
    # Convertir en tableaux numpy
    return {cat: np.array(vals) for cat, vals in result.items()}
