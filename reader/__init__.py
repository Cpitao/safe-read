from datetime import timedelta, datetime, timezone

from flask import Flask
from flask_jwt_extended import JWTManager, get_jwt, create_access_token, get_jwt_identity, set_access_cookies
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config['SECRET_KEY'] = 'SECRET_KEY_THIS_IS'  # @TODO later
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reader.db'
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['JWT_SECRET_KEY'] = 'aedfnuisfbdnawjisvnklfebacnsdjocjxamszklnsa'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    jwt = JWTManager(app)

    db.init_app(app)

    @app.after_request
    def refresh_expiring_jwts(response):
        try:
            exp_timestamp = get_jwt()["exp"]
            now = datetime.now(timezone.utc)
            target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
            if target_timestamp > exp_timestamp:
                access_token = create_access_token(identity=get_jwt_identity())
                set_access_cookies(response, access_token)
            return response
        except (RuntimeError, KeyError):
            # Case where there is not a valid JWT. Just return the original response
            return response

    from .models import User

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app


app = create_app()
with app.app_context():
    db.create_all()
