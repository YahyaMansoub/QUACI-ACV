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

    # Define quantities per unit
    quantity_df = pd.DataFrame({
        'Component': ['PV', 'Battery', 'HVAC', 'DHW'],
        'Quantity': [400, 250, 50, 283],
        'Kg_per_unit': [1, 25, 1, 1]  # Adjust if units are different
    }).set_index('Component')

    durées_vie = {
        'ExternalWood': 50,
        'OSB': 50,
        'Poutrelle': 50,
        'Beam': 50,
        'Parquet': 50,
        'Steel': 50,
        'Glazing': 25,
        'Wool': 50,
        'WaterProofing': 30,
        'Polystyrene': 30,
        'Gypsum': 30,
        'Aluminium': 25,
        'Paint': 15,
        'Mortar': 50,
        'PV Systems': 25,
        'Battery': 10,
        'HVAC': 20,
        'DHW': 10,
        'Cinderblock': 50,
        'FriedBricks': 50,
        'Earth': 50,
        'Hemp': 50,
        'Concrete': 50
    }

    def __init__(
        self,
        comp_quantity: pd.Series,
        dur_vie_mean: float,
        dur_vie_std_dev: float,
        path: str
    ):

        self.dur_vie_comp = pd.Series({
            k: np.random.normal(loc=v, scale=0.05 * v) for k, v in self.durées_vie.items()
        })
        self.comp_quantity = comp_quantity
        self.comp_quantity = self.comp_quantity.to_frame().T
        self.dur_vie_mean = dur_vie_mean
        self.dur_vie_std_dev = dur_vie_std_dev
        self.dur_vie = np.random.normal(
            loc=dur_vie_mean, scale=dur_vie_std_dev)
        self.fact_renouv = np.maximum(1, self.dur_vie / self.dur_vie_comp)
        self.final_comp_quantity = comp_quantity * self.fact_renouv
        self.path = path
        self.end = pd.DataFrame()
        self.Materials = [
            'ExternalWood', 'BeamWood', 'Cinderblock', 'Concrete', 'Earthen',
            'Firedbrick', 'Glass', 'Glass wool', 'Gypsum', 'Hemp', 'Lath',
            'Mortar', 'OSB', 'Paint', 'Plywood', 'Steel', 'WaterProofing', 'XPS',
            '1kwh', '1Mj', 'Battery', 'DHW', 'HVAC', 'PV Systems', 'Transport in France',
            'Transport in Morocco', 'Transport Marin'
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
        # the life span dataframe
        self.lifespan = pd.DataFrame([self.dur_vie_comp, self.fact_renouv])
        self.lifespan.index = ['Durée de vie des composantes',
                               'Facteur de renouvellement']
        self.data = {}
        self.simulations = pd.DataFrame()
        self.material_dfs = {}

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

                mean = pd.to_numeric(dk["Moyenne"], errors='coerce')
                std = pd.to_numeric(dk["SD"], errors='coerce')

                # Generate random probabilities between 0 and 1
                n_samples = len(self.impact_categories)
                random_probs = np.random.random(n_samples)

                samples = []

                for i in range(n_samples):

                    m = mean.iloc[i] if not pd.isna(mean.iloc[i]) else 0
                    s = std.iloc[i] if not pd.isna(
                        std.iloc[i]) and std.iloc[i] > 0 else 0.1

                    # Cap standard deviation to prevent extreme values
                    s = min(s, 0.5)

                    try:
                        value = lognorm.ppf(
                            random_probs[i], s=s, scale=np.exp(m))

                        if np.isnan(value) or np.isinf(value) or value > 1e6:
                            value = 1000
                        samples.append(value)
                    except:
                        samples.append(0)
                Simulations[mat] = samples

        self.simulations = Simulations

    def step1(self):
        self.materials_df = self.comp_quantity.multiply(
            self.lifespan.loc["Facteur de renouvellement"], axis=1)
        self.result_df = pd.DataFrame(index=self.materials_df.index)
        for component in ['PV', 'Battery', 'HVAC', 'DHW']:
            qty = self. quantity_df.loc[component, 'Quantity']
            kg_per_unit = self.quantity_df.loc[component, 'Kg_per_unit']
            col_name = {
                'PV': 'PV Systems',
                'Battery': 'Battery',
                'HVAC': 'HVAC',
                'DHW': 'DHW'
            }[component]

            self.result_df[component] = self.materials_df[col_name] * qty

        self.result_df['Total Energy System'] = self.result_df.sum(axis=1)
        self.result_df['Total Building Component'] = self.materials_df.drop(columns=['PV Systems', 'Battery', 'HVAC', 'DHW']).sum(
            axis=1)-self.materials_df[['PV Systems', 'Battery', 'HVAC', 'DHW']].sum(axis=1)

    def step2(self):
        n_rows = len(self.simulations)

        normal_params = {
            "Parquet": (180, 25),
            "Aluminum": (350, 40),
            "Earth": (400, 60),
            "Module B6": (50, 5),
            "Transportation to Landfill": (30, 4),
        }
        # Generate DataFrame with normally distributed random values
        df_random = pd.DataFrame({
            key: np.random.normal(loc=mu, scale=sigma, size=n_rows)
            for key, (mu, sigma) in normal_params.items()
        })

        for col in df_random.columns:
            self.simulations[col] = df_random[col]

    def step3(self):
        r = self.simulations.copy()
        materials = [self.comp_quantity.index[0]]

        for material in materials:
            # Select numeric columns only
            numeric_cols = r.select_dtypes(include='number').columns
            non_numeric_cols = r.columns.difference(numeric_cols)

            # Prepare multipliers (fill NaN with 1.0)
            multipliers = self.result_df.loc[material].reindex(
                numeric_cols).fillna(1.0)

            # Multiply numeric part
            numeric_part = r[numeric_cols].mul(multipliers, axis=1)

            # Keep non-numeric part unchanged
            non_numeric_part = r[non_numeric_cols]

            # Combine back
            self.material_dfs[material] = pd.concat(
                [numeric_part, non_numeric_part], axis=1)

    def step4(self, name):
        categories = {
            "Module A Envelope": [
                "CinderBlock", "Fired Bricks", "Earth", "Hemp", "Concrete", "External Wood",
                "OSB", "Poutrelle", "Beam", "Parquet", "Steel", "Glazing", "Wool",
                "WaterProofing", "Polystyrene", "Gypsum", "Aluminum", "Paint", "Mortar"
            ],
            "Module A Demand Side": ["HVAC", "DHW"],
            "Module A Production Side PC": ["PV Systems"],
            "Module A Production Side PV&Battery": ["PV Systems", "Battery"],
            "Module A4 Transportation to construction site": [
                "Transportation In moroco", "Transportation in France", "Transportation marine"
            ],
            "Module C2 Transportation End Of Life": ["Transportation to Landfill"]
        }

        a = self.material_dfs[name].copy()

        # Initialize the new DataFrame
        new_df = {}

        # Loop over the categories and extract/compute the required columns
        for category, col_names in categories.items():
            # Check if all columns exist in the DataFrame
            existing_cols = [col for col in col_names if col in a.columns]

            if existing_cols:
                # Sum the selected columns
                new_df[category] = a[existing_cols].sum(axis=1)
            else:
                print(
                    f"Warning: None of the columns in {category} were found in the DataFrame")
        # Convert the dictionary to a DataFrame
        new_df = pd.DataFrame(new_df)
        self.end["Row Total"] = new_df.sum(axis=1, numeric_only=True)

        '''
        # Assuming "Row Total" column already exists
        max_allowed = 1_000_000

        # Normalize between 0 and 1
        normalized = self.end["Row Total"] / self.end["Row Total"].max()

        # Rescale to max_allowed
        self.end["Row Total Scaled"] = normalized * max_allowed
        '''

        # Your list of impact categories (likely a Series)
        categories = [
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

        # Add it to the dataframe
        self.end.insert(0, "Impact Category", categories)

    def final(self, name):
        self.load_data()
        self.create_simulations()
        self.step1()
        self.step2()
        self.step3()
        self.step4(name)

        # Set pandas display to show full numbers without scientific notation
        pd.set_option('display.float_format', '{:.6f}'.format)

        return self.end


'''
This Portion of the code is made only for testing 
this class .
'''


data = {
    "ExternalWood": [137.5, 137.5, 137.5, 137.5, 137.5, 1407.86],
    "OSB": [0, 0, 0, 0, 0, 4281.312],
    "Poutrelle": [0, 0, 0, 0, 0, 5352.83552],
    "Beam": [0, 0, 0, 0, 0, 790.72],
    "Parquet": [0, 0, 0, 0, 0, 229.7816],
    "Steel": [351, 225, 351, 351, 351, 270],
    "Glazing": [225.434208] * 6,
    "Wool": [725.92] * 6,
    "WaterProofing": [1177.349398] * 6,
    "Polystyrene": [107.6433735, 107.6433735, 107.6433735, 107.6433735, 0, 43.0573494],
    "Gypsum": [268.1392557] * 6,
    "Aluminium": [58.2] * 6,
    "Paint": [65.37796637] * 6,
    "Mortar": [21753.6, 13401.6, 13610.4, 21753.6, 20860.16, 4467.2],
    "PV Systems": [0.633333333, 0.633333333, 0.633333333, 0.766666667, 0.733333333, 0.633333333],
    "Battery": [1] * 6,
    "HVAC": [1] * 6,
    "DHW": [0.08333] * 6,
    "Cinderblock": [10609.6, 15914.4, 0, 15914.4, 40709.4, 0],
    "FriedBricks": [0, 0, 19447.2, 0, 0, 0],
    "Earth": [0, 75168, 0, 0, 0, 0],
    "Hemp": [43214.584, 0, 0, 0, 0, 0],
    "Concrete": [8775, 5625, 8775, 47925, 8775, 5625],
}

index = ["Hemp", "Earth", "Fired Bricks", "Concrete", "Cinder blocks", "Wood"]


'''
df = pd.DataFrame(data, index=index)

quaci = QUACI(
    comp_quantity=df.loc["Hemp"],
    dur_vie_mean=50.0,
    dur_vie_std_dev=50.0*0.05,
    path='Material_Statistics'
)


print(quaci.final("Hemp").head(30))
'''
