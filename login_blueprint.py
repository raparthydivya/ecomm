from flask import Blueprint, render_template, request, Flask,session
import pandas as pd
from flask_mysqldb import MySQL
import MySQLdb.cursors


login_blueprint = Blueprint("login_blueprint", __name__)

app = Flask(__name__)
mysql = MySQL(app)


@login_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form
        if "username" in data and "password" in data:
            username = data["username"]
            password = data["password"]
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT * FROM user WHERE username = %s AND password = %s",
                (username, password),
            )
            account = cursor.fetchone()

            if account:
                session['loggedin']=True
                
                session['username']=account['username']
                session['user_id']=account['user_id']
                return {
                    "status": "SUCESS",
                    "message": "LOGIN  SUCESSFULLY",
                    "data": "",
                    "traceback": "",
                }
            else:
                return {
                    "status": "FAILURE",
                    "message": "Incorrect username or password",
                    "data": "",
                    "traceback": "",
                }
    return render_template('login.html')
#  Excel
    # if request.method == 'POST':
    #     users=pd.read_excel('open_ecommerce.xlsx', sheet_name='user_data')
    #     username = request.form.get('username')
    #     password = request.form.get('password')
    #     print(users)
    #     for index, row in users.iterrows():
    #         print(row['username'], row['password'])
    #         if str(username) == str(row['username']) and str(password)==str(row['password']):
    #             return "Valid User found"
    #     print(username)
    #     print(password)
    #     return "NO valid user found "
    # return render_template('login.html')
