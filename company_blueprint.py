from flask import Blueprint, render_template, request, Flask, session, redirect, url_for
from datetime import datetime,timedelta
import pandas as pd
from openpyxl import load_workbook
from flask_mysqldb import MySQL
import MySQLdb.cursors
from dateutil.relativedelta import relativedelta


company_blueprint = Blueprint("company_blueprint", __name__)
app = Flask(__name__)
mysql = MySQL(app)


def validate_login():
    if (
        "logged_in" not in session
        or not session["logged_in"]
        or session["usertype"] != "companyuser"
    ):
        return redirect(url_for(".company_login"))
    else:
        company_user_id = session["company_user_id"]
        company_id = session["company_id"]
        companyuser = session["usertype"]
        return True


@company_blueprint.route("/company/home", methods=["GET", "POST"])
def company_home():
    current_page = "home"
    if "logged_in" not in session or not session["logged_in"] or "usertype" not in session or session['usertype']!='company_user':
        return redirect(url_for(".company_login"))
    else:
        company_user_id = session["company_user_id"]
        company_id=session['company_id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT * FROM company WHERE company_id={company_id}")
        company=cursor.fetchone()
        cursor.close()
        print(company)
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT o.status,COUNT(*) AS order_count FROM orders o JOIN product p ON o.product_id=p.product_id WHERE p.company_id={company_id} GROUP BY status")
        company_order_data = cursor.fetchall()
            # print(order_data)
        cursor.close()
        company_chart_data=[]
        for data in company_order_data:
                
            company_chart_data.append({"name":data['status'],'y':data['order_count']})
        # print(company_chart_data)
        
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT p.name,COUNT(o.order_id) AS order_count FROM orders o JOIN product p ON o.product_id=p.product_id WHERE company_id={company_id} GROUP BY p.product_id,p.name limit 15 ")
        company_products_order_data = cursor.fetchall()
        cursor.close()
        company_product_data=[]
        
        for data in company_products_order_data:
                
            company_product_data.append({"name":data['name'],"y":data['order_count']})
        # print(company_product_data)
        
        
        today=datetime.today()
        final_data=[]
        n=3
        for i in range(n):
                start_date=today-relativedelta(months=i)
                start_date=start_date.replace(day=1)
                end_date=start_date+ relativedelta(months=1) - timedelta(days=1)
            
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                query=f"SELECT COUNT(*) AS order_count,DATE(o.created_date) AS created_date FROM orders o JOIN product p ON o.product_id=p.product_id WHERE p.company_id={company_id} AND o.created_date BETWEEN '{start_date}' AND '{end_date}' GROUP BY DATE(o.created_date)"     
                cursor.execute(query)
                order_data=cursor.fetchall()
                # print(query)
                
                month_data = []
            
                current_date=start_date
            
                while current_date <= end_date:
                    order_count=0
                    for data in order_data:
                        
                        if current_date.strftime('%Y-%m-%d')==data['created_date'].strftime('%Y-%m-%d'):
                            order_count=data['order_count']
                            break
                    month_data.append(order_count)
                    current_date +=timedelta(days=1)
                    
                # print(month_data)
                final_data.append({'name':start_date.strftime('%B'),'data':month_data})
                
           
        
        

    return render_template("company_home.html", current_page=current_page,company_chart_data=company_chart_data,company_product_data=company_product_data,final_data=final_data,company=company)


# company_user_id=company_user_id,company_id=company_id


@company_blueprint.route("/company/login", methods=["GET", "POST"])
def company_login():
    if request.method == "POST":
        data = request.form
        message = request.args.get("message", "")
        alert_class = request.args.get("alert_class", "")

        if "username" in data and "password" in data:
            username = data["username"]
            password = data["password"]

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT * FROM company_users WHERE username = %s AND password = %s",
                (username, password),
            )
            account = cursor.fetchone()

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT company_id FROM company_users WHERE username = %s AND password = %s",
                (username, password),
            )
            company = cursor.fetchone()
            # print(company)

            if account:
                session["logged_in"] = True
                session["username"] = account["username"]
                session["company_user_id"] = account["company_user_id"]
                session["usertype"] = "company_user"

            if company:
                
                session["company_id"] = company["company_id"]
                cursor.close()

                return redirect(url_for(".company_home"))

            else:
                message = "incorrect username or password"
                alert_class = "warning"
                return render_template(
                    "company_login.html", message=message, alert_class=alert_class
                )

    return render_template("company_login.html")


