from flask import Flask, render_template, request, session, jsonify
import pandas as pd
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = "key"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "password"
app.config["MYSQL_DB"] = "ecomm"

mysql = MySQL(app)
# result=cursor.fetchall()
# mysql.connection.commit()
# cursor.close()
# print(result)
#     msg=''
#     cursor = mysql.connection.cursor()
#     cursor.execute('SELECT * FROM user')


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        data = request.json
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
    return ""





@app.route("/register", methods=["POST", "GET"])
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
    return render_template("register.html")


@app.route("/add_company", methods=["POST", "GET"])
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


@app.route("/get_company/<ids>", methods=["GET"])
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


@app.route("/add_product", methods=["POST", "GET"])
def add_product():
    if request.method == "POST":
        data = request.json
        if data and "model_number" in data:
            company_id = int(data["company_id"])
            product_code = data["product_code"]
            name = data["name"]
            description = data["description"]
            model_number = int(data["model_number"])
            print(company_id)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(f"SELECT * FROM product WHERE model_number = {model_number}")
            account = cursor.fetchone()
            if account:
                return {
                    "status": "FAILURE",
                    "message": "modelnumber already exists",
                    "data": "",
                    "traceback": "",
                }
            else:
                cursor.execute(
                    "INSERT INTO product(company_id,product_code,name,description,model_number) VALUES (%s,%s,%s,%s,%s)",
                    (company_id, product_code, name, description, model_number),
                )
                mysql.connection.commit()
                return {
                    "status": "SUCESS",
                    "message": "product added successfully",
                    "data": "",
                    "traceback": "",
                }
    return ""


@app.route("/get_product<ids>", methods=["GET"])
def get_product(ids):
    id_list = [int(id) for id in ids.split(",")]
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "SELECT * FROM product WHERE product_id IN ({})".format(
            ",".join(["%s"] * len(id_list))
        ),
        id_list,
    )
    products = cursor.fetchall()
    data = {"products": [], "missing_products": []}
    for id in id_list:
        found = False
        for product in products:
            if product["product_id"] == id:
                data["products"].append(product)
                found = True
                break
        if not found:
            data["missing_products"].append(id)

    return {
        "status": "sucess",
        "message": "Product Details",
        "data": data,
        "traceback": "",
    }


@app.route("/addproduct_cart", methods=["POST", "GET"])
def addproduct_cart():
    if request.method == "POST":
        data = request.json
        if data and "user_id" in data and "product_id" in data:
            user_id = data["user_id"]
            product_id = data["product_id"]

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT * FROM user WHERE user_id = %s",
                (user_id,),
            )
            account = cursor.fetchone()
            if not account:
                return {
                    "status": "FAILURE",
                    "message": "user_id does not exists",
                    "data": "",
                    "traceback": "",
                }
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT * FROM product WHERE product_id = %s",
                (product_id,),
            )
            account = cursor.fetchone()
            if not account:
                return {
                    "status": "FAILURE",
                    "message": " product_id does not exists",
                    "data": "",
                    "traceback": "",
                }
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT * FROM cart WHERE user_id = %s AND product_id=%s",
                (user_id, product_id),
            )
            account = cursor.fetchone()
            if account:
                return {
                    "status": "FAILURE",
                    "message": "user_id and product_id combination already exists",
                    "data": "",
                    "traceback": "",
                }

            else:
                cursor.execute(
                    "INSERT INTO cart(user_id,product_id) VALUES (%s,%s)",
                    (user_id, product_id),
                )
            mysql.connection.commit()
            return {
                "status": "SUCESS",
                "message": "SUCESSFULLY added to cart",
                "data": "",
                "traceback": "",
            }
    return ""


