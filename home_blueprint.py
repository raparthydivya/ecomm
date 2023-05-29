from flask import Blueprint, render_template, request, Flask,session,redirect
import pandas as pd
from flask_mysqldb import MySQL
import MySQLdb.cursors


home_blueprint = Blueprint("home_blueprint", __name__)

app = Flask(__name__)


mysql = MySQL(app)


@home_blueprint.route("/home", methods=["GET", "POST"])
def home():
   return render_template('home.html')
  