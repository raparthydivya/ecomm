from flask import Blueprint, render_template,request,Flask,session,redirect,url_for
from datetime import datetime
import pandas as pd
from openpyxl import load_workbook
from flask_mysqldb import MySQL
import MySQLdb.cursors


company_blueprint = Blueprint("company_blueprint", __name__)
app = Flask(__name__)
mysql = MySQL(app)


def validate_login():
    if "logged_in" not in session or not session['logged_in'] or session['usertype']!='companyuser':
        return redirect(url_for(".company_login"))
    else:
        company_user_id = session["company_user_id"]
        company_id=session['company_id']










@company_blueprint.route("/add_company", methods=["GET","POST"])
def add_company():
    if request.method == "POST":
        data = request.json
        if data and "company_name" in data:
            company_name = data["company_name"]
            status = data["status"]

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT * FROM company WHERE company_name = %s", (company_name,)
            )
            account = cursor.fetchone()
            if account:
                return {
                    "status": "FAILURE",
                    "message": "companyname already exists",
                    "data": "",
                    "traceback": "",
                }
            else:
                cursor.execute(
                    "INSERT INTO company(company_name,status) VALUES (%s,%s)",
                    (company_name, status),
                )
                mysql.connection.commit()
                return {
                    "status": "SUCESS",
                    "message": "Company_name added SUCESSFULLY",
                    "data": "",
                    "traceback": "",
                }
    return render_template("company.html")
    
@company_blueprint.route('/get_company/<ids>')
def get_company(ids):
    id_list = [int(id) for id in ids.split(",")]
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "SELECT * FROM company WHERE company_id IN ({})".format(
            ",".join(["%s"] * len(id_list))
        ),
        id_list,
    )
    companies = cursor.fetchall()

    data = {"companies": [], "missing_company": []}
    for id in id_list:
        found = False
        for company in companies:
            if company["company_id"] == id:
                data["companies"].append(company)
                found = True
                break
        if not found:
            data["missing_company"].append(id)

    return {
        "status": "sucess",
        "message": "Company Details",
        "data": data,
        "traceback": "",
    }

@company_blueprint.route("/company/home", methods=["GET","POST"])
def company_home():
    current_page='home'
    # if "logged_in" not in session or not session["logged_in"]:
    #     return redirect("/company/login")
    # else:
    #     company_user_id = session["company_user_id"]
    #     company_id=session['company_id']
        
    return render_template('company_home.html',current_page=current_page)
# company_user_id=company_user_id,company_id=company_id
    

    
@company_blueprint.route("/company/login", methods=["GET","POST"])
def company_login():
    if request.method == "POST":
        data = request.form
       
        if "username" in data and "password" in data:
            username = data["username"]
            password = data["password"]
           
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT * FROM company_users WHERE username = %s AND password = %s",
                (username, password)
            )
            account = cursor.fetchone()
            
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT company_id FROM company_users WHERE username = %s AND password = %s",
                (username, password)
            )
            company = cursor.fetchone()
            # print(company)
           
   
            if account:
                session['logged_in']= True 
                session['username']=account['username']
                session['company_user_id']=account['company_user_id']
                session['usertype']='companyuser'
                
            if company:
                session['company_id']=company['company_id']
                cursor.close() 
                  
                return redirect(url_for('.company_home'))
            
            else:
                message='incorrect username or password'
                alert_class='warning'
                return render_template('company_login.html',message=message,alert_class=alert_class)
         
    return render_template('company_login.html')
    


