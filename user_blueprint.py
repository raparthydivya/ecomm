from flask import Blueprint,render_template,request
import pandas as pd
user_blueprint= Blueprint('user_blueprint', __name__)
from flask_mysqldb import MySQL
import MySQLdb.cursors
mysql = MySQL(app)
@user_blueprint.route('/get_user/<ids>')

def get_user(ids):
    id_list=[int(id) for id in ids.split(',')]
    details=pd.read_excel('open_ecommerce.xlsx',sheet_name='user_data')
    user_data=details[details['user_id'].isin(id_list)]
    data={
        'users':[],
        'missing_users':[]
       
    }
    for id in id_list:
        for index,row in user_data.iterrows():
            if row['user_id']==id:
               users={
                'user_id':row['user_id'],
                'username':row['username'],
                'mobile':row['mobile'],
                'password':row['password']
                }
               data['users'].append(users)
               break
            else:
                data['missing_users'].append(id)
             
    return{
            'status':'sucess',
            'message':'User Details',
            'data': data,
            'traceback':''
    }
    
mysql = MySQL(app)
@user_blueprint.route('/user_address', methods=['GET','POST'])
def user_address():
    if request.method == "POST":
        data = request.json
        if data and 'user_id' in data and 'street_name' in data and 'city' in data and 'state' in data and 'country' in data and 'postal_code' in data:
            user_id=data['user_id']
            street_name=data['street_name']
            city=data['city']
            state=data['state']
            country=data['country']
            postal_code=data['postal_code']
            
            cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                'SELECT * FROM address WHERE user_id=%s AND street_name=%s AND city=%s AND state=%s AND country=%s AND postal_code=%s',(user_id,street_name,city,state,country,postal_code))
        
            existing_user=cursor.fetchone()
            
            if existing_user:
                return{
                    'status':'failure',
            'message':'User address already exists',
            'data': '',
            'traceback':''
                    
                }
            else:
                cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(
                'INSERT INTO address(user_id,street_name,city,state,country,postal_code) VALUES(%s,%s,%s,%s,%s,%s)',(user_id,street_name,city,state,country,postal_code)
                )
                mysql.connection.commit()
               

                return {
                'status':'sucess',
                'message':'User address added successfully',
                'data': '',
                'traceback':''
                }
                
        