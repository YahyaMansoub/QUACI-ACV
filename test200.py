import os
import pandas as pd
import numpy as np
from scipy.stats import lognorm


class QUACI:
    # Liste des matériaux regroupée pour éviter les doublons
    Materials = [
        'External Wood',      # Regroupement de ExternalWood et External Wood OSB
        'Beam',              # Regroupement de BeamWood et Beam
        'Cinderblock',       # Uniformisation de Cinderblock/CinderBlock
        'Concrete',
        'Earth',            # Regroupement de Earthen et Earth
        'Fired Bricks',     # Regroupement de Firedbrick et Fired Bricks
        'Glass',            # Regroupement de Glass et Glazing
        'Wool',             # Regroupement de Glass wool et Wool
        'Gypsum',
        'Hemp',
        'Lath',
        'Mortar',
        'OSB',
        'Paint',
        'Plywood',
        'Steel',
        'WaterProofing',
        'Polystyrene',      # Regroupement de XPS et Polystyrene
        'Parquet',
        'Poutrelle',
        'Aluminum',
        'PV Systems',
        'Battery',
        'HVAC',
        'DHW'
    ]
    
    # Mapping des anciens noms vers les nouveaux noms pour la correspondance
    material_mapping = {
        'ExternalWood': 'External Wood',
        'External Wood OSB': 'External Wood',
        'BeamWood': 'Beam',
        'Firedbrick': 'Fired Bricks',
        'Glass wool': 'Wool',
        'Glazing': 'Glass',
        'Earthen': 'Earth',
        'XPS': 'Polystyrene'
    }

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
        # Charger les données à partir des fichiers Excel
        for dirpath, dirnames, filenames in os.walk(self.path):
            for filename in filenames:
                df = pd.read_excel(os.path.join(dirpath, filename))
                name = filename.split('_')[0]
                # Appliquer le mapping des matériaux
                name = self.material_mapping.get(name, name)
                self.data[name] = df

        # Traiter les données chargées
        for mat in self.Materials:
            if mat in self.data.keys():
                dp = self.data[mat]
                dp = dp.iloc[dp[dp.iloc[:, 0] ==
                                "Catégorie d'impact"].index[0]:]
                dp.columns = dp.iloc[0]
                dp = dp[1:]
                dp = dp.reset_index(drop=True)
                self.data[mat] = dp.iloc[:27]

        # Générer des données aléatoires pour les matériaux manquants
        self.generate_missing_data()

    def generate_missing_data(self):
        """Génère des données aléatoires pour les matériaux sans fichiers récapitulatifs."""
        # Liste des matériaux sans données
        missing_materials = [mat for mat in self.Materials if mat not in self.data]
        
        if missing_materials:
            print(f"Génération de données aléatoires pour {len(missing_materials)} matériaux manquants:")
            for mat in missing_materials:
                print(f" - {mat}")
            
            # Créer un DataFrame template basé sur un matériau existant si disponible
            template = None
            for mat in self.Materials:
                if mat in self.data:
                    template = self.data[mat].copy()
                    break
            
            # Si aucun matériau n'a de données, créer un template de zéro
            if template is None:
                template = pd.DataFrame({
                    "Catégorie d'impact": self.impact_categories,
                    "Moyenne": [0] * len(self.impact_categories),
                    "SD": [0] * len(self.impact_categories)
                })
            
            # Générer des données pour chaque matériau manquant
            for mat in missing_materials:
                # Créer un DataFrame pour ce matériau avec des valeurs aléatoires
                material_type = self.categorize_material(mat)
                
                df = template.copy()
                
                # Générer des moyennes et écarts types différents selon le type de matériau
                if material_type == "construction":
                    # Matériaux de construction lourds (béton, brique, etc.)
                    moyennes = np.random.uniform(0.5, 5.0, len(self.impact_categories))
                    sds = np.random.uniform(0.1, 0.5, len(self.impact_categories))
                elif material_type == "wood":
                    # Produits à base de bois
                    moyennes = np.random.uniform(0.2, 3.0, len(self.impact_categories))
                    sds = np.random.uniform(0.1, 0.4, len(self.impact_categories))
                elif material_type == "metal":
                    # Métaux
                    moyennes = np.random.uniform(3.0, 10.0, len(self.impact_categories))
                    sds = np.random.uniform(0.3, 0.7, len(self.impact_categories))
                elif material_type == "insulation":
                    # Matériaux d'isolation
                    moyennes = np.random.uniform(0.3, 2.5, len(self.impact_categories))
                    sds = np.random.uniform(0.1, 0.3, len(self.impact_categories))
                elif material_type == "system":
                    # Systèmes (PV, HVAC, etc.)
                    moyennes = np.random.uniform(5.0, 15.0, len(self.impact_categories))
                    sds = np.random.uniform(0.5, 1.0, len(self.impact_categories))
                else:
                    # Par défaut
                    moyennes = np.random.uniform(0.1, 5.0, len(self.impact_categories))
                    sds = np.random.uniform(0.1, 0.5, len(self.impact_categories))
                
                # Certaines catégories d'impact ont des valeurs plus élevées en général
                for i, category in enumerate(self.impact_categories):
                    if "Climate change" in category:
                        moyennes[i] *= 2.0  # Impact plus élevé pour le changement climatique
                    elif "Resource use" in category:
                        moyennes[i] *= 1.5  # Impact plus élevé pour l'utilisation des ressources
                
                df["Moyenne"] = moyennes
                df["SD"] = sds
                
                # Ajouter les données générées à self.data
                self.data[mat] = df

    def categorize_material(self, material_name):
        """Catégorise un matériau en fonction de son nom pour générer des valeurs cohérentes."""
        material_lower = material_name.lower()
        
        if any(term in material_lower for term in ['wood', 'beam', 'osb', 'plywood', 'lath', 'parquet']):
            return "wood"
        elif any(term in material_lower for term in ['concrete', 'brick', 'block', 'cinder', 'earth', 'mortar']):
            return "construction"
        elif any(term in material_lower for term in ['steel', 'metal', 'aluminum', 'aluminium']):
            return "metal"
        elif any(term in material_lower for term in ['insulation', 'wool', 'xps', 'polystyrene', 'hemp']):
            return "insulation"
        elif any(term in material_lower for term in ['pv', 'hvac', 'dhw', 'battery', 'system']):
            return "system"
        elif any(term in material_lower for term in ['glass', 'glazing']):
            return "glass"
        else:
            return "other"

    def create_simulations(self):
        Simulations = pd.DataFrame()
        Simulations["Catégorie d'impact"] = self.impact_categories

        for mat in self.Materials:
            if mat in self.data.keys():
                dk = self.data[mat].copy()
                Moyenne = pd.to_numeric(dk["Moyenne"], errors='coerce').fillna(0)
                std = pd.to_numeric(dk["SD"], errors='coerce').fillna(0.1)
                
                # Éviter les valeurs extrêmes ou nulles
                std = np.where(std <= 0, 0.1, std)
                
                try:
                    # Utiliser la distribution lognormale pour générer des échantillons
                    lognormal_samples = lognorm(s=std, scale=np.exp(Moyenne)).rvs()
                except:
                    # En cas d'erreur, utiliser une méthode alternative
                    print(f"Erreur lors de la génération des échantillons pour {mat}, utilisation d'une méthode alternative.")
                    lognormal_samples = np.exp(np.random.normal(Moyenne, std))
                
                Simulations[mat] = lognormal_samples

        # Vérifier qu'il n'y a pas de valeurs négatives ou NaN
        Simulations = Simulations.fillna(0)
        for col in Simulations.columns:
            if col != "Catégorie d'impact":
                Simulations[col] = np.maximum(0, Simulations[col])

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
