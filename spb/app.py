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
def current_jobs():
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


if __name__ == '__main__':
    app.run(port=5000, debug=True)
