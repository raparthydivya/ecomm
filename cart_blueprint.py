from flask import (
    Blueprint,
    render_template,
    request,
    Flask,
    redirect,
    session,
    url_for,
    flash,
)
import pandas as pd
from datetime import datetime
from openpyxl import load_workbook
from flask_mysqldb import MySQL
import MySQLdb.cursors


cart_blueprint = Blueprint("cart_blueprint", __name__)

app = Flask(__name__)
mysql = MySQL(app)


@cart_blueprint.route("/addproduct_cart/<int:product_id>", methods=["GET"])
def addproduct_cart(product_id):
    if "logged_in" not in session or not session["logged_in"]:
        print(session)
        return redirect(url_for("login_blueprint.login"))
    else:
        if product_id:
            user_id = session["user_id"]
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT * FROM cart WHERE user_id = %s AND product_id=%s",
                (user_id, product_id),
            )
            account = cursor.fetchone()
            if account:
                message = "product already exists in your cart"
                alert_class = "warning"
            else:
                cursor.execute(
                    "INSERT INTO cart (user_id,product_id) VALUES (%s,%s)",
                    (user_id, product_id),
                )
                mysql.connection.commit()
                message = "product successfully added to cart"
                alert_class = "success"
                cursor.close()
            return redirect(
                url_for(
                    "cart_blueprint.view_cart", message=message, alert_class=alert_class
                )
            )
    return redirect(url_for("cart_blueprint.view_cart",message=message, alert_class=alert_class))

@cart_blueprint.route("/view_cart", methods=["GET"])
def view_cart():
    if "logged_in" not in session or not session["logged_in"]:
        return redirect("login")
    else:
        user_id = session["user_id"]
        message = request.args.get("message",'')
        alert_class=request.args.get('alert_class')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            f"SELECT c.*,p.image,p.name,p.amount FROM cart AS c JOIN product as p ON p.product_id=c.product_id WHERE c.user_id={user_id}"
        )
        cart_items = cursor.fetchall()
        cursor.close()
        # print(cart_items)
        # print(user_id)

    return render_template(
        "cart.html",message=message,alert_class=alert_class,
        cart_items=cart_items,
    )


@cart_blueprint.route("/delete_cart", methods=["POST"])
def delete_cart():
    if "logged_in" not in session or not session["logged_in"]:
        return redirect("login")
    else:
        user_id = session["user_id"]
        product_id = request.form.get("product_id")
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            f" DELETE FROM cart WHERE user_id={user_id} AND product_id={product_id}"
        )
        mysql.connection.commit()
        cursor.close()
        message="Product successfully removed from your cart"
        alert_class='success'
        return redirect(url_for("cart_blueprint.view_cart",message=message, alert_class=alert_class))
