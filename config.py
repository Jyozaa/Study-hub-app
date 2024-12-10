import os

WTF_CSRF_ENABLED = True
SECRET_KEY = 'a-very-secret-secret'
SESSION_TYPE = 'filesystem'

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
SQLALCHEMY_TRACK_MODIFICATIONS = True   

