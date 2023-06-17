from flask import Blueprint, render_template, request, Flask,session,redirect
import pandas as pd
from flask_mysqldb import MySQL
import MySQLdb.cursors
from cart_blueprint import addproduct_cart



home_blueprint = Blueprint("home_blueprint", __name__)


app = Flask(__name__)


mysql = MySQL(app)

@home_blueprint.route("/home", methods=["GET", "POST"])
def home():
   current_page='home'
   cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
   cursor.execute(
                    "SELECT * FROM product limit 12"
                  
                )
   products = cursor.fetchall()
   # product_id=request.args.get('product_id')
   cursor.close()
   return render_template('home.html',products=products,current_page=current_page)
  
# @home_blueprint.route("/addproduct_cart/<int:product_id>")
# def addproduct_cart(product_id):