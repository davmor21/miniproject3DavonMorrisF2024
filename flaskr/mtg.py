import scrython
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db  # Import get_db

bp = Blueprint('mtg', __name__)

@bp.route('/')
def index():
    db = get_db()  # Get the database connection
    cards = db.execute(
        'SELECT * FROM card'  # Your SQL query to fetch cards
    ).fetchall()
    return render_template('mtg/collection.html', cards=cards)

@bp.route('/add', methods=('GET', 'POST'))
@login_required
def add():
    if request.method == 'POST':
        card_name = request.form['card_name']
        error = None

        if not card_name:
            error = 'Card name is required.'
        else:
            try:
                card = scrython.cards.Named(fuzzy=card_name)
                db = get_db()  # Get the database connection

                # Check if the card already exists (using SQL query)
                existing_card = db.execute(
                    'SELECT id FROM card WHERE name = ?', (card.name(),)
                ).fetchone()

                if existing_card:
                    error = f"Card '{card.name()}' already exists in your collection."
                else:
                    db.execute(
                        'INSERT INTO card (name, set, mana_cost, type, rarity, image_url)'
                        ' VALUES (?, ?, ?, ?, ?, ?)',
                        (card.name(), card.set_code(), card.mana_cost(),
                         card.type_line(), card.rarity(), card.image_uris()['normal'])
                    )
                    db.commit()

                    flash(f"Card '{card.name()}' added to your collection!")
                    return redirect(url_for('mtg.index'))

            except scrython.ScryfallError as e:
                error = f"Error fetching card data: {e}"

        flash(error)

    return render_template('mtg/add.html')