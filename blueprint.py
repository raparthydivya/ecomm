from flask import Blueprint,render_template,request,Flask,redirect,url_for,flash,session
import pandas as pd
user_blueprint= Blueprint('user_blueprint', __name__,static_folder="static",template_folder="templates")
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
mysql = MySQL(app)






@user_blueprint.route('/edit_user/<int:user_id>', methods=['GET','POST'])
def edit_user(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM user WHERE user_id=%s",(user_id,))
    user=cursor.fetchone()
    cursor.close()
    return render_template('user.html',user=user,user_id=user_id)

@user_blueprint.route('/save_user', methods=['POST'])
def save_user():
      if request.method == "POST":
        data = request.form
        username = data["username"]
        password = data["password"]
        mobile = data["mobile"]
        user_id = data['user_id']
        # if user_id:
        #     user_id=int(user_id)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        print(username)
        cursor.execute("UPDATE user SET username=%s,password=%s,mobile=%s WHERE user_id=%s", (username,password,mobile,user_id))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('user_blueprint.user_list'))
      user_id=request.args.get('user_id')
      cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
      cursor.execute("SELECT * FROM user WHERE user_id=%s",(user_id,))
      user=cursor.fetchone()
      cursor.close()
      return render_template('user_details.html',user=user,user_id=user_id)
     
@user_blueprint.route("/user_list",methods=['GET','POST'])
def user_list():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM user")
    users=[]
    for row in cursor.fetchall():
      user={
        'user_id':row['user_id'],
        'username':row['username'],
        'mobile':row['mobile'],
        'password':row['password'],
        'created_date':row['created_date'],
        'updated_date':row['updated_date']
      }
      users.append(user)
      cursor.close()
    return render_template('user_list.html',users=users)
    
    

@user_blueprint.route('/view', methods=['GET','POST'])
def view():
  viewuser_id=request.args.get('user_id')
  cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
  cursor.execute("SELECT * FROM user WHERE user_id=%s",(viewuser_id,))
  user=cursor.fetchone()
  return render_template('view.html',user=user)
  
  
    