import os
import pandas as pd
import numpy as np
from scipy.stats import lognorm


class QUACI:
    Materials = [
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
        self.Materials = [
            'ExternalWood', 'BeamWood', 'Cinderblock', 'Concrete', 'Earthen',
            'Firedbrick', 'Glass', 'Glass wool', 'Gypsum', 'Hemp', 'Lath',
            'Mortar', 'OSB', 'Paint', 'Plywood', 'Steel', 'WaterProofing', 'XPS'
        ]
        self.impact_categories = [
            "Acidification",
            "Climate change",
            "Climate change - Biogenic",
            "Climate change - Fossil",
            "Climate change - Land use and LU change",
            "Ecotoxicity, freshwater - inorganics",
            "Ecotoxicity, freshwater - organics - p.1",
            "Ecotoxicity, freshwater - organics - p.2",
            "Ecotoxicity, freshwater - part 1",
            "Ecotoxicity, freshwater - part 2",
            "Eutrophication, freshwater",
            "Eutrophication, marine",
            "Eutrophication, terrestrial",
            "Human toxicity, cancer",
            "Human toxicity, cancer - inorganics",
            "Human toxicity, cancer - organics",
            "Human toxicity, non-cancer",
            "Human toxicity, non-cancer - inorganics",
            "Human toxicity, non-cancer - organics",
            "Ionising radiation",
            "Land use",
            "Ozone depletion",
            "Particulate matter",
            "Photochemical ozone formation",
            "Resource use, fossils",
            "Resource use, minerals and metals",
            "Water use"
        ]
        self.data = {}

    def load_data(self) -> dict:

        for dirpath, dirnames, filenames in os.walk(self.path):
            for filename in filenames:
                df = pd.read_excel(os.path.join(dirpath, filename))
                name = filename.split('_')[0]
                self.data[name] = df

        for mat in self.Materials:
            if mat in self.data.keys():
                dp = self.data[mat]
                dp = dp.iloc[dp[dp.iloc[:, 0] ==
                                "Catégorie d'impact"].index[0]:]
                dp.columns = dp.iloc[0]
                dp = dp[1:]
                dp = dp.reset_index(drop=True)
                self.data[mat] = dp.iloc[:27]

    def create_simulations(self):
        Simulations = pd.DataFrame()
        Simulations["Catégorie d'impact"] = self.impact_categories

        for mat in self.Materials:
            if mat in self.data.keys():
                dk = self.data[mat].copy()
                Moyenne = pd.to_numeric(
                    dk["Moyenne"], errors='coerce')
                std = pd.to_numeric(dk["SD"], errors='coerce')
                lognormal_samples = lognorm(s=std, scale=np.exp(Moyenne)).rvs()
                Simulations[mat] = lognormal_samples

        return Simulations


quaci = QUACI(
    comp_quantity=pd.Series([1, 2, 3]),
    dur_vie_mean=10.0,
    dur_vie_std_dev=2.0,
    dur_vie_comp=pd.Series([5, 6, 7]),
    path='Material_Statistics'
)
quaci.load_data()
simulations = quaci.create_simulations()
simulations.to_csv('simulations.csv', index=False)
print("Simulations saved to simulations.csv")
