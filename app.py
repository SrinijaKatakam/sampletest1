from flask import Flask, request
from flask import render_template
import textwrap
import pyodbc
from datetime import datetime, timedelta
from azure.storage.blob import generate_container_sas, ContainerSasPermissions

app = Flask(__name__)

if __name__ == '_main_':
    app.run()

account_name = "sristorageblobcontainer"
account_key = "FnTE/wQ7bffP3go+ZV2erldm9lZe+WAee9kxnQ9pXIosoINJrh6gw0irR8xH87BT+Bg0Eh6C+AeX/vqFYaykdw=="
container_name = "quiz1container"

driver = '{ODBC Driver 17 for SQL Server}'

server_name = 'databasetest3'
database_name = 'test'


server = '{server_name}.database.windows.net,1433'.format(server_name=server_name)

username = "srinija"
password = "Texas@123"

connection_string = textwrap.dedent('''
    Driver={driver};
    Server={server};
    Database={database};
    Uid={username};
    Pwd={password};
    Encrypt=yes;
    TrustServerCertificate=no;
    Connection Timeout=30;
'''.format(
    driver=driver,
    server=server,
    database=database_name,
    username=username,
    password=password
))


def get_img_url_with_container_sas_token(blob_name):
    container_sas_token = generate_container_sas(
        account_name=account_name,
        container_name=container_name,
        account_key=account_key,
        permission=ContainerSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1)
    )
    blob_url_with_container_sas_token = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{container_sas_token}"
    return blob_url_with_container_sas_token

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/disppic')
def disp_pic():
    img_names = []
    img_names_sorted = []
    img_sorted_links = []
    cnxx: pyodbc.Connection = pyodbc.connect(connection_string)
    crsr: pyodbc.Cursor = cnxx.cursor()
    select_sql = "select Picture from people where salary < 99000"
    crsr.execute(select_sql)
    for row in crsr:
        for data in row:
            img_names.append(data)
    cnxx.close()
    for names in img_names:
        if names != None:
            img_names_sorted.append(names)
    for values in img_names_sorted:
        img_sorted_links.append(get_img_url_with_container_sas_token(values))
    return render_template("disppic.html", sas_tokens = img_sorted_links)


@app.route('/keyupdate', methods =["GET", "POST"])
def key_update():
    row_values = []
    if request.method == "POST":
        keyword = request.form.get("keywordchange")
    print(keyword)
    cnxx: pyodbc.Connection = pyodbc.connect(connection_string)
    crsr: pyodbc.Cursor = cnxx.cursor()
    # select_sql = "update people set Keywords=? where Name='Dhruvi'"
    crsr.execute("update people set Keywords=? where Name='Dhruvi'", keyword)
    cnxx.commit()
    cnxx.close()
    conn: pyodbc.Connection = pyodbc.connect(connection_string)
    cur: pyodbc.Cursor = conn.cursor()
    select_sql = "select * from people where Name='Dhruvi'"
    cur.execute(select_sql)
    for data in cur:
        for values in data:
            row_values.append(values)
    print(row_values)
    conn.close()
    return render_template("keyupdate.html", row_values = row_values)


@app.route('/salaryupdate', methods =["GET", "POST"])
def salary_update():
    salary = []
    if request.method == "POST":
        Name = request.form.get("salaryname")
        new_salary = request.form.get("salary")
        print(Name)
        print(new_salary)
    cnxx: pyodbc.Connection = pyodbc.connect(connection_string)
    crsr: pyodbc.Cursor = cnxx.cursor()
    # select_sql = "update people set Keywords=? where Name='Dhruvi'"
    crsr.execute("update people set Salary=? where Name=?", new_salary, Name)
    cnxx.commit()
    cnxx.close()
    conn: pyodbc.Connection = pyodbc.connect(connection_string)
    cur: pyodbc.Cursor = conn.cursor()
    # select_sql = "select * from people where id=?"
    cur.execute("select * from people where Name=?", Name)
    for data in cur:
        for values in data:
            salary.append(values)
    print(salary)
    conn.close()
    return render_template("salaryupdate.html", salary=salary)

