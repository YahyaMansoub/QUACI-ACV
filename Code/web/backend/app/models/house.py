from app import db


class House(db.Model):
    __tablename__ = 'house'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    space_id = db.Column(db.Integer, db.ForeignKey('space.id'), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)  # Path to CSV file
    simulations_count = db.Column(db.Integer, nullable=False)
    factors_count = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<House {self.name}>'
