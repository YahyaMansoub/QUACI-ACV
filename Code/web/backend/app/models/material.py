
from app import db

class Material(db.Model):
    __tablename__ = 'material'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    impact_values = db.Column(db.JSON, nullable=False)  # Dictionnaire catégorie → valeur
    unit = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<Material {self.name}>'

    def get_impact(self, category):
        return self.impact_values.get(category, 0)

    def get_impact_unit(self, category):
        return self.unit

    def sample_impact(self, category):
        import numpy as np
        mean = self.get_impact(category)
        # échantillonnage normal autour de la moyenne
        std = mean * 0.1 if mean else 0
        return float(np.random.normal(mean, std))
