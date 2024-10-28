import scrython
import requests

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

@bp.route('/collection/<int:collection_id>/add', methods=('GET', 'POST'))
@login_required
def add_card(collection_id):
    if request.method == 'POST':
        card_name = request.form['card_name']
        error = None

        if not card_name:
            error = 'Card name is required.'
        else:
            try:
                # Make a synchronous request to Scryfall API
                response = requests.get(f'https://api.scryfall.com/cards/named?fuzzy={card_name}')
                response.raise_for_status()  # Raise an exception for bad status codes
                card_data = response.json()

                db = get_db()

                existing_card = db.execute(
                    'SELECT id FROM card WHERE name = ? AND collection_id = ?',
                    (card_data['name'], collection_id)
                ).fetchone()

                if existing_card:
                    error = f"Card '{card_data['name']}' already exists in this collection."
                else:
                    db.execute(
                        'INSERT INTO card (name, `set`, mana_cost, type, rarity, image_url, collection_id)'  # Enclose 'set' in backticks
                        ' VALUES (?, ?, ?, ?, ?, ?, ?)',
                        (card_data['name'], card_data['set'], card_data['mana_cost'],
                         card_data['type_line'], card_data['rarity'], card_data['image_uris']['normal'], collection_id)
                    )
                    db.commit()

                    flash(f"Card '{card_data['name']}' added to the collection!")
                    return redirect(url_for('mtg.collections'))

            except requests.exceptions.RequestException as e:
                error = f"Error fetching card data: {e}"

        flash(error)

    return render_template('mtg/add_card.html', collection_id=collection_id)

@bp.route('/collections/<int:collection_id>')
@login_required
def collection(collection_id):
    db = get_db()
    collections = db.execute(
        'SELECT *'
        ' FROM collection'
        ' WHERE id = ?', (collection_id,)
    ).fetchone()

    if collections is None:
        abort(404, f"Collection id {collection_id} doesn't exist.")

    cards = db.execute(
        'SELECT * FROM card WHERE collection_id = ?', (collection_id,)
    ).fetchall()

    return render_template('mtg/collection.html', cards=cards, collection=collections)