@company_blueprint.route("/company/register", methods=["GET", "POST"])
def company_register():
    if request.method == "POST":
        data = request.form
        username = data["username"]
        password = data["password"]
        name = data["name"]
        role = data["role"]
        company_name = data["company_name"]
        # logo_url=data['logo_url']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM company WHERE company_name=%s", (company_name,))
        company = cursor.fetchone()

        if company:
            message = "company name already exists"
            alert_class = "warning"

        else:
            message = "Successfully logged in"
            alert_class = "success"

            # message='company_id does not exists fill the all details'
            logo_url = f"https://placehold.co/600x400/grey/white?text={company_name}"
            cursor.execute(
                "INSERT INTO company(company_name,logo_url) VALUES(%s,%s)",
                (company_name, logo_url),
            )
            mysql.connection.commit()
            last_insert_id = cursor.lastrowid
            # print(last_insert_id)
            cursor.execute(
                "INSERT INTO company_users(company_id,name,username,password,role) VALUES(%s,%s,%s,%s,%s)",
                (last_insert_id, name, username, password, role),
            )
            mysql.connection.commit()
            # cursor.commit
            cursor.close()
            return redirect(
                url_for(".company_login", message=message, alert_class=alert_class)
            )
    return render_template("company_register.html")


@company_blueprint.route("/company/logout", methods=["GET", "POST"])
def company_logout():
    session.clear()
    return redirect(url_for(".company_login"))


