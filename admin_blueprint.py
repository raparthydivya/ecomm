from flask import Blueprint, render_template, request, Flask, session, redirect, url_for
from datetime import datetime,timedelta,time
import pandas as pd
from openpyxl import load_workbook
from flask_mysqldb import MySQL
import MySQLdb.cursors
from dateutil.relativedelta import relativedelta


admin_blueprint = Blueprint("admin_blueprint", __name__)
app = Flask(__name__)
mysql = MySQL(app)


def login123():
    print(session)
    if session:
        redirect(url_for(".admin_login"))
        print(18)
        
    if (
        "logged_in" not in session
        or not session["logged_in"]
        or "usertype" not in session
        or session["usertype"] != "admin_user"
    ):
        print(27)
        return redirect(url_for(".admin_login"))
    return True  

@admin_blueprint.route("/admin/sidebar", methods=["GET", "POST"])
def admin_sidebar():
    if (
        "logged_in" not in session
        or not session["logged_in"]
        or "usertype" not in session
        or session["usertype"] != "admin_user"
    ):
        return redirect(url_for(".admin_login"))
    else:
        message = request.args.get("message", "")
        alert_class = request.args.get("alert_class")
        
        
    return render_template('admin_sidebar.html',admin=admin)





@admin_blueprint.route("/admin/home", methods=["GET", "POST"])
def admin_home():
    
   
    current_page = "admin home"
    if (
        "logged_in" not in session
        or not session["logged_in"]
        or "usertype" not in session
        or session["usertype"] != "admin_user"
    ):
        return redirect(url_for(".admin_login"))
    else:
   
        message = request.args.get("message", "")
        alert_class = request.args.get("alert_class")
        id=session['id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT * FROM admin WHERE id={id}")
        admin = cursor.fetchone()
        # print(admin)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT status,COUNT(*) AS order_count FROM orders GROUP BY status")
        order_data = cursor.fetchall()
            # print(order_data)
        cursor.close()
        chart_data=[]
       
        for data in order_data:
                
            chart_data.append({"name":data['status'],'y':data['order_count']})
                # print(chart_data)
                
                
        
        today=datetime.today()
        final_output=[]
        n=3
        for i in range(n):
                start_date=today-relativedelta(months=i)
                start_date=start_date.replace(day=1)
                end_date=start_date+ relativedelta(months=1) - timedelta(days=1)
            
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                query=f"SELECT COUNT(*) AS order_count,DATE(created_date) AS created_date FROM orders WHERE created_date BETWEEN '{start_date}' AND '{end_date}' GROUP BY DATE(created_date)"     
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
                final_output.append({'name':start_date.strftime('%B'),'data':month_data})
                
        # print(final_output)     
                        
        
            
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT p.name,COUNT(o.order_id) AS order_count FROM orders o JOIN product p ON o.product_id=p.product_id GROUP BY p.product_id,p.name limit 15 ")
        products_order_data = cursor.fetchall()
        cursor.close()
        product_data=[]
        
        for data in products_order_data:
                
            product_data.append({"name":data['name'],"y":data['order_count']})
            
            # print(product_orders)
        
    return render_template('admin_home.html',chart_data=chart_data,product_data=product_data,final_output=final_output,current_page=current_page,admin=admin)
    
    


@admin_blueprint.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        data = request.form
        if "admin_name" in data and "password" in data:
            admin_name = data["admin_name"]
            password = data["password"]

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT * FROM admin WHERE admin_name = %s AND password = %s",
                (admin_name, password),
            )
            account = cursor.fetchone()
            if account:
                session["logged_in"] = True
                session["admin_name"] = account["admin_name"]
                session["id"] = account["id"]
                session["usertype"] = "admin_user"

                return redirect(url_for(".admin_home"))
            else:
                message = "incorrect admin_name or password"
                alert_class = "warning"
                return render_template(
                    "admin_login.html", message=message, alert_class=alert_class
                )
    return render_template("admin_login.html")


