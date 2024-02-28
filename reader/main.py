import os

from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from . import db
from .models import Shelf, Document

main = Blueprint('main', __name__)
UPLOADS = "C:\\Users\\Piotr\\PycharmProjects\\SafeRead\\uploads"


@main.route('/', methods=['GET'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    return render_template('index.html')


@main.route('/home', methods=['GET'])
@login_required
def home():
    shelves = current_user.shelves
    return render_template('home.html', shelves=shelves)


@main.route('/upload', methods=['POST'])
@login_required
def upload():
    file = request.files['file']
    shelf_name = request.form['shelfName']
    iv = request.form['iv']
    shelf = db.session.query(Shelf).filter_by(owner_id=current_user.id) \
        .filter_by(name=shelf_name).first()
    if not shelf:
        flash('Invalid shelf')
        return 'Invalid shelf', 400

    if file.filename == '':
        flash('No selected file')
        return 'Invalid file', 400

    if not all(c in 'abcdef0123456789' for c in file.filename):
        return "", 400

    try:
        document = Document(title=file.filename, shelf_id=shelf.id, enc_iv=iv)
        db.session.add(document)
        if not os.path.isdir(f'{UPLOADS}/{current_user.username}'):
            os.mkdir(f'{UPLOADS}/{current_user.username}')
        file.save(f"{UPLOADS}/{current_user.username}/{secure_filename(file.filename)}")
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()

    return 'ok', 200


@main.route('/shelf', methods=['GET', 'POST'])
@login_required
def add_shelf():
    data = request.form
    name = data['shelfName']
    description = data['shelfDescription']
    shelf = Shelf(name=name, description=description, owner_id=current_user.id)
    try:
        db.session.add(shelf)
        db.session.commit()
    except Exception as e:
        return f"You already have shelf named {name}", 400
    return redirect(url_for('main.home'))


@main.route('/shelf/<name>', methods=['GET'])
@login_required
def shelf(name):
    return render_template('shelf.html', shelf_name=name, username=current_user.username)


@main.route('/shelf/<name>/<doc>/display', methods=['GET'])
@login_required
def get_document(name, doc):
    return render_template('pdf.html', name=name)


@main.route('/shelf/<name>/<doc>', methods=['GET'])
@login_required
def document(name, doc):
    shelf = db.session.query(Shelf).filter_by(owner_id=current_user.id).filter_by(name=name).first()
    document = db.session.query(Document).filter_by(shelf_id=shelf.id).filter_by(title=doc).first()
    return send_file(f'{UPLOADS}/{current_user.username}/{document.title}')


@main.route('/shelf/<name>/<doc>/iv', methods=['GET'])
@login_required
def iv(name, doc):
    shelf = db.session.query(Shelf).filter_by(owner_id=current_user.id).filter_by(name=name).first()
    document = db.session.query(Document).filter_by(shelf_id=shelf.id).filter_by(title=doc).first()
    return jsonify({"iv": document.enc_iv})


@main.route('/shelf/<name>/docs', methods=['GET'])
@login_required
def documents(name):
    results_per_page = 10
    try:
        current_page = int(request.args.get('page'))
    except TypeError:
        return "Invalid page", 400
    except KeyError:
        current_page = 0

    shelf = db.session.query(Shelf).filter_by(owner_id=current_user.id).filter_by(name=name).first()
    docs = db.session.query(Document).filter_by(shelf_id=shelf.id) \
        .offset(results_per_page * current_page).limit(results_per_page).all()

    return jsonify([{"title": doc.title, "iv": doc.enc_iv} for doc in docs])
