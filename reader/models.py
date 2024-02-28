import bcrypt
from sqlalchemy import UniqueConstraint

from . import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), unique=True, nullable=False)
    email = db.Column(db.String)
    password = db.Column(db.String)

    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

    shelves = db.relationship('Shelf', backref='user', lazy=True)


class Shelf(db.Model):
    __tablename__ = 'shelves'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(256))
    description = db.Column(db.String(1000))

    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    documents = db.relationship('Document', backref='shelf', lazy=True)

    __table_args__ = (
        UniqueConstraint('name', 'owner_id'),
    )


class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(256))
    enc_iv = db.Column(db.String(32))

    shelf_id = db.Column(db.Integer, db.ForeignKey('shelves.id'), nullable=False)
