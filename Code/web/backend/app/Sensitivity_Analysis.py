import copy
import pandas as pd
from quaci_class import QUACI


class SensitivityAnalyzer:
    def __init__(self, base_quaci: QUACI):
        self.base_quaci = base_quaci
        self.parameters = self._get_parameters()
        self.baseline = None
        self.results = pd.DataFrame()

    def _get_parameters(self):
        """Extract parameters for sensitivity analysis"""
        params = {
            'materials': list(self.base_quaci.comp_quantity.columns),
            'lifespan_params': ['dur_vie_mean', 'dur_vie_std_dev']
        }
        return params

    def _run_quaci_simulation(self, modified_quaci_params: dict):
        """Run QUACI simulation with modified parameters"""
        q = copy.deepcopy(self.base_quaci)

        # Modify parameters
        for param, value in modified_quaci_params.items():
            if param in ['dur_vie_mean', 'dur_vie_std_dev']:
                setattr(q, param, value)
            elif param in self.parameters['materials']:
                q.comp_quantity[param] = value

        # Run simulation
        result = q.final(q.comp_quantity.index[0])
        # Use mean of Row Total as output metric
        return result['Row Total'].mean()

    def run_analysis(self, perturbation_percent=0.1):
        """Perform OAT sensitivity analysis"""
        # Run baseline
        self.baseline = self._run_quaci_simulation({})

        # Analyze materials
        sensitivity = {}
        for material in self.parameters['materials']:
            original_value = self.base_quaci.comp_quantity[material].iloc[0]
            perturbed_value = original_value * (1 + perturbation_percent)

            # Run perturbed simulation
            modified_params = {material: perturbed_value}
            perturbed_output = self._run_quaci_simulation(modified_params)

            # Calculate sensitivity index
            delta_Y = perturbed_output - self.baseline
            delta_X = perturbation_percent
            SI = (delta_Y / self.baseline) / delta_X
            sensitivity[material] = SI

        # Analyze lifespan parameters
        for param in self.parameters['lifespan_params']:
            original_value = getattr(self.base_quaci, param)
            perturbed_value = original_value * (1 + perturbation_percent)

            # Run perturbed simulation
            modified_params = {param: perturbed_value}
            perturbed_output = self._run_quaci_simulation(modified_params)

            # Calculate sensitivity index
            delta_Y = perturbed_output - self.baseline
            delta_X = perturbation_percent
            SI = (delta_Y / self.baseline) / delta_X
            sensitivity[param] = SI

        # Calculate relative influence
        total_SI = sum(abs(si) for si in sensitivity.values())
        self.results = pd.DataFrame({
            'Parameter': sensitivity.keys(),
            'SI': sensitivity.values(),
            'RI': [abs(si)/total_SI for si in sensitivity.values()]
        }).sort_values('RI', ascending=False)

        return self.results

    def get_most_influential(self, n=5):
        """Get top n most influential parameters"""
        return self.results.head(n)


'''
This Portion is only made for testing. 
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


# Create base QUACI instance
base_quaci = QUACI(
    comp_quantity=df.loc["Hemp"],
    dur_vie_mean=50.0,
    dur_vie_std_dev=2.5,
    path='Material_Statistics'
)

# Perform sensitivity analysis
analyzer = SensitivityAnalyzer(base_quaci)
results = analyzer.run_analysis(perturbation_percent=0.1)  # 10% perturbation

# Get results
print("Full results:")
print(results)

print("\nTop 5 influential parameters:")
print(analyzer.get_most_influential(5))
'''
