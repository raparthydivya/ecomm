from flask import Blueprint, render_template, request, Flask,redirect,flash
import pandas as pd
from datetime import datetime
from openpyxl import load_workbook
from flask_mysqldb import MySQL
from flask import Flask, session
import MySQLdb.cursors

app = Flask(__name__)
mysql = MySQL(app)

register_blueprint = Blueprint("register_blueprint", __name__)


@register_blueprint.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.form
        if data and "username" in data and "password" in data and "mobile" in data:
            username = data["username"]
            password = data["password"]
            mobile = data["mobile"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT * FROM user WHERE username = %s OR mobile = %s",
            (username, mobile),
        )
        account = cursor.fetchone()

        if account:
            flash("username or mobilenumber exists")
            return render_template(
                "error.html", message="username or mobilenumber already exists"
            )
        #      {
        #             "status": "FAILURE",
        #             "message": "username or mobilenumber exists",
        #             "data": "",
        #             "traceback": "",
        #         }
        else:
            cursor.execute(
                "INSERT INTO user( username,mobile,password) VALUES(%s,%s,%s)",
                (username, mobile, password),
            )
        mysql.connection.commit()
        flash("You are registered successfully")
        return redirect("/login")
    # {
    #         "status": "SUCESS",
    #         "message": "REGISTERED SUCESSFULLY",
    #         "data": "",
    #         "traceback": "",
    #     }
    return render_template("register.html")