@admin_blueprint.route("/admin/logout", methods=["GET", "POST"])
def admin_logout():
    session.clear()
    return redirect(url_for(".admin_login"))


@admin_blueprint.route("/admin/products", methods=["GET", "POST"])
def admin_products():
    current_page = "admin products"
    if (
        "logged_in" not in session
        or not session["logged_in"]
        or "usertype" not in session
        or session["usertype"] != "admin_user"
    ):
        return redirect(url_for(".admin_login"))
    else:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT * FROM admin")
        admin = cursor.fetchone()
        cursor.close()
        message = request.args.get("message", "")
        alert_class = request.args.get("alert_class")
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
                "SELECT p.*,c.*,ct.*,st.* FROM product AS p JOIN company as c ON p.company_id=c.company_id JOIN category as ct ON p.category_id=ct.category_id JOIN sub_category as st ON p.sub_category_id=st.sub_category_id"
            )
        products = cursor.fetchall()
        cursor.close()
    return render_template(
        "admin_products.html",
        products=products,
        message=message,
        alert_class=alert_class,
        current_page=current_page,admin=admin
    )


@admin_blueprint.route("/admin/view_product/<int:product_id>", methods=["GET"])
def admin_view_product(product_id):
    current_page = "admin products"
    message = request.args.get("message", "")
    alert_class = request.args.get("alert_class")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM admin")
    admin = cursor.fetchone()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        f"SELECT p.*,c.*,ct.*,st.* FROM product AS p JOIN company as c ON p.company_id=c.company_id JOIN category as ct ON p.category_id=ct.category_id JOIN sub_category as st ON p.sub_category_id=st.sub_category_id WHERE product_id={product_id}"
    )
    product = cursor.fetchone()
    cursor.close()
    return render_template(
        "admin_view_product.html",
        product=product,
        product_id=product_id,
        message=message,
        alert_class=alert_class,
        current_page=current_page,admin=admin
    )


@admin_blueprint.route("/admin/users", methods=["GET", "POST"])
def admin_users():
    current_page = "users"
    if (
        "logged_in" not in session
        or not session["logged_in"]
        or "usertype" not in session
        or session["usertype"] != "admin_user"
    ):
        return redirect(url_for(".admin_login"))
    else:
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM admin")
        admin = cursor.fetchone()
        cursor.close()
        message = request.args.get("message", "")
        alert_class = request.args.get("alert_class")

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

    return render_template(
            "admin_users.html",
            users=users,
            message=message,
            alert_class=alert_class,
            current_page=current_page,admin=admin
        )


@admin_blueprint.route("/admin/view_address/<int:user_id>", methods=["GET"])
def admin_view_address(user_id):
    current_page = "users"
    message = request.args.get("message", "")
    alert_class = request.args.get("alert_class")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM admin")
    admin = cursor.fetchone()
    cursor.close()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        f"SELECT u.*,a.* FROM user AS u JOIN address as a ON u.user_id=a.user_id WHERE u.user_id={user_id}"
    )
    user_address = cursor.fetchall()
    cursor.close()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
   
    cursor.execute(f"SELECT * FROM user WHERE user_id={user_id}")
    user_data = cursor.fetchone()
    cursor.close()
    
    return render_template(
        "admin_user_address.html",
        user_address=user_address,
        message=message,
        user_id=user_id,
        alert_class=alert_class,
        current_page=current_page,admin=admin,user_data=user_data
    )


@admin_blueprint.route("/admin/user_address/<int:user_id>", methods=["GET", "POST"])
def admin_user_address(user_id):
    current_page = "users"
   
    message = request.args.get("message", "")
    alert_class = request.args.get("alert_class")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM admin")
    admin = cursor.fetchone()
    cursor.close()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f"SELECT * FROM user WHERE user_id={user_id}")
    user_data = cursor.fetchone()

    cursor.execute(f"SELECT * FROM address WHERE user_id={user_id}")
    user_address = cursor.fetchone()
    cursor.close()

    return render_template(
            "admin_user_address.html",
            user_address=user_address,
            message=message,
            user_id=user_id,user_data=user_data,
            alert_class=alert_class,
            current_page=current_page,admin=admin
           
        )


