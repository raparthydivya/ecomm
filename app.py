from flask import Flask, request, redirect, json, jsonify,render_template,url_for
from login_blueprint import login_blueprint
from register_blueprint import register_blueprint
from company_blueprint import company_blueprint
from product_blueprint import product_blueprint
from cart_blueprint import cart_blueprint
from wishlist_blueprint import wishlist_blueprint
from user_blueprint import user_blueprint

import pandas as pd
import numpy as np
from openpyxl import load_workbook
from datetime import datetime
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)

app.secret_key = "key"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "password"
app.config["MYSQL_DB"] = "ecomm"

mysql = MySQL(app)

app.register_blueprint(login_blueprint)
app.register_blueprint(register_blueprint)
app.register_blueprint(company_blueprint)
app.register_blueprint(product_blueprint)
app.register_blueprint(cart_blueprint)
app.register_blueprint(wishlist_blueprint)
app.register_blueprint(user_blueprint)


@app.route("/")
def hello():
    return ''






































@app.route("/company", methods=["POST"])
def company():
    details = pd.read_excel("open_ecommerce.xlsx", sheet_name="company")
    company_name = request.get_json()["company_name"]
    status = request.get_json()["status"]
    updated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for index, row in details.iterrows():
        print(row["company_name"], row["status"])
        if str(company_name) == str(row["company_name"]) and str(status) == str(
            row["status"]
        ):
            return "Valid User found"
    print(company_name)
    print(status)
    return {
        "status": "sucess",
        "message": "Company exists",
        "data": "",
        "traceback": "",
    }


@app.route("/companydetails", methods=["POST", "GET"])
def companydetails():
    details = pd.read_excel("open_ecommerce.xlsx", sheet_name="company")
    company_name = request.get_json()["company_name"]
    status = request.get_json()["status"]
    print(company_name)
    print(details["company_name"].str.lower().tolist())
    updated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not company_name.strip():
        return {
            "status": "error",
            "message": "Company name cannot be empty",
            "data": "",
            "traceback": "",
        }
    if company_name.lower() in details["company_name"].str.lower().tolist():
        return {
            "status": "failure",
            "message": "Company already exists",
            "data": "",
            "traceback": "",
        }

    print(details["company_id"].max())
    max_company_id = details["company_id"].max()
    new_company_id = max_company_id + 1

    wb = load_workbook("open_ecommerce.xlsx")
    ws = wb.active
    ws.append([new_company_id, company_name, status, updated_date, updated_date])
    wb.save("open_ecommerce.xlsx")

    return {
        "status": "sucess",
        "message": "Company added successfully",
        "data": {"company_id": int(new_company_id)},
        "traceback": "",
    }


@app.route("/productdetails", methods=["POST"])
def productdetails():
    details = pd.read_excel("open_ecommerce.xlsx", sheet_name="products")
    company_id = request.get_json()["company_id"]
    product_code = request.get_json()["product_code"]
    name = request.get_json()["name"]
    description = request.get_json()["description"]
    updated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    model_number = request.get_json()["model_number"]
    if not name.strip():
        return {
            "status": "failure",
            "message": "name cannot be empty",
            "data": "",
            "traceback": "",
        }
    if model_number in details["model_number"].values:
        return {
            "status": "failure",
            "message": "model number already exists",
            "data": "",
            "traceback": "",
        }
    print(details["product_id"].max())
    max_product_id = details["product_id"].max()
    new_product_id = max_product_id + 1

    wb = load_workbook("open_ecommerce.xlsx")
    ws = wb.active
    ws.append(
        [
            new_product_id,
            company_id,
            product_code,
            name,
            description,
            updated_date,
            updated_date,
            model_number,
        ]
    )
    wb.save("open_ecommerce.xlsx")
    return {
        "status": "sucess",
        "message": "Product added successfully",
        "data": {"product_id": int(new_product_id)},
        "traceback": "",
    }


@app.route("/cart", methods=["POST", "GET"])
def cart():
    details = pd.read_excel("open_ecommerce.xlsx", sheet_name="cart")
    user_id = request.get_json()["user_id"]
    product_id = request.get_json()["product_id"]

    user_data = pd.read_excel("open_ecommerce.xlsx", sheet_name="user_data")
    if user_id not in user_data.index:
        return {
            "status": "failure",
            "message": "Invalid userid",
            "data": {},
            "traceback": "",
        }
    product_data = pd.read_excel("open_ecommerce.xlsx", sheet_name="products")
    if product_id not in product_data.index:
        return {
            "status": "failure",
            "message": "Invalid userid",
            "data": {},
            "traceback": "",
        }
    cart_data = pd.read_excel("open_ecommerce.xlsx", sheet_name="cart")
    if (user_id, product_id) in cart_data.index:
        return {
            "status": "sucess",
            "message": "Product added to cart successful",
            "data": {},
            "traceback": "",
        }
    if ((details["user_id"] == user_id) & (details["product_id"] == product_id)).any():
        return {
            "status": "failure",
            "message": "The given Userid and Productid combination already exists",
            "data": "",
            "traceback": "",
        }

    wb = load_workbook("open_ecommerce.xlsx")
    ws = wb["cart"]
    cart_id_values = [int(row[0]) for row in ws.iter_rows(min_row=2, values_only=True)]
    if cart_id_values:
        cart_id = max(cart_id_values) + 1
    else:
        cart_id = 1
    ws.append([cart_id, user_id, product_id])
    wb.save("open_ecommerce.xlsx")

    return {
        "status": "sucess",
        "message": "Product has been added to the Cart successfully",
        "data": {},
        "traceback": "",
    }


