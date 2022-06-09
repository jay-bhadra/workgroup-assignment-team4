
from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash, check_password_hash
import cx_Oracle
import os
import socket

app = Flask(__name__)

os.environ['TNS_ADMIN'] = r'\adb'
# lib_dir = '/instantclient_21_3'
# cx_Oracle.init_oracle_client(lib_dir=lib_dir)


# #ocl_host = cx_Oracle.makedsn(r'adb.eu-frankfurt-1.oraclecloud.com', '1522', service_name=r'g0db1faf08c4cbf_db202203191726_medium.adb.oraclecloud.com')
# ocl_user = 'ADMIN'
ocl_pw = r'Iberia123456'
# ocl_host = r'db202203191726_medium'

pub_ip = r"35.198.145.47"
dbname = r"Iberia_IT"
project_id = r"elated-lotus-344717"
instance_name = r"iberia-it"
db_port = 3306


# ocl_connection = cx_Oracle.connect(ocl_user, password=ocl_pw, dsn=ocl_host)
# #ocl_connection = ocl_connection.cursor()

app.config["SECRET_KEY"] = "this is not secret, remember, change it!"
app.config["SQLALCHEMY_DATABASE_URI"]= f"mysql + mysqldb://root:{ocl_pw}@{pub_ip}/{dbname}?unix_socket =/cloudsql/{project_id}:{instance_name}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= True

db_url = f"mysql+pymysql://root:{ocl_pw}@{pub_ip}:{db_port}/{dbname}" #TCP
#db_url = r"mysql+pymysql://root:{ocl_pw}@{pub_ip}/{dbname}?unix_socket=/cloudsql/{project_id}:{instance_name}" #UNIX
db = SQLAlchemy(app)

engine = create_engine(db_url)

@app.route("/")
def index():

      
    test_query2 = f"""SELECT DISTINCT support_group FROM monthly_incidents_raised"""   
    
    with engine.connect() as connection:
        test_final = connection.execute(test_query2).fetchall()
        
    return render_template("test.html", test_final=test_final)
        
    
        
    


app.run(debug=True)