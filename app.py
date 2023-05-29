from flask import Flask, request, redirect, json, jsonify,render_template,url_for
from login_blueprint import login_blueprint
from register_blueprint import register_blueprint
from company_blueprint import company_blueprint
from product_blueprint import product_blueprint
from cart_blueprint import cart_blueprint
from wishlist_blueprint import wishlist_blueprint
from user_blueprint import user_blueprint
from home_blueprint import home_blueprint

import pandas as pd
import numpy as np
from openpyxl import load_workbook
from datetime import datetime
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = "key"


app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "password"
app.config["MYSQL_DB"] = "ecomm"

mysql = MySQL(app)

app.register_blueprint(login_blueprint)
app.register_blueprint(register_blueprint)
app.register_blueprint(company_blueprint)
app.register_blueprint(product_blueprint)
app.register_blueprint(cart_blueprint)
app.register_blueprint(wishlist_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(home_blueprint)


@app.route("/")
def hello():
    return render_template('base.html')











if __name__ == "__main__":
    app.run(port=5004, debug=True)



