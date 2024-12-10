from flask import Flask, request, session
from flask_admin import Admin
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object('config')

babel = Babel(app, locale_selector=lambda: session.get('lang', 'en'))

admin = Admin(app, template_mode='bootstrap4')

def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return session.get('lang', 'en')

db = SQLAlchemy(app)

migrate = Migrate(app, db)

from app import views, models, forms