@admin_blueprint.route("/admin/companies", methods=["GET", "POST"])
def admin_companies():
    current_page = "companies"
    if (
        "logged_in" not in session
        or not session["logged_in"]
        or "usertype" not in session
        or session["usertype"] != "admin_user"
    ):
        return redirect(url_for(".admin_login"))
    else:
        message = request.args.get("message", "")
        alert_class = request.args.get("alert_class")
        # session["admin_name"] = account["admin_name"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM admin")
        admin = cursor.fetchone()
        cursor.close()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM company")
        companies = cursor.fetchall()

        return render_template(
            "admin_companies.html",
            companies=companies,
            message=message,
            alert_class=alert_class,
            current_page=current_page,admin=admin
        )


@admin_blueprint.route(
    "/admin/company_products/<int:company_id>", methods=["GET", "POST"]
)
def admin_company_products(company_id):
    current_page = "companies"
    if (
        "logged_in" not in session
        or not session["logged_in"]
        or "usertype" not in session
        or session["usertype"] != "admin_user"
    ):
        return redirect(url_for(".admin_login"))
    else:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM admin")
        admin = cursor.fetchone()
        cursor.close()
        message = request.args.get("message", "")
        alert_class = request.args.get("alert_class")
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT * FROM company WHERE company_id={company_id}")
        company = cursor.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT * FROM product WHERE company_id={company_id}")
        products = cursor.fetchall()
        cursor.close()
        return render_template(
            "admin_company_products.html",
            products=products,
            company_id=company_id,
            message=message,
            alert_class=alert_class,
            current_page=current_page,admin=admin,company=company
        )

@admin_blueprint.route("/admin/company/view_product/<int:product_id>", methods=["GET"])
def admin_company_view_product(product_id):
    current_page = "companies"
    message = request.args.get("message", "")
    alert_class = request.args.get("alert_class")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM admin")
    admin = cursor.fetchone()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        f"SELECT p.*,c.*,ct.*,st.* FROM product AS p JOIN company as c ON p.company_id=c.company_id JOIN category as ct ON p.category_id=ct.category_id JOIN sub_category as st ON p.sub_category_id=st.sub_category_id WHERE product_id={product_id}"
    )
    product = cursor.fetchone()
    cursor.close()
    return render_template(
        "admin_company_view_product.html",
        product=product,
        product_id=product_id,
        message=message,
        alert_class=alert_class,
        current_page=current_page,admin=admin
    )


@admin_blueprint.route("/admin/orders", methods=["GET", "POST"])
def admin_orders():
    current_page = "orders"
    if (
        "logged_in" not in session
        or not session["logged_in"]
        or "usertype" not in session
        or session["usertype"] != "admin_user"
    ):
        return redirect(url_for(".admin_login"))
    else:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM admin")
        admin = cursor.fetchone()
        cursor.close()
        message = request.args.get("message", "")
        alert_class = request.args.get("alert_class")
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            f"SELECT o.*,a.*,p.image,p.name,p.amount,u.* FROM orders AS o JOIN address AS a ON o.address_id=a.address_id JOIN product as p ON o.product_id=p.product_id  JOIN user AS u ON o.user_id=u.user_id"
        )
        orders = cursor.fetchall()
        cursor.close()
        return render_template(
            "admin_orders.html",
            orders=orders,
            message=message,
            alert_class=alert_class,
            current_page=current_page,admin=admin
        )


