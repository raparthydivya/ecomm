from flask import Blueprint, render_template,request,Flask
from datetime import datetime
import pandas as pd
from openpyxl import load_workbook
from flask_mysqldb import MySQL
import MySQLdb.cursors


company_blueprint = Blueprint("company_blueprint", __name__)
app = Flask(__name__)
mysql = MySQL(app)

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