@company_blueprint.route("/company/register", methods=["GET","POST"])
def company_register():
    if request.method=='POST':
        data = request.form
        username = data["username"]
        password=data["password"]
        name=data['name']
        role=data['role']
        company_name=data['company_name']
        logo_url=data['logo_url']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT * FROM company WHERE company_name=%s",(company_name,))
        company = cursor.fetchone()
        
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute(
        #     f"SELECT * FROM company_users WHERE username = {username}",)
        # account = cursor.fetchone()
        # if account:
        #         return "username already exists"
        
        # else:
        if company:
            return "company name already exists"
        else:
            # return 'company_id does not exists'
            # message='company_id does not exists fill the all details'
            cursor.execute(
                "INSERT INTO company(company_name,logo_url) VALUES(%s,%s)",
                (company_name,logo_url)
                 ) 
            cursor.execute("SELECT LAST_INSERT_ID()")
            # print(fetch_last_company_id)
            # cursor.execute(fetch_last_company_id)
            last_inserted_company_id_row=cursor.fetchone()
            print(last_inserted_company_id_row)
            # print(row)
            if last_inserted_company_id_row:
                last_inserted_company_id=last_inserted_company_id_row[0]
                cursor.execute(
                    "INSERT INTO company_users(company_id,name,username,password,role) VALUES(%s,%s,%s,%s,%s)",
                    (last_inserted_company_id_row,name,username,password,role),
                    )
                
                cursor.close()
    return render_template('company_register.html')
                
@company_blueprint.route("/company/logout", methods=["GET", "POST"])
def company_logout():
    session.clear()
    return redirect(url_for('.company_login'))
 
 
   

    
@company_blueprint.route("/company/products", methods=["GET","POST"])
def company_products():
    current_page='products'
    validate_login()
    # if "logged_in" not in session or not session['logged_in']:
    #     return redirect(url_for(".company_login"))
    # else:
    message = request.args.get("message",'')
    alert_class=request.args.get('alert_class')
    company_user_id = session["company_user_id"]
    company_id=session['company_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
            f"SELECT * FROM product WHERE company_id={company_id}"
        )
    products = cursor.fetchall()
    cursor.close()
    return render_template('products.html',products=products,message=message,alert_class=alert_class,current_page=current_page)
   

@company_blueprint.route('/company/view_product/<int:product_id>',methods=['GET'])
def company_view_product(product_id):
    
    message = request.args.get("message",'')
    alert_class=request.args.get('alert_class')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM product WHERE product_id=%s",(product_id,))
    product=cursor.fetchone()
    cursor.close()
    # if not product: 
    #     return " No more products available"
    return render_template('company_viewproduct.html',product=product,product_id=product_id,message=message,alert_class=alert_class)

@company_blueprint.route('/company/edit_product/<int:product_id>',methods=['GET'])
def company_edit_product(product_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM product WHERE product_id=%s",(product_id,))
    product=cursor.fetchone()
    cursor.close()
    # if not product: 
    #     return " No more products available"
    return render_template('edit_product.html',product=product,product_id=product_id)
    
     
@company_blueprint.route('/save_product/<int:product_id>', methods=['POST'])
def save_product(product_id):
      if request.method == "POST":
        if "logged_in" not in session or not session["logged_in"]:
           return redirect("company_login")
        else:
          data = request.form
          company_user_id = session["company_user_id"]
          name=data['name']
          product_code=data['product_code']
          description=data['description']
          model_number=data['model_number']
        #   image=data['image']
          cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
          cursor.execute(f"UPDATE product SET name=%s,product_code=%s,description=%s,model_number=%s WHERE product_id={product_id}", (name,product_code,description,model_number,))
          mysql.connection.commit()
          cursor.close()
          message='Product updated successfullly'
          alert_class='success'
          return redirect(url_for('company_blueprint.company_view_product',message=message,alert_class=alert_class))


      return render_template('edit_product.html',product_id=product_id)
   
    
  
@company_blueprint.route("/company/add_product", methods=["POST","GET"])
def company_add_product():
  if request.method == "POST":
    if "logged_in" not in session or not session["logged_in"]:
        return redirect("company_login")
    else:
    
        data = request.form
        company_user_id = session["company_user_id"]
        company_id=session['company_id']
        name=data['name']
        categories=data['categories']
        product_code=data['product_code']
        description=data['description']
        model_number=data['model_number']
        image=data['image']
        amount=data['amount']
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
                    f'SELECT * FROM product WHERE company_id={company_id} AND name=%s AND product_code=%s AND description=%s AND model_number=%s AND image=%s AND amount=%s',(name,product_code,description,model_number,image,amount))   
        existing_product=cursor.fetchone()
              
        if existing_product:
          message = "Product already exists"
          alert_class = "warning"
          return redirect(url_for('.company_products',message=message,alert_class=alert_class))
        
        else:
          company_user_id = session["company_user_id"]
          company_id=session['company_id']
          cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
          cursor.execute(
          'INSERT INTO product(company_id,name,categories,product_code,description,model_number,image,amount) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',(company_id,name,categories,product_code,description,model_number,image,amount)
          )
          mysql.connection.commit()
          cursor.close()
          message = "Product successfully added "
          alert_class = "success"
          return redirect(url_for('company_blueprint.company_view_product',message=message,alert_class=alert_class))
        
  return render_template('add_product.html') 
    
    
    
    
    
@company_blueprint.route('/company/view_orders',methods=['GET'])
def company_view_orders():
    current_page='orders'
    if "logged_in" not in session or not session["logged_in"]:
        return redirect("company_login")
    else:
        company_user_id = session["company_user_id"]
        company_id=session['company_id']
    
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # cursor.execute("SELECT * FROM orders WHERE product_id=%s",(product_id,))
        cursor.execute(
            f"SELECT o.*,a.*,p.image,p.name,p.amount,u.username FROM orders AS o JOIN address AS a ON o.address_id=a.address_id JOIN product as p ON p.product_id=o.product_id JOIN user as u ON u.user_id=o.user_id WHERE p.company_id={company_id}"
        )        
        
        orders=cursor.fetchall()
        # print(orders)
        cursor.close()
    # if not product: _
    #     return " No more products available"
    return render_template('company_order_view.html',orders=orders,current_page=current_page)
    
@company_blueprint.route('/company/order/<int:order_id>',methods=['GET'])
def company_order(order_id):
    if "logged_in" not in session or not session['logged_in']:
        return redirect(url_for(".company_login"))
    
    else:
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT o.*,a.*,p.image,p.name,p.amount,u.username FROM orders AS o JOIN address AS a ON o.address_id=a.address_id JOIN product as p ON p.product_id=o.product_id JOIN user as u ON u.user_id=o.user_id WHERE o.order_id={order_id}"
)
        order=cursor.fetchone()
        cursor.close()
        return render_template('view_company_order.html',order=order)
    
        
    
