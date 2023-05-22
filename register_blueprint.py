from flask import Blueprint,render_template,request,Flask
import pandas as pd
from datetime import datetime
from openpyxl import load_workbook
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
mysql = MySQL(app)

register_blueprint= Blueprint('register_blueprint', __name__)

@register_blueprint.route('/register',methods=['GET','POST'])
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
                     return {
                    "status": "SUCCESS",
                    "message": "username or mobilenumber exists",
                    "data": "",
                    "traceback": "",
                }
                else:
                  cursor.execute(
                    "INSERT INTO user( username,mobile,password) VALUES(%s,%s,%s)",
                    (username, mobile, password),
                )
                mysql.connection.commit()
                return {
                    "status": "SUCESS",
                    "message": "REGISTERED SUCESSFULLY",
                    "data": "",
                    "traceback": "",
                }
        return ' '
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
#     if request.method == 'POST':
#         users=pd.read_excel('open_ecommerce.xlsx', sheet_name='user_data')
#         username = request.form.get('username')
#         password = request.form.get('password')
#         mobile=request.form.get('mobile')
#         registration_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         if username in users["username"].values:
#                 return {
#                 'status':'failure',
#                 'message':'Username already exits',
#                 'data':'Register with other username',
#                 'traceback':''
#                 }
#         if mobile in users["mobile"].values:
#                 return {
#                 'status':'failure',
#                 'message':'Mobilenumber already exits',
#                 'data':'' ,
#                 'traceback':''
#                 }
#         print(users['user_id'].max())
#         max_user_id=users['user_id'].max()
#         new_id = max_user_id+1
            
#         wb=load_workbook('open_ecommerce.xlsx')
#         ws=wb.active
#         ws.append([new_id,username,password,mobile,registration_date,registration_date])
#         wb.save('open_ecommerce.xlsx')
#         return {
#                 'status':'succes',
#                 'message':'Registration Successful',
#                 'data':{ "user_id":int(new_id)
#                     },'traceback':''
#                 }
#     return render_template('register.html')