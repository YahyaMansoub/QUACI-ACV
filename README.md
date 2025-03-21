# Comparative Building Life Cycle Assessment (LCA) with Uncertainty Analysis

This repository implements the methodology proposed in the paper "Dealing with uncertainties in comparative building life cycle assessment" by Marie-Lise Pannier et al. The goal is to perform a comparative Life Cycle Assessment (LCA) of building design alternatives while accounting for uncertainties. The methodology involves Sensitivity Analysis (SA) and Uncertainty Analysis (UA) to identify influential factors and assess the reliability of the results.

## Methodology Overview

The methodology consists of the following steps:

1. **Selection of Alternatives and LCA Model**:
   - Define the building design alternatives.
   - Build the LCA model to compare alternatives based on the same functional unit.

2. **Identification of Uncertain Factors**:
   - List all uncertain factors affecting the LCA model.
   - Characterize uncertainties using uniform distributions or data from literature.

3. **Sensitivity Analysis (SA)**:
   - Perform SA to identify the most influential uncertain factors.
   - Use the Morris method adapted for comparative LCA.

4. **Improvement of Uncertainty Characterization**:
   - Refine the uncertainty characterization for the most influential factors.
   - Update distributions based on more precise data.

5. **Uncertainty Analysis (UA)**:
   - Perform UA using dependent sampling (e.g., Sobol sequences).
   - Compare alternatives using various metrics (e.g., discernibility analysis, Heijungs significance metric).

## Python Implementation

The implementation in Python can be structured as follows:

### 1. Define Alternatives and LCA Model
```python
# Define building design alternatives
alternatives = {
    "Concrete": {"materials": {...}, "energy_use": {...}},
    "Wooden-Framed": {"materials": {...}, "energy_use": {...}},
    "Concrete Blocks": {"materials": {...}, "energy_use": {...}}
}

# Define LCA model
def lca_model(alternative):
    # Calculate environmental impacts based on alternative
    return impacts
