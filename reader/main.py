import os

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

from . import db
from .models import Shelf, Document

main = Blueprint('main', __name__)
UPLOADS = "C:\\Users\\Piotr\\PycharmProjects\\SafeRead\\backend\\uploads"


@main.route('/shelf/<name>/<doc>', methods=['POST'])
@jwt_required()
def upload_file(name, doc):
    file = request.files['file']
    # iv = request.form['iv']
    # if not iv:
    #     return {"err": "Invalid request, try again"}, 400

    owner = get_jwt_identity()
    shelf = db.session.query(Shelf).filter_by(owner=owner) \
        .filter_by(name=name).first()
    if not shelf:
        return {"err": "Shelf not found"}, 404

    if file.filename == '':
        return {"err": "Invalid file"}, 400

    if not all(c in 'abcdef0123456789' for c in file.filename) or file.filename != doc:
        return {"err": "Invalid request, try again"}, 400

    try:
        document = Document(title=doc, shelf_id=shelf.id)
        db.session.add(document)

        # Save file
        if not os.path.isdir(UPLOADS):
            os.mkdir(UPLOADS)
        if not os.path.isdir(f'{UPLOADS}/{owner}'):
            os.mkdir(f'{UPLOADS}/{owner}')
        file.save(f"{UPLOADS}/{owner}/{secure_filename(file.filename)}")

        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()

    return {"doc": doc}, 200


@main.route('/shelf', methods=['POST'])
@jwt_required()
def add_shelf():
    data = request.json
    name = data['name']
    description = data['description']
    owner = get_jwt_identity()
    shelf = db.session.query(Shelf).filter_by(owner=owner).filter_by(name=name).first()
    if shelf:
        return {"err": f"{shelf} already exists"}, 409

    shelf = Shelf(name=name, description=description, owner=owner)

    try:
        db.session.add(shelf)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

    return {"shelf": name}, 201


@main.route('/shelf/<name>/<doc>', methods=['PUT'])
@jwt_required()
def update_page(name, doc):
    owner = get_jwt_identity()
    page = request.json['page']
    shelf = db.session.query(Shelf).filter_by(owner=owner).filter_by(name=name).first()
    if not shelf:
        return {'err': 'No such shelf'}, 400
    doc = db.session.query(Document).filter_by(shelf_id=shelf.id).filter_by(title=doc).first()
    if not doc:
        return {'err': 'No such document'}
    doc.page = page
    db.session.commit()
    return {'page': page}, 200


@main.route('/shelf', methods=['GET'])
@jwt_required()
def get_shelves():
    owner = get_jwt_identity()
    shelves = db.session.query(Shelf).filter_by(owner=owner).all()
    return jsonify([{'name': shelf.name, 'description': shelf.description} for shelf in shelves])


@main.route('/shelf/<name>/<doc>', methods=['GET'])
@jwt_required()
def document(name, doc):
    owner = get_jwt_identity()
    shelf = db.session.query(Shelf).filter_by(owner=owner).filter_by(name=name).first()
    document = db.session.query(Document).filter_by(shelf_id=shelf.id).filter_by(title=doc).first()
    resp = send_file(f'{UPLOADS}/{owner}/{secure_filename(document.title)}')
    resp.headers.add('Page', document.page if document.page is not None else 1)
    return resp


@main.route('/shelf/<name>/<doc>/page', methods=['GET'])
@jwt_required()
def iv(name, doc):
    owner = get_jwt_identity()
    shelf = db.session.query(Shelf).filter_by(owner=owner).filter_by(name=name).first()
    document = db.session.query(Document).filter_by(shelf_id=shelf.id).filter_by(title=doc).first()
    return jsonify({"page": document.page})


@main.route('/shelf/<name>', methods=['GET'])
@jwt_required()
def documents(name):
    owner = get_jwt_identity()
    shelf = db.session.query(Shelf).filter_by(owner=owner).filter_by(name=name).first()
    docs = db.session.query(Document).filter_by(shelf_id=shelf.id).all()
    return jsonify([{"title": doc.title} for doc in docs])

@main.route('/test', methods=['GET'])
def test():
    import time
    time.sleep(5)
    return send_file('pan-tadeusz.pdf')