@admin_blueprint.route("/admin/categories", methods=["GET", "POST"])
def admin_categories():
    current_page = "categories"
    if (
        "logged_in" not in session
        or not session["logged_in"]
        or "usertype" not in session
        or session["usertype"] != "admin_user"
    ):
        return redirect(url_for(".admin_login"))
    else:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM admin")
        admin = cursor.fetchone()
        cursor.close()
        message = request.args.get("message", "")
        alert_class = request.args.get("alert_class")
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(" SELECT * FROM category ")
        categories = cursor.fetchall()
        cursor.close()
        return render_template(
            "admin_categories.html",
            categories=categories,
            message=message,
            alert_class=alert_class,
            current_page=current_page,admin=admin
        )


@admin_blueprint.route("/admin/sub_categories", methods=["GET", "POST"])
def admin_sub_categories():
    current_page = "sub categories"
    if (
        "logged_in" not in session
        or not session["logged_in"]
        or "usertype" not in session
        or session["usertype"] != "admin_user"
    ):
        return redirect(url_for(".admin_login"))
    else:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM admin")
        admin = cursor.fetchone()
        cursor.close()
        message = request.args.get("message", "")
        alert_class = request.args.get("alert_class")
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT sb.*,c.* FROM sub_category AS sb JOIN category as c ON sb.category_id=c.category_id",)

        sub_categories = cursor.fetchall()
        cursor.close()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT * FROM category")
        categories=cursor.fetchall()
        # print(category)
        return render_template(
            "admin_sub_categories.html",
            sub_categories=sub_categories,
            message=message,
            alert_class=alert_class,
            current_page=current_page,categories=categories,admin=admin
        )


@admin_blueprint.route("/admin/add_categories", methods=["GET", "POST"])
def admin_add_categories():
    current_page = "categories"
    if (
        "logged_in" not in session
        or not session["logged_in"]
        or "usertype" not in session
        or session["usertype"] != "admin_user"
    ):
        return redirect(url_for(".company_login"))
    else:
        if request.method == "POST":
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM admin")
            admin = cursor.fetchone()
            cursor.close()
            data = request.form
            category_name = data["category_name"]
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT * FROM category WHERE category_name=%s", (category_name,)
            )
            existing_category = cursor.fetchone()
            cursor.close()

            if existing_category:
                message = "category already exists"
                alert_class = "warning"
                return redirect(
                    url_for(
                        ".admin_categories", message=message, alert_class=alert_class
                    )
                )

            else:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(
                    "INSERT INTO category(category_name) VALUES(%s)",
                    (category_name),
                )
                mysql.connection.commit()
                cursor.close()
                message = "category successfully added "
                alert_class = "success"
                return redirect(
                    url_for(
                        ".admin_categories", message=message, alert_class=alert_class,admin=admin
                    )
                )


@admin_blueprint.route("/admin/add_sub_categories", methods=["GET", "POST"])
def admin_add_sub_categories():
    current_page = "sub categories"
    
    if (
        "logged_in" not in session
        or not session["logged_in"]
        or "usertype" not in session
        or session["usertype"] != "admin_user"
    ):
        return redirect(url_for(".company_login"))
    
    else:
        if request.method == "POST":
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM admin")
            admin = cursor.fetchone()
            cursor.close()
            data = request.form
            # category_name=data['category_name']
            category_id=data['category_id']
            sub_category_name = data["sub_category_name"]
            
            
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                        f"SELECT * FROM sub_category WHERE sub_category_name=%s",
                (sub_category_name,),
            )
            existing_sub_category = cursor.fetchone()
            cursor.close()
            
                
            if existing_sub_category:
                message = "Sub category already exists"
                alert_class = "warning"
                return redirect(
                    url_for(
                        ".admin_sub_categories", message=message, alert_class=alert_class
                    )
              
                )

            else:
                category_id=data['category_id']
                # existing_category['category_id']
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(
                    "INSERT INTO sub_category(sub_category_name,category_id) VALUES(%s,%s)",
                    (sub_category_name,category_id),
                )
                mysql.connection.commit()
                cursor.close()
                message = "Sub category successfully added "
                alert_class = "success"
                return redirect(
                    url_for(
                        ".admin_sub_categories", message=message, alert_class=alert_class,
                    )
                )
    return render_template(
            "admin_sub_categories.html",
            message=message,
            alert_class=alert_class,
            current_page=current_page,admin=admin
        )



