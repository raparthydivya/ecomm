from flask import Blueprint,render_template,request,Flask,session
import pandas as pd
from datetime import datetime
from openpyxl import load_workbook
from flask_mysqldb import MySQL
import MySQLdb.cursors

 
product_blueprint= Blueprint('product_blueprint', __name__)
app = Flask(__name__)
mysql = MySQL(app)
@product_blueprint.route('/add_product', methods=['GET','POST'])
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
            cursor.execute(
                f"SELECT * FROM product WHERE model_number = {model_number}"
            )
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



@product_blueprint.route("/get_product/<ids>", methods=["GET"])
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
    
    
@product_blueprint.route('/view_product/<int:product_id>',methods=['GET'])
def view_product(product_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM product WHERE product_id=%s",(product_id,))
    product=cursor.fetchone()
    cursor.close()
    # if not product: 
    #     return " No more products available"
    return render_template('view_product.html',product=product,product_id=product_id)
 
      
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
#     if request.method=='POST':
#         details=pd.read_excel('open_ecommerce.xlsx',sheet_name='products')
#         company_id=request.form.get('company_id')
#         product_code=request.form.get('product_code')
#         name=request.form.get('name')
#         description=request.form.get('description')
#         updated_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         model_number=request.form.get('model_number')
#         if not name:
#             return {'status':'failure','message':'name cannot be empty','data':'','traceback':''}
#         if model_number in details['model_number'].values:
#             return {'status':'failure','message':'model number already exists','data':'','traceback':''}
#         print(details['product_id'].max())
#         max_product_id=details['product_id'].max()
#         new_product_id=max_product_id+1

#         wb=load_workbook('open_ecommerce.xlsx')
#         ws=wb.active
#         ws.append([new_product_id,company_id,product_code,name,description,updated_date,updated_date,model_number])
#         wb.save('open_ecommerce.xlsx')
#         return {
#             'status':'sucess',
#             'message':'Product added successfully',
#             'data': {'product_id':int(new_product_id)},
#             'traceback':''
#             } 
#     return render_template('product.html')

# @product_blueprint.route('/get_products/<ids>')
# def get_products(ids):
#     id_list=[int(id) for id in ids.split(',')]
#     details=pd.read_excel('open_ecommerce.xlsx',sheet_name='products')
#     product_data=details[details['product_id'].isin(id_list)]

#     data={
#         'product':[],
#         'missing_products':[]
        
#     }
#     for id in id_list: 
#         for index,row in product_data.iterrows(): 
#             if row ['product_id'] == id:
#                 product = { 
#                            'product_id':row['product_id'], 
#                     'company_id':row['company_id'],
#                 'name':row['name']if not pd.isna(row['name']) else ' ',
#                 'product_code':row['product_code']if not pd.isna(row['product_code']) else ' ',
#                 'description':row['description']if not pd.isna(row['description']) else ' ',
#                 'model_number':row['model_number']if not pd.isna(row['model_number']) else ' '} 
#                 data['product'].append(product) 
#                 break 
#             else: 
#                 data['missing_products'].append(id)
            
        
#     return{
#             'status':'sucess',
#             'message':'Product Details',
#             'data': data,
#             'traceback':''
#     }