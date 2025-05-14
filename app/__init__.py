from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import DeclarativeBase
from os import environ
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from sqlalchemy_utils import database_exists, create_database
from dotenv import load_dotenv

load_dotenv(override=True)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
bcrypt = Bcrypt()
jwt = JWTManager()
migrate = Migrate()


def create_app(config=None):
    app = Flask(__name__)

    url = environ.get("POSTGRESQL_URL")
    if not url:
        raise ValueError("POSTGRESQL_URL environment variable is not set")

    try:
        if not database_exists(url):
            create_database(url)
            print(f"Database created successfully at {url}")
        else:
            print("Database already exists")
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        raise

    app.config.update(
        SQLALCHEMY_DATABASE_URI=url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY=environ.get("SECRET_KEY"),
        SECRET_KEY=environ.get("SECRET_KEY"),
    )

    if config:
        app.config.update(config)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.accounts import accounts_bp
    from app.routes.transactions import transactions_bp
    from app.swagger import swagger_ui_blueprint

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(accounts_bp, url_prefix='/api/accounts')
    app.register_blueprint(transactions_bp, url_prefix='/api/transactions')
    app.register_blueprint(swagger_ui_blueprint)

    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Error creating tables: {str(e)}")
            raise

    return app
