import os

class Config:
    SECRET_KEY = 'import os'

class Config:
    SECRET_KEY = '7d3995de71cff150ec91e7ba758d2222f41408ef3e6a57e2'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///isms.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USER')
    MAIL_PASSWORD = os.environ.get('MAIL_PASS')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///isms.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('sawairagohar3012@gmail.com')
    MAIL_PASSWORD = os.environ.get('anyeong819')