@company_blueprint.route("/company/products", methods=["GET", "POST"])
def company_products():
    current_page = "products"
    # validate_login()
    if "logged_in" not in session or not session["logged_in"] or "usertype" not in session or session['usertype']!='company_user':
        return redirect(url_for(".company_login"))
    else:
        message = request.args.get("message", "")
        alert_class = request.args.get("alert_class")
        
        company_user_id = session["company_user_id"]
        company_id = session["company_id"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT * FROM company WHERE company_id={company_id}")
        company=cursor.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT * FROM product WHERE company_id={company_id}")
        products = cursor.fetchall()
        cursor.close()
    return render_template(
        "products.html",
        products=products,
        message=message,
        alert_class=alert_class,
        current_page=current_page,company=company
    )


@company_blueprint.route("/company/view_product/<int:product_id>", methods=["GET"])
def company_view_product(product_id):
    if "logged_in" not in session or not session["logged_in"] or "usertype" not in session or session['usertype']!='company_user':
        return redirect(url_for(".company_login"))
    else:
        message = request.args.get("message", "")
        alert_class = request.args.get("alert_class")
        
        company_user_id = session["company_user_id"]
        company_id = session["company_id"]
        current_page = "products"
        message = request.args.get("message", "")
        alert_class = request.args.get("alert_class")
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT * FROM company WHERE company_id={company_id}")
        company=cursor.fetchone()
        cursor.close()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM product WHERE product_id=%s", (product_id,))
        product = cursor.fetchone()
        cursor.close()
    # if not product:
    #     return " No more products available"
    return render_template(
        "company_viewproduct.html",
        product=product,company=company,
        product_id=product_id,
        message=message,
        alert_class=alert_class,
        current_page=current_page,
    )


@company_blueprint.route("/company/edit_product/<int:product_id>", methods=["GET"])
def company_edit_product(product_id):
    current_page = "products"
    if "logged_in" not in session or not session["logged_in"] or "usertype" not in session or session['usertype']!='company_user':
        return redirect(url_for(".company_login"))
    else:
        message = request.args.get("message", "")
        alert_class = request.args.get("alert_class")
        
        company_user_id = session["company_user_id"]
        company_id = session["company_id"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT * FROM company WHERE company_id={company_id}")
        company=cursor.fetchone()
        cursor.close()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM product WHERE product_id=%s", (product_id,))
        product = cursor.fetchone()
        cursor.close()
        category = [
                    {"category_id": 1, "category_name": "Electronics"},
                    {"category_id": 2, "category_name": "Fashion"},
                    {"category_id": 3, "category_name": 'Home'}
                ]
        sub_category = [
                    {
                        "sub_category_id": 1,
                        "category_id": 1,
                        "sub_category_name": "Smart Phones",
                    },
                    {
                        "sub_category_id": 2,
                        "category_id": 1,
                        "sub_category_name": "Laptops",
                    },
                    {
                        "sub_category_id": 3,
                        "category_id": 2,
                        "sub_category_name": "Top Wear",
                    },
                    {
                        "sub_category_id": 4,
                        "category_id": 2,
                        "sub_category_name": "Bottom Wear",
                    },
                    {
                        "sub_category_id": 5,
                        "category_id": 3,
                        "sub_category_name": "Home Appliances",
                    }
                    
                ]
    # if not product:
    #     return " No more products available"
    return render_template(
        "edit_product.html",
        product=product,
        product_id=product_id,
        current_page=current_page,category=category,sub_category=sub_category,company=company
    )


@company_blueprint.route("/save_product/<int:product_id>", methods=["POST"])
def save_product(product_id):
    current_page = "products"
    if request.method == "POST":
        if "logged_in" not in session or not session["logged_in"] or "usertype" not in session or session['usertype']!='company_user':
            return redirect(url_for(".company_login"))
        else:
            data = request.form
            company_user_id = session["company_user_id"]
            company_id=session['company_id']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(f"SELECT * FROM company WHERE company_id={company_id}")
            company=cursor.fetchone()
            cursor.close()
            name = data["name"]
            product_code = data["product_code"]
            description = data["description"]
            model_number = data["model_number"]
            selected_value=data['category_id']
            category_id,sub_category_id=selected_value.split('|')
            #   categories=data['categories']
            #   image=data['image']
            category = [
                {"category_id": 1, "category_name": "Electronics"},
                {"category_id": 2, "category_name": "Fashion"},
                {"category_id": 3, "category_name": 'Home'}
            ]
            sub_category = [
                {
                    "sub_category_id": 1,
                    "category_id": 1,
                    "sub_category_name": "Smart Phones"
                },
                {
                    "sub_category_id": 2,
                    "category_id": 1,
                    "sub_category_name": "Laptops"
                },
                {
                    "sub_category_id": 3,
                    "category_id": 2,
                    "sub_category_name": "Top Wear"
                },
                {
                    "sub_category_id": 4,
                    "category_id": 2,
                    "sub_category_name": "Bottom Wear"
                },
                {
                    "sub_category_id": 5,
                    "category_id": 3,
                    "sub_category_name": "Home Appliances",
                }
                
            ]

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                f"UPDATE product SET name=%s,product_code=%s,description=%s,model_number=%s,category_id=%s,sub_category_id=%s WHERE product_id={product_id}",
                (name, product_code, description, model_number, category_id,sub_category_id),
            )
            mysql.connection.commit()
            cursor.close()
            message = "Product updated successfullly"
            alert_class = "success"
            return redirect(
                url_for(
                    ".company_view_product",
                    message=message,
                    alert_class=alert_class,
                    product_id=product_id,
                )
            )

    return render_template(
        "edit_product.html", product_id=product_id, current_page=current_page,category=category,sub_category=sub_category,company=company
    )


@company_blueprint.route("/company/add_product", methods=["POST", "GET"])
def company_add_product():
    current_page = "products"
    category = [
                {"category_id": 1, "category_name": 'Electronics'},
                {"category_id": 2, "category_name": 'Fashion'},
                {"category_id": 3, "category_name": 'Home'}
            ]
    sub_category = [
                {
                    "sub_category_id": 1,
                    "category_id": 1,
                    "sub_category_name": "Smart Phones",
                },
                {
                    "sub_category_id": 2,
                    "category_id": 1,
                    "sub_category_name": "Laptops",
                },
                {
                    "sub_category_id": 3,
                    "category_id": 2,
                    "sub_category_name": "Top Wear",
                },
                {
                    "sub_category_id": 4,
                    "category_id": 2,
                    "sub_category_name": "Bottom Wear",
                },
                {
                    "sub_category_id": 5,
                    "category_id": 3,
                    "sub_category_name": "Home Appliances",
                }
                
            ]
    
    if "logged_in" not in session or not session["logged_in"] or "usertype" not in session or session['usertype']!='company_user':
            return redirect(url_for(".company_login"))
    else:
        company_id = session["company_id"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT * FROM company WHERE company_id={company_id}")
        company=cursor.fetchone()
        cursor.close()
        if request.method == "POST":
        
            data = request.form
            company_user_id = session["company_user_id"]
            
            name = data["name"]
            product_code = data["product_code"]
            description = data["description"]
            model_number = data["model_number"]
            image = data["image"]
            amount = data["amount"]
            selected_value=data['category_id']
            category_id,sub_category_id=selected_value.split('|')
            
            
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                f"SELECT * FROM product WHERE company_id={company_id} AND name=%s AND product_code=%s AND description=%s AND model_number=%s AND image=%s AND amount=%s",
                (name, product_code, description, model_number, image, amount),
            )
            existing_product = cursor.fetchone()

            if existing_product:
                message = "Product already exists"
                alert_class = "warning"
                return redirect(
                    url_for(
                        ".company_products", message=message, alert_class=alert_class
                    )
                )

            else:
                company_user_id = session["company_user_id"]
                company_id = session["company_id"]
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(
                    "INSERT INTO product(company_id,name,product_code,description,model_number,image,amount,category_id,sub_category_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        company_id,
                        name,
                        product_code,
                        description,
                        model_number,
                        image,
                        amount,
                        category_id,sub_category_id
                    ),
                )
                mysql.connection.commit()
                cursor.close()
                message = "Product successfully added "
                alert_class = "success"
                return redirect(
                    url_for(
                        ".company_view_product",
                        message=message,
                        alert_class=alert_class,company=company
                    )
                )

    return render_template("add_product.html", current_page=current_page,category=category,sub_category=sub_category,company=company)


