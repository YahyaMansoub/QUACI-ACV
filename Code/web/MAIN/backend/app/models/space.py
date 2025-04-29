from app import db


class Space(db.Model):
    __tablename__ = 'space'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    factors = db.Column(db.JSON, nullable=False)  # List of CSV column names
    houses = db.relationship('House', backref='space',
                             lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Space {self.name}>'