@company_blueprint.route('/company/update_order_status',methods=['GET','POST'])
def company_update_order_status():
    if "logged_in" not in session or not session['logged_in']:
        return redirect(url_for(".company_login"))
    
    else:
        if request.method=='POST':
            
            company_user_id = session["company_user_id"]
            company_id=session['company_id']
            order_id=request.form.get('order_id')
            print(order_id)
            status=request.form.get('status')
            # print(update_status)
            cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("UPDATE orders SET status=%s WHERE order_id=%s",(status,order_id))
            mysql.connection.commit()
            return redirect(url_for('.company_view_orders',order_id=order_id))
    
        return redirect(url_for('company_home'))
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
#     if request.method == 'POST':
#         details = pd.read_excel("open_ecommerce.xlsx", sheet_name="company")
#         company_name = request.form.get("company_name")
#         status = request.form.get("status")
#         print(company_name)
#         print(details["company_name"].str.lower().tolist())
#         updated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         if not company_name:
#             return {
#                 "status": "error",
#                 "message": "Company name cannot be empty",
#                 "data": "",
#                 "traceback": "",
#             }
#         if company_name.lower() in details["company_name"].str.lower().tolist():
#             return {
#                 "status": "failure",
#                 "message": "Company already exists",
#                 "data": "",
#                 "traceback": "",
#             }

#         print(details["company_id"].max())
#         max_company_id = details["company_id"].max()
#         new_company_id = max_company_id + 1

#         wb = load_workbook("open_ecommerce.xlsx")
#         ws = wb.active
#         ws.append([new_company_id, company_name, status, updated_date, updated_date])
#         wb.save("open_ecommerce.xlsx")

#         return {
#             "status": "sucess",
#             "message": "Company added successfully",
#             "data": {"company_id": int(new_company_id)},
#             "traceback": "",
#         }
#     return render_template('company.html')

# @company_blueprint.route('/get_company/<ids>')
# def get_company(ids):
#     id_list=[int(id) for id in ids.split(',')]
#     details=pd.read_excel('open_ecommerce.xlsx',sheet_name='company')
#     company_data=details[details['company_id'].isin(id_list)]
    
#     data={
#         'company':[],
#         'missing_company':[]
#     }
#     for id in id_list:
#         for index,row in company_data.iterrows():
#             if row['company_id'] == id:
#                 company={
#                     'company_id':row['company_id'],
#                     'company_name':row['company_name'],
#                     'status':row['status']  
#                 }
#                 data['company'].append(company)
#                 break
#             else:
#                 data['missing_company'].append(id)
        
#     return{
#             'status':'sucess',
#             'message':'Company Details',
#             'data': data,
#             'traceback':''
#     }