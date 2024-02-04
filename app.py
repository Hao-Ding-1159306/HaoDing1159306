from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect

app = Flask(__name__)

dbconn = None
connection = None


def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser,
                                         password=connect.dbpass, host=connect.dbhost,
                                         database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn


@app.route("/")
def home():
    return redirect("/currentjobs")


@app.route("/currentjobs")
def currentjobs():
    cursor = getCursor()

    query = """
        SELECT j.job_id, IFNULL(CONCAT(c.first_name, ' ', c.family_name), c.family_name) AS full_name, j.job_date
        FROM job j
        INNER JOIN customer c ON j.customer = c.customer_id
        WHERE j.completed = 0
    """
    cursor.execute(query)
    jobList = cursor.fetchall()
    return render_template("currentjoblist.html", job_list=jobList)


@app.route("/administrator")
def administrator():
    return render_template("administrator.html")


@app.route("/administrator/customer", methods=['GET'])
def customer():
    # 获取搜索关键字
    search_value = request.args.get('search')
    print(f'search_value: {search_value}')
    cursor = getCursor()
    if search_value is not None:
        query = """
            SELECT * FROM customer WHERE family_name LIKE %s OR first_name LIKE %s
            ORDER BY family_name, first_name;
        """
        params = (f'%{search_value}%', f'%{search_value}%')
        cursor.execute(query, params)
    else:

        query = """
                SELECT * FROM customer
                ORDER BY family_name, first_name;
        """
        cursor.execute(query)
    customer_list = cursor.fetchall()
    return render_template("customer.html", customer_list=customer_list)


@app.route("/administrator/service")
def service():
    return render_template("service.html")


@app.route("/administrator/part")
def part():
    return render_template("part.html")


@app.route("/administrator/billinghistory")
def billinghistory():
    return render_template("billinghistory.html")


if __name__ == '__main__':
    app.run(port=5000, debug=True)