@company_blueprint.route("/company/view_orders", methods=["GET"])
def company_view_orders():
    current_page = "orders"
    if "logged_in" not in session or not session["logged_in"] or "usertype" not in session or session['usertype']!='company_user':
        return redirect(url_for(".company_login"))
    else:
        company_user_id = session["company_user_id"]
        company_id = session["company_id"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT * FROM company WHERE company_id={company_id}")
        company=cursor.fetchone()
        cursor.close()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute("SELECT * FROM orders WHERE product_id=%s",(product_id,))
        cursor.execute(
            f"SELECT o.*,a.*,p.image,p.name,p.amount,u.username FROM orders AS o JOIN address AS a ON o.address_id=a.address_id JOIN product as p ON p.product_id=o.product_id JOIN user as u ON u.user_id=o.user_id WHERE p.company_id={company_id}"
        )
        orders = cursor.fetchall()
        # print(orders)
        cursor.close()
    # if not product: _
    #     return " No more products available"
    return render_template(
        "company_order_view.html", orders=orders, current_page=current_page,company=company
    )


@company_blueprint.route("/company/order/<int:order_id>", methods=["GET"])
def company_order(order_id):
    current_page = "orders"
    if "logged_in" not in session or not session["logged_in"] or "usertype" not in session or session['usertype']!='company_user':
        return redirect(url_for(".company_login"))

    else:
        company_user_id = session["company_user_id"]
        company_id = session["company_id"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT * FROM company WHERE company_id={company_id}")
        company=cursor.fetchone()
        cursor.close()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            f"SELECT o.*,a.*,p.image,p.name,p.amount,u.username FROM orders AS o JOIN address AS a ON o.address_id=a.address_id JOIN product as p ON p.product_id=o.product_id JOIN user as u ON u.user_id=o.user_id WHERE o.order_id={order_id}"
        )
        order = cursor.fetchone()
        cursor.close()
        return render_template(
            "view_company_order.html", order=order, current_page=current_page,company=company
        )


@company_blueprint.route("/company/update_order_status", methods=["GET", "POST"])
def company_update_order_status():
    current_page = "orders"
    if "logged_in" not in session or not session["logged_in"] or "usertype" not in session or session['usertype']!='company_user':
        return redirect(url_for(".company_login"))

    else:
        if request.method == "POST":
            company_user_id = session["company_user_id"]
            company_id = session["company_id"]
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(f"SELECT * FROM company WHERE company_id={company_id}")
            company=cursor.fetchone()
            cursor.close()
            order_id = request.form.get("order_id")
            # print(order_id)
            status = request.form.get("status")
            # print(update_status)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "UPDATE orders SET status=%s WHERE order_id=%s", (status, order_id)
            )
            mysql.connection.commit()
            return redirect(url_for(".company_view_orders", order_id=order_id))

        return redirect(url_for("company_home"), current_page=current_page,company=company)

