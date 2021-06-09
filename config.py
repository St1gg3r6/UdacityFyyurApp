import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL - DONE 31/05/21
SQLALCHEMY_DATABASE_URI = 'postgresql://stephenusher@localhost:5432/fyyurdev'
