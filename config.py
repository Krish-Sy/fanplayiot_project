import os

class Config:
    SECRET_KEY = 'abc@123'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
    #'sqlite:///events.db'
    #postgresql://...
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    API_KEY= os.environ.get('API_KEY')
