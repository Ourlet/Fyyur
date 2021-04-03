from dotenv import load_dotenv
load_dotenv()

import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

# IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://' + os.environ['USER'] + ':' + os.environ['PASSWORD'] + '@localhost:5432/fyyur'