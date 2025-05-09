

import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Union
from app.models.material import Material
from app.utils.calculation import calculate_impact_matrix


class AnalysisService:
    @staticmethod
    def calculate_environmental_impact(materials_data, lifespan=50):
        impact_matrix = calculate_impact_matrix(materials_data, lifespan)
        return {category: float(np.sum(values)) for category, values in impact_matrix.items()}

    @staticmethod
    def compare_materials(material_ids, impact_category):
        materials = Material.query.filter(Material.id.in_(material_ids)).all()
        return {
            material.name: {
                'value': material.get_impact(impact_category),
                'unit': material.get_impact_unit(impact_category)
            } for material in materials
        }

    @staticmethod
    def generate_uncertainty_analysis(house_id, simulations=1000):
        from app.services.house_service import HouseService
        house = HouseService.get_house_by_id(house_id)
        if not house:
            return None

        materials = house.materials
        impact_categories = [
            "Climate change",
            "Acidification",
            "Resource use, fossils",
            "Water use",
        ]

        results = {}
        for category in impact_categories:
            samples = [
                sum(material.sample_impact(category) * material.quantity for material in materials)
                for _ in range(simulations)
            ]
            results[category] = {
                'mean': float(np.mean(samples)),
                'median': float(np.median(samples)),
                'std': float(np.std(samples)),
                'percentile_5': float(np.percentile(samples, 5)),
                'percentile_95': float(np.percentile(samples, 95))
            }
        return results


def compute_smd(a1: np.ndarray, a2: np.ndarray) -> pd.DataFrame:
    mean_diff = np.mean(a1 - a2, axis=0)
    std_diff = np.std(a1 - a2, axis=0, ddof=1)
    smd = mean_diff / std_diff
    std_error = std_diff / np.sqrt(a1.shape[0])
    return pd.DataFrame({'SMD': smd, 'StdError': std_error}, index=[f'Indicator {i+1}' for i in range(a1.shape[1])])


def compute_drd(a1: np.ndarray, a2: np.ndarray) -> pd.DataFrame:
    drd = (a1 - a2) / np.maximum(a1, a2)
    return pd.DataFrame(drd, columns=[f'Indicator {i+1}' for i in range(a1.shape[1])])


def compute_pairwise_probabilities(a1: np.ndarray, a2: np.ndarray) -> np.ndarray:
    return np.mean(a1 < a2, axis=0)


def generate_heatmap_data(matrices: Dict[str, np.ndarray]) -> Dict:
    keys = list(matrices.keys())
    n_matrices = len(keys)
    n_indicators = matrices[keys[0]].shape[1]

    result = {
        'labels': keys,
        'probabilities': np.zeros((n_matrices, n_matrices, n_indicators)).tolist(),
        'smd_values': np.zeros((n_matrices, n_matrices)).tolist()
    }

    for i in range(n_matrices):
        for j in range(n_matrices):
            if i != j:
                probs = compute_pairwise_probabilities(matrices[keys[i]], matrices[keys[j]])
                smd_df = compute_smd(matrices[keys[i]], matrices[keys[j]])
                result['probabilities'][i][j] = probs.tolist()
                result['smd_values'][i][j] = float(np.mean(smd_df['SMD']))

    return result


def discernability_analysis(dfs: Dict[int, pd.DataFrame]) -> Dict:
    factors = list(dfs.values())[0].columns.tolist()
    comparisons = []
    house_ids = list(dfs.keys())

    for i in range(len(house_ids)):
        for j in range(i+1, len(house_ids)):
            df1, df2 = dfs[house_ids[i]], dfs[house_ids[j]]
            probabilities = [
                float(np.mean(df1[factor] < df2[factor])) for factor in factors
            ]
            comparisons.append({
                'house1': house_ids[i],
                'house2': house_ids[j],
                'values': probabilities
            })

    return {'factors': factors, 'comparisons': comparisons}


def heijungs_analysis(dfs: Dict[int, pd.DataFrame]) -> Dict:
    metrics = {}
    for h1, df1 in dfs.items():
        metrics[h1] = {}
        for h2, df2 in dfs.items():
            if h1 != h2:
                diff = df1.mean() - df2.mean()
                std = np.sqrt(df1.var() + df2.var())
                metrics[h1][h2] = round(float(np.mean(diff / std)), 4)
    return {'heijungs_metrics': metrics}


def ranking_probability_analysis(dfs: Dict[int, pd.DataFrame]) -> Dict:
    house_ids = list(dfs.keys())
    n_simulations = len(next(iter(dfs.values())))

    ranking_counts = {
        rank: {str(h): 0 for h in house_ids} for rank in range(1, len(house_ids) + 1)
    }

    for sim in range(n_simulations):
        totals = {
            h: np.sum(dfs[h].iloc[sim].values) for h in house_ids
        }
        ranked = sorted(totals.items(), key=lambda x: x[1])
        for rank, (house_id, _) in enumerate(ranked, start=1):
            ranking_counts[rank][str(house_id)] += 1 / n_simulations

    return {'house_ids': house_ids, 'ranking_probabilities': ranking_counts}
