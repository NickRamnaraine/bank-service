from flask import Flask
from dotenv import load_dotenv
import os
from .models import db
from .routes import init_routes

# Load environment variables from .env file
load_dotenv()

# Creating and configuring the app
def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bank.db"
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


    # Initalize the app
    db.init_app(app)

    # Creating the tables in sqlite
    with app.app_context():
        db.create_all()

    init_routes(app)

    return app
    