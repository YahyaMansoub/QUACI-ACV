import os


class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'  # Path to your SQLite database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'instance/data'
