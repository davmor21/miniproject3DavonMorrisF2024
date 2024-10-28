from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    card_type = db.Column(db.String(50), nullable=False)
    set_name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Card {self.name}>'
