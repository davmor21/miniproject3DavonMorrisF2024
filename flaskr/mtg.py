from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('mtg', __name__)

@bp.route('/')
def index():
    return render_template('mtg/index.html')

@bp.route('/collections')
@login_required
def collections():
    db = get_db()
    collections = db.execute(
        'SELECT *'
        ' FROM collection'
        ' WHERE user_id = ?', (g.user['id'],)
    ).fetchall()
    return render_template('mtg/collections.html', collections=collections)

@bp.route('/create_collection', methods=('GET', 'POST'))
@login_required
def create_collection():
    if request.method == 'POST':
        name = request.form['name']
        error = None

        if not name:
            error = 'Collection name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO collection (name, user_id)'
                ' VALUES (?, ?)',
                (name, g.user['id'])
            )
            db.commit()
            return redirect(url_for('mtg.collections'))

    return render_template('mtg/create_collection.html')

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
                db = get_db()

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