@app.route("/addproduct_wishlist", methods=["POST", "GET"])
def addproduct_wishlist():
    if request.method == "POST":
        data = request.json
        if data and "user_id" in data and "product_id" in data:
            user_id = data["user_id"]
            product_id = data["product_id"]

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT * FROM user WHERE user_id = %s",
                (user_id,),
            )
            account = cursor.fetchone()
            if not account:
                return {
                    "status": "FAILURE",
                    "message": "user_id does not exists",
                    "data": "",
                    "traceback": "",
                }
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT * FROM product WHERE product_id = %s",
                (product_id,),
            )
            account = cursor.fetchone()
            if not account:
                return {
                    "status": "FAILURE",
                    "message": " product_id does not exists",
                    "data": "",
                    "traceback": "",
                }
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT * FROM wishlist WHERE user_id = %s AND product_id=%s",
                (user_id, product_id),
            )
            account = cursor.fetchone()
            if account:
                return {
                    "status": "FAILURE",
                    "message": "user_id and product_id combination already exists",
                    "data": "",
                    "traceback": "",
                }

            else:
                cursor.execute(
                    "INSERT INTO wishlist(user_id,product_id) VALUES (%s,%s)",
                    (user_id, product_id),
                )
            mysql.connection.commit()
            return {
                "status": "SUCESS",
                "message": "SUCESSFULLY added to wishlist",
                "data": "",
                "traceback": "",
            }
    return ""

    # cursor.execute('INSERT INTO user( username,mobile,password) VALUES(%s,%s,%s)',(username,mobile,password))
    # mysql.connection.commit()
    # cursor.close()
    # return 'Registration successful.user added to the database'
    # return render_template('register.html')


#     cursor.execute('INSERT INTO user VALUES(2,"john",990,"john","2023-05-18 21:05:00","2023-05-18 21:05:00");')
#     # result=cursor.fetchall()
#     mysql.connection.commit()
#     cursor.close()
# print(result)


app.run(host="localhost", port=5000, debug=True)


# CREATE TABLE user(
#     user_id int NOT NULL AUTO_INCREMENT ,username varchar(255),mobile int,password varchar(255),created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ,updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
# PRIMARY KEY(user_id))

# CREATE TABLE company(
#     company_id int NOT NULL AUTO_INCREMENT ,company_name varchar(255),status int,created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ,updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
# PRIMARY KEY(user_id))

# CREATE TABLE product(
#     product_id int NOT NULL AUTO_INCREMENT ,company_id int,product_code varchar(255),name varchar(255),description varchar(255),model_number int,created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ,updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
# PRIMARY KEY(product_id))

# CREATE TABLE cart(
#         cart_id int NOT NULL AUTO_INCREMENT,user_id int,product_id int,PRIMARY KEY(cart_id)
# )

# CREATE TABLE wishlist(
#         wishlist_id int NOT NULL AUTO_INCREMENT,user_id int,product_id int,PRIMARY KEY(wishlist_id)
# )
# CREATE TABLE address(
#           address_id int NOT NULL AUTO_INCREMENT, user_id int NOT NULL,street_name varchar(255) NOT NULL,city varchar(255) NOT NULL,state varchar(255) NOT NULL,country varchar(255) NOT NULL,postal_code varchar(255) NOT NULL,created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     PRIMARY KEY(address_id))


# mysql -u root -p


# CREATE USER 'username'@'localhost' IDENTIFIED WITH authentication_plugin BY 'password';

# GRANT CREATE, ALTER, DROP, INSERT, UPDATE, INDEX, DELETE, SELECT, REFERENCES, RELOAD on *.* TO 'root'@'localhost' WITH GRANT OPTION;

# # INSERT INTO user VALUES(1,divya,9999999099,divya)

# INSERT INTO user VALUES(3,'elena',998,'ele',"2023-05-18 23:15:00","2023-05-18 23:15:00");

#  INSERT INTO company VALUES(1,'DELL',1,"2023-05-20 14:15:00","2023-05-20 14:15:00");
# INSERT INTO address VALUES(1,1,'priya colony kharkhana','Hyderabad','Telangana','India','500015',"2023-05-22 23:15:00","2023-05-22 23:15:00")

# cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#                  cursor.execute('INSERT INTO company VALUES(2,"MAC",1,"2023-05-18 15:05:00","2023-05-18 21:05:00");')
# #     # result=cursor.fetchall()
#                  mysql.connection.commit()
