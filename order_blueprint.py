from flask import Blueprint,render_template,request,Flask,redirect,url_for,flash,session
from datetime import datetime
import mysql.connector
import pandas as pd
order_blueprint= Blueprint('order_blueprint', __name__)
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
mysql = MySQL(app)


@order_blueprint.route("/place_order/<int:product_id>", methods=["POST","GET"])
def place_order(product_id):   
        if "logged_in" not in session or not session["logged_in"]:
            return redirect("/login")
        else:
    
                user_id = session["user_id"]
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
                cursor.execute(f"SELECT * FROM product WHERE product_id={product_id}")
                products= cursor.fetchone()
                
                
                cursor.execute(f"SELECT * FROM address WHERE user_id={user_id}")
                addresses= cursor.fetchall()
                cursor.close()
                
                
                if not addresses:
                    return redirect(url_for("user_blueprint.add_address"))
                    
                        
        return render_template('order.html',addresses=addresses,product_id=product_id,products=products)
       
    
@order_blueprint.route("/submit_order/<int:product_id>", methods=["POST","GET"])
def submit_order(product_id):
    if request.method == "POST":
        if "logged_in" not in session or not session["logged_in"]:
           return redirect("login")
        
        else:
          cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
          cursor.execute(f"SELECT * FROM product WHERE product_id={product_id}")
          product= cursor.fetchone()
          user_id = session["user_id"]
          address_id=request.form.get('address_id')
          status='order placed'
          cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
          cursor.execute(
                    "INSERT INTO orders (user_id,product_id,amount,address_id,status) VALUES (%s,%s,%s,%s,%s)",(user_id,product_id,product['amount'],address_id,status)
            
                  )
          mysql.connection.commit()
          cursor.close()
          message='Order placed successfullly'
          alert_class='success'
          
        return redirect(url_for("order_blueprint.view_order",message=message,alert_class=alert_class))
        #   return render_template('order.html',message=message,alert_class=alert_class,product_id=product_id,)

@order_blueprint.route("/view_order", methods=["GET"])
def view_order():
        if "logged_in" not in session or not session["logged_in"]:
           return redirect("login")
        else:
          user_id = session["user_id"]
          message = request.args.get("message",'')
          alert_class=request.args.get('alert_class')
          cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
          cursor.execute(
            f"SELECT o.*,a.*,p.image,p.name FROM orders AS o JOIN address AS a ON o.address_id=a.address_id JOIN product as p ON o.product_id=p.product_id WHERE o.user_id={user_id}"
           )
          orders = cursor.fetchall()
          cursor.close()
        return render_template('view_order.html',orders=orders,message=message,alert_class=alert_class)






    

    #  status='order placed'
    #             created_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #             updated_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
    #             cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #             cursor.execute(
    #                 "INSERT INTO orders (user_id,product_id,address_id,status,created_date,updated_date) VALUES (%s,%s,%s,%s,%s,%s)",(user_id,product_id,address_id,status,created_date,updated_date)
            
    #               )
    #             mysql.connection.commit()
    
    
    
    
    
           
    #     return render_template('order.html')
    # return render_template('home.html')
        
          
        
        
        