from flask import Blueprint, render_template, request, Flask,session,redirect,flash,url_for
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
                (username, password)
            )
            account = cursor.fetchone()

            if account:
                session['logged_in']= True 
                session['username']=account['username']
                session['user_id']=account['user_id']
                return redirect("/home")
                #     "status": "SUCESS",
                #     "message": "LOGIN  SUCESSFULLY",
                #     "data": "",
                #     "traceback": "",
                # }
            else:
                return render_template('error.html',message=" Incorrect username or password")
            # {
            #         "status": "FAILURE",
            #         "message": "Incorrect username or password",
            #         "data": "",
            #         "traceback": "",
            #     }
    return render_template('login.html')


@login_blueprint.route("/logout", methods=["GET", "POST"])
def logout():
    user_id=session.get('user_id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM user WHERE user_id=%s",(user_id,))
    user=cursor.fetchone()
    session.clear()
    flash('you are logged out','success')
    return redirect('/home')
    






























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
