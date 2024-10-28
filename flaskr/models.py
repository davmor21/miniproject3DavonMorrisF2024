from flaskr.db import db

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    set = db.Column(db.String(20), nullable=False)
    mana_cost = db.Column(db.String(50))
    type = db.Column(db.String(50))
    rarity = db.Column(db.String(20))
    image_url = db.Column(db.String(200))

    def __repr__(self):
        return f'<Card {self.name}>'