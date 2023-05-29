from flask import Blueprint,render_template,request,Flask,redirect,url_for,flash,session
import mysql.connector
import pandas as pd
user_blueprint= Blueprint('user_blueprint', __name__,static_folder="static",template_folder="templates")
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
mysql = MySQL(app)

# @user_blueprint.route('/get_user/<ids>')

# def get_user(ids):
#     id_list=[int(id) for id in ids.split(',')]
#     details=pd.read_excel('open_ecommerce.xlsx',sheet_name='user_data')
#     user_data=details[details['user_id'].isin(id_list)]
#     data={
#         'users':[],
#         'missing_users':[]
       
#     }
#     for id in id_list:
#         for index,row in user_data.iterrows():
#             if row['user_id']==id:
#                users={
#                 'user_id':row['user_id'],
#                 'username':row['username'],
#                 'mobile':row['mobile'],
#                 'password':row['password']
#                 }
#                data['users'].append(users)
#                break
#             else:
#                 data['missing_users'].append(id)
             
#     return{
#             'status':'sucess',
#             'message':'User Details',
#             'data': data,
#             'traceback':''
#     }
    
# mysql = MySQL(app)
# @user_blueprint.route('/user_address', methods=['GET','POST'])
# def user_address():
#     if request.method == "POST":
#         data = request.json
#         if data and 'user_id' in data and 'street_name' in data and 'city' in data and 'state' in data and 'country' in data and 'postal_code' in data:
#             user_id=data['user_id']
#             street_name=data['street_name']
#             city=data['city']
#             state=data['state']
#             country=data['country']
#             postal_code=data['postal_code']
            
#             cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#             cursor.execute(
#                 'SELECT * FROM address WHERE user_id=%s AND street_name=%s AND city=%s AND state=%s AND country=%s AND postal_code=%s',(user_id,street_name,city,state,country,postal_code))
        
#             existing_user=cursor.fetchone()
            
#             if existing_user:
#                     return{
#                         'status':'failure',
#                 'message':'User address already exists',
#                 'data': '',
#                 'traceback':''
                        
#                     }
#             else:
#                     cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#                     cursor.execute(
#                     'INSERT INTO address(user_id,street_name,city,state,country,postal_code) VALUES(%s,%s,%s,%s,%s,%s)',(user_id,street_name,city,state,country,postal_code)
#                     )
#                     mysql.connection.commit()
               

#             return {
#                 'status':'sucess',
#                 'message':'User address added successfully',
#                 'data': '',
#                 'traceback':''
#                 }
        
@user_blueprint.route('/edit_user/<int:user_id>', methods=['GET','POST'])
def edit_user(user_id):
  print(user_id)
  # user_id=session.get('user_id')
  print(user_id)
  cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
  q=f" SELECT * FROM user WHERE 'user_id'={user_id}"
  print(q)
  print(session)
  cursor.execute(q)
  user=cursor.fetchone()
  cursor.close()
  if user_id!=session['user_id']:
    return render_template('error.html',message='You are not authorized to edit this user')
  return render_template('edit.html',user=user,user_id=user_id)
 
@user_blueprint.route('/save_user/<int:user_id>', methods=['POST'])
def save_user(user_id):
      if request.method == "POST":
        data = request.form
        username = data["username"]
        password = data["password"]
        mobile = data["mobile"]
        user_id = data["user_id"]
        # created_date=data["created_date"]
        # updated_date=data["updated_date"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("UPDATE user SET username=%s,password=%s,mobile=%s,updated_date={date} WHERE user_id=%s", (username,password,mobile,user_id))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('user_blueprint.user_list'))
      user_id=request.args.get('user_id')
      cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
      cursor.execute("SELECT * FROM user WHERE user_id=%s",(user_id,))
      user=cursor.fetchone()
      cursor.close()
      return render_template('edit.html',user=user,user_id=user_id)
     
@user_blueprint.route("/user_list",methods=['GET','POST'])
def user_list():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM user")
    data=cursor.fetchall()
    cursor.close()  
    users=[]
    for row in data:
      user={
        'user_id':row['user_id'],
        'username':row['username'],
        'mobile':row['mobile'],
        'password':row['password'],
        'created_date':row['created_date'],
        'updated_date':row['updated_date']
      }
      users.append(user)   
    return render_template('user_list.html',users=users,)
    
@user_blueprint.route('/view/<int:user_id>',methods=['GET'])
def view(user_id):
  if user_id!=session['user_id']:
    return render_template('error.html',message='You are not authorized to view this user')
  # user_id=session.get('user_id')
  # viewuser_id=request.args.get('user_id')
  cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
  cursor.execute("SELECT * FROM user WHERE user_id=%s",(user_id,))
  user=cursor.fetchone()
  cursor.close()
  
  return render_template('view.html',user=user,user_id=user_id)
  
    