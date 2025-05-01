import os
import pandas as pd
import numpy as np
from scipy.stats import lognorm


class QUACI:
    existing = [
        'ExternalWood', 'BeamWood', 'Cinderblock', 'Concrete', 'Earthen',
        'Firedbrick', 'Glass', 'Glass wool', 'Gypsum', 'Hemp', 'Lath',
        'Mortar', 'OSB', 'Paint', 'Plywood', 'Steel', 'WaterProofing', 'XPS'
    ]

    def __init__(
        self,
        comp_quantity: pd.Series,
        dur_vie_mean: float,
        dur_vie_std_dev: float,
        dur_vie_comp: pd.Series,
        path: str
    ):
        self.comp_quantity = comp_quantity
        self.dur_vie_mean = dur_vie_mean
        self.dur_vie_std_dev = dur_vie_std_dev
        self.dur_vie = np.random.normal(
            loc=dur_vie_mean, scale=dur_vie_std_dev)
        self.fact_renouv = np.maximum(1, self.dur_vie / dur_vie_comp)
        self.final_comp_quantity = comp_quantity * self.fact_renouv
        self.path = path

    def load_and_clean_excels(self) -> dict:
        cleaned_dfs = {}
        target_filenames = {
            f"{name}_Tableau récap.xlsx".lower(): name for name in self.existing
        }

        for root, dirs, files in os.walk(self.path):
            for file in files:
                file_lower = file.lower()
                if file_lower in target_filenames:
                    full_path = os.path.join(root, file)
                    try:
                        df = pd.read_excel(full_path, engine='openpyxl')
                        # Find the header row
                        header_row_idx = df[df.iloc[:, 0]
                                            == "Catégorie d'impact"].index[0]
                        # Extract the sub dataframe starting from the header
                        sub_df = df.iloc[header_row_idx + 1:].copy()
                        sub_df.columns = df.iloc[header_row_idx].tolist()
                        # Process numeric columns, replacing commas with periods
                        numeric_cols = ['Moyenne', 'SD',
                                        'Médiane', 'CV', '2,5%', '97,5%', 'SEM']
                        for col in numeric_cols:
                            if col in sub_df.columns:
                                sub_df[col] = sub_df[col].astype(
                                    str).str.replace(',', '.').astype(float)
                        component_name = target_filenames[file_lower]
                        cleaned_dfs[component_name] = sub_df
                    except Exception as e:
                        print(f"Error processing {full_path}: {e}")
        return cleaned_dfs

    def generate_random_values(self, cleaned_dfs: dict) -> pd.DataFrame:
        data = []
        for material in self.existing:
            if material not in cleaned_dfs:
                print(
                    f"Material {material} not found in cleaned DataFrames. Skipping.")
                continue
            df = cleaned_dfs[material]
            for _, row in df.iterrows():
                category = row.get("Catégorie d'impact")
                mean = row.get('Moyenne')
                std = row.get('SD')
                if pd.isna(mean) or pd.isna(std):
                    print(
                        f"Missing mean or std for {category} in {material}. Skipping.")
                    continue
                if mean <= 0:
                    print(
                        f"Non-positive mean for {category} in {material}. Skipping.")
                    data.append((material, category, np.nan))
                    continue
                if std <= 0:
                    data.append((material, category, mean))
                    continue
                # Compute parameters for lognormal distribution
                var = std ** 2
                try:
                    sigma_sq = np.log(var / (mean ** 2) + 1)
                    sigma = np.sqrt(sigma_sq)
                    mu = np.log(mean) - sigma_sq / 2
                    generated_value = lognorm.rvs(s=sigma, scale=np.exp(mu))
                except Exception as e:
                    print(
                        f"Error generating value for {category} in {material}: {e}")
                    generated_value = np.nan
                data.append((material, category, generated_value))

        # Create DataFrame and pivot
        result_df = pd.DataFrame(
            data, columns=['Material', 'Impact Category', 'Value'])
        result_pivot = result_df.pivot(
            index='Impact Category', columns='Material', values='Value')
        return result_pivot