@admin_blueprint.route("/admin/edit_sub_category/<int:sub_category_id>", methods=["GET"])
def admin_edit_sub_category(sub_category_id):
    current_page = "products"
    if (
        "logged_in" not in session
        or not session["logged_in"]
        or "usertype" not in session
        or session["usertype"] != "admin_user"
    ):
        return redirect(url_for(".admin_login"))
    else:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM admin")
        admin = cursor.fetchone()
        cursor.close()
        # admin_id=session['admin_id']
        message = request.args.get("message", "")
        aleidrt_class = request.args.get("alert_class")
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT sb.*,c.* FROM sub_category AS sb JOIN category as c ON sb.category_id=c.category_id",)
        sub_category=cursor.fetchone()
        cursor.close()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT * FROM category")
        category=cursor.fetchall()
    return render_template(
        "edit_sub_category.html",
        sub_category=sub_category,
        sub_category_id=sub_category_id,
        current_page=current_page,category=category,admin=admin
    )


@admin_blueprint.route("/save_sub_category/<int:sub_category_id>", methods=["POST"])
def save_sub_category(sub_category_id):
    current_page = "Sub Categories"
    if request.method=='POST':
        if (
            "logged_in" not in session
            or not session["logged_in"]
            or "usertype" not in session
            or session["usertype"] != "admin_user"
        ):
            return redirect(url_for(".admin_login"))
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM admin")
            admin = cursor.fetchone()
            cursor.close()
            message = request.args.get("message", "")
            alert_class = request.args.get("alert_class")
            data=request.form
            
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(f"SELECT * FROM sub_category WHERE sub_category_id={sub_category_id}")
            sub_category=cursor.fetchone()
            cursor.close()
            sub_category_name = data["sub_category_name"]
            category_id=data['category_id']
            print(category_id)
            

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                    f"UPDATE sub_category SET sub_category_name=%s,category_id=%s WHERE sub_category_id={sub_category_id}",
                    (sub_category_name,category_id),
                )
            mysql.connection.commit()
            cursor.close()
            message = "Sub Category updated successfullly"
            alert_class = "success"
            return redirect(
                    url_for(
                        ".admin_sub_categories",
                        message=message,
                        alert_class=alert_class,
                        sub_category_id=sub_category_id,
                    )
                )

    return render_template(
        "edit_sub_category.html", sub_category_id=sub_category_id, current_page=current_page,sub_category=sub_category,admin=admin
    )
    
    
@admin_blueprint.route("/admin/delete_sub_category/<int:sub_category_id>", methods=["POST"])
def admin_delete_sub_category(sub_category_id):
    current_page = "Sub Categories"
    if request.method=='POST':
        if (
            "logged_in" not in session
            or not session["logged_in"]
            or "usertype" not in session
            or session["usertype"] != "admin_user"
        ):
            return redirect(url_for(".admin_login"))
        else:
            
            message = request.args.get("message", "")
            alert_class = request.args.get("alert_class")
            
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                    f"DELETE FROM sub_category WHERE sub_category_id={sub_category_id}",
                )
            mysql.connection.commit()
            cursor.close()
            message = "Sub Category Deleted Successfullly"
            alert_class = "success"
            return redirect(
                    url_for(
                        ".admin_sub_categories",
                        message=message,
                        alert_class=alert_class,
                        sub_category_id=sub_category_id,
                    )
                )
    return render_template(
            "admin_sub_categories.html",
            message=message,
            alert_class=alert_class,
            current_page=current_page,
        )