@company_blueprint.route("/company/users", methods=["GET", "POST"])
def company_users():
    current_page = "users"
    # validate_login()
    if "logged_in" not in session or not session["logged_in"] or "usertype" not in session or session['usertype']!='company_user':
        return redirect(url_for(".company_login"))
    else:
        message = request.args.get("message", "")
        alert_class = request.args.get("alert_class")
        
        company_user_id = session["company_user_id"]
        company_id = session["company_id"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT * FROM company WHERE company_id={company_id}")
        company=cursor.fetchone()
        cursor.close()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT DISTINCT u.* FROM user u WHERE u.user_id IN( SELECT DISTINCT o.user_id FROM orders AS o JOIN product AS p ON o.product_id=p.product_id JOIN company as c ON c.company_id=p.company_id JOIN user as u ON u.user_id=o.user_id WHERE c.company_id={company_id})")
        users=cursor.fetchall()
        # print(users)
    return render_template('company_users.html',users=users,company=company,current_page=current_page)





@company_blueprint.route("/company/delete_product/<int:product_id>", methods=["POST"])
def company_delete_product(product_id):
    current_page = "products"
    if request.method=='POST':
        if "logged_in" not in session or not session["logged_in"] or "usertype" not in session or session['usertype']!='company_user':
           return redirect(url_for(".company_login"))
        else:
            message = request.args.get("message", "")
            alert_class = request.args.get("alert_class")
            
            company_user_id = session["company_user_id"]
            company_id = session["company_id"]
            
            message = request.args.get("message", "")
            alert_class = request.args.get("alert_class")
            
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                    f"DELETE FROM product WHERE product_id={product_id}",
                )
            mysql.connection.commit()
            cursor.close()
            message = "Product Deleted Successfullly"
            alert_class = "success"
            return redirect(
                    url_for(
                        ".company_products",
                        message=message,
                        alert_class=alert_class,
                        product_id=product_id,
                    )
                )
    return render_template(
            "products.html",
            message=message,
            alert_class=alert_class,
            current_page=current_page,
        )
































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