@app.route("/wishlist", methods=["POST"])
def wishlist():
    details = pd.read_excel("open_ecommerce.xlsx", sheet_name="wishlist")
    user_id = request.get_json()["user_id"]
    product_id = request.get_json()["product_id"]

    user_data = pd.read_excel("open_ecommerce.xlsx", sheet_name="user_data")
    if user_id not in user_data.index:
        return {
            "status": "failure",
            "message": "Invalid userid",
            "data": {},
            "traceback": "",
        }
    product_data = pd.read_excel("open_ecommerce.xlsx", sheet_name="products")
    if product_id not in product_data.index:
        return {
            "status": "failure",
            "message": "Invalid Productid",
            "data": {},
            "traceback": "",
        }

    wishlist_data = pd.read_excel("open_ecommerce.xlsx", sheet_name="wishlist")
    if ((details["user_id"] == user_id) & (details["product_id"] == product_id)).any():
        return {
            "status": "failure",
            "message": "The given Userid and Productid combination already exists",
            "data": "",
            "traceback": "",
        }

    wb = load_workbook("open_ecommerce.xlsx")
    ws = wb["wishlist"]
    wishlist_id_values = [
        int(row[0]) for row in ws.iter_rows(min_row=2, values_only=True)
    ]
    if wishlist_id_values:
        wishlist_id = max(wishlist_id_values) + 1
    else:
        wishlist_id = 1
    ws.append([wishlist_id, user_id, product_id])
    wb.save("open_ecommerce.xlsx")

    return {
        "status": "sucess",
        "message": "Product has been added to the wishlist successfully",
        "data": {},
        "traceback": "",
    }


@app.route("/get_products/<ids>")
def get_products(ids):
    id_list = [int(id) for id in ids.split(",")]
    details = pd.read_excel("open_ecommerce.xlsx", sheet_name="products")
    product_data = details[details["product_id"].isin(id_list)]

    data = {"product": [], "missing_products": []}
    for id in id_list:
        for index, row in product_data.iterrows():
            if row["product_id"] == id:
                product = {
                    "product_id": row["product_id"],
                    "company_id": row["company_id"],
                    "name": row["name"] if not pd.isna(row["name"]) else " ",
                    "product_code": row["product_code"]
                    if not pd.isna(row["product_code"])
                    else " ",
                    "description": row["description"]
                    if not pd.isna(row["description"])
                    else " ",
                    "model_number": row["model_number"]
                    if not pd.isna(row["model_number"])
                    else " ",
                }
                data["product"].append(product)
                break
            else:
                data["missing_products"].append(id)

    return {
        "status": "sucess",
        "message": "Product Details",
        "data": data,
        "traceback": "",
    }


@app.route("/get_company/<ids>")
def get_company(ids):
    id_list = [int(id) for id in ids.split(",")]
    details = pd.read_excel("open_ecommerce.xlsx", sheet_name="company")
    company_data = details[details["company_id"].isin(id_list)]

    data = {"company": [], "missing_company": []}
    for id in id_list:
        for index, row in company_data.iterrows():
            if row["company_id"] == id:
                company = {
                    "company_id": row["company_id"],
                    "company_name": row["company_name"],
                    "status": row["status"],
                }
                data["company"].append(company)
                break
            else:
                data["missing_company"].append(id)

    return {
        "status": "sucess",
        "message": "Company Details",
        "data": data,
        "traceback": "",
    }


@app.route("/get_user/<ids>")
def get_user(ids):
    id_list = [int(id) for id in ids.split(",")]
    details = pd.read_excel("open_ecommerce.xlsx", sheet_name="user_data")
    user_data = details[details["user_id"].isin(id_list)]
    data = {"users": [], "missing_users": []}
    for id in id_list:
        for index, row in user_data.iterrows():
            if row["user_id"] == id:
                users = {
                    "user_id": row["user_id"],
                    "username": row["username"],
                    "mobile": row["mobile"],
                    "password": row["password"],
                }
                data["users"].append(users)
                break
            else:
                data["missing_users"].append(id)

    return {
        "status": "sucess",
        "message": "User Details",
        "data": data,
        "traceback": "",
    }


if __name__ == "__main__":
    app.run(port=5004, debug=True)


# if __name__=='__main__':
#     app.run(debug=True)
