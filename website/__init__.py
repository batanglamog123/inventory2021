from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import FileField
from flask_uploads import configure_uploads, IMAGES, UploadSet
from flask_cors import CORS, cross_origin
from os.path import join, dirname, realpath

UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/item_images')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

db = SQLAlchemy()
migrate = Migrate()
DB_NAME = 'inventory2021_db.db'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'inventory_system_2021'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['UPLOADED_IMAGES_DEST'] = 'website/static/item_images'
    
    from .inventory import inventory, images
    from .auth import auth, images
    from .item_approval import approval, images
    from .management import management

    configure_uploads(app, images)
    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    # DB
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    migrate.init_app(app, db)

    # VIEWS
    app.register_blueprint(inventory, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(approval, url_prefix='/')
    app.register_blueprint(management, url_prefix='/')

    cors.init_app(inventory, resources={r"/*": {"origins": "*", "supports_credentials": True}})

    # Create DB
    from .models import User, Item
    create_database(app)

    # LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Database Created!')