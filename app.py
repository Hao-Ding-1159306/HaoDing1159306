import re
from datetime import datetime

import mysql.connector
from flask import Flask, redirect, render_template, request, url_for
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
    results = cursor.fetchall()
    results = [{'job_id': row[0], 'full_name': row[1], 'job_date': row[2]} for row in results]
    print(results)
    cursor.close()
    return render_template("currentjoblist.html", results=results)

def search_part_service(job_id):
    part_query = """
                        SELECT 
                            p.part_id,
                            p.part_name,
                            p.cost,
                            COALESCE(jp.qty, 0) AS qty
                        FROM
                            part p
                        LEFT JOIN
                            job_part jp ON p.part_id = jp.part_id AND jp.job_id = %s;
                     """
    cursor = getCursor()
    cursor.execute(part_query, (job_id,))
    part_results = cursor.fetchall()
    cursor.close()
    print('part_results', part_results)
    part_results = [{'part_id': row[0], 'part_name': row[1], 'cost': row[2], 'qty': row[3]} for row in part_results]

    service_query = """
                            SELECT 
                                s.service_id,
                                s.service_name,
                                s.cost,
                                COALESCE(js.qty, 0) AS qty
                            FROM
                                service s
                            LEFT JOIN
                                job_service js ON s.service_id = js.service_id AND js.job_id = %s;
                        """
    cursor = getCursor()
    cursor.execute(service_query, (job_id,))
    service_results = cursor.fetchall()
    cursor.close()
    print('service_results', service_results)
    service_results = [{'service_id': row[0], 'service_name': row[1], 'cost': row[2], 'qty': row[3]} for row in service_results]

    return part_results, service_results


@app.route('/job/<int:job_id>', methods=['GET', 'POST'])
def job(job_id):
    part_results, service_results = search_part_service(job_id)
    if request.method == 'POST':
        part_ids = request.form.getlist('part_id[]')
        part_quantities = request.form.getlist('part_qty[]')
        service_ids = request.form.getlist('service_id[]')
        service_quantities = request.form.getlist('service_qty[]')
        print('\n',part_ids,part_quantities,service_ids,service_quantities,'\n')
        # add part
        for part_id, part_qty in zip(part_ids, part_quantities):
            print(part_id, part_qty)
            if int(part_qty) == 0:
                continue
            # check
            query = "SELECT * FROM job_part WHERE job_id = %s AND part_id = %s"
            cursor = getCursor()
            cursor.execute(query, (job_id, part_id))
            result = cursor.fetchone()

            if result:
                # update
                update_query = "UPDATE job_part SET qty = %s WHERE job_id = %s AND part_id = %s"
                cursor.execute(update_query, (part_qty, job_id, part_id))
            else:
                # insert
                insert_query = "INSERT INTO job_part (job_id, part_id, qty) VALUES (%s, %s, %s)"
                cursor.execute(insert_query, (job_id, part_id, part_qty))

            cursor.close()
        # add service
        for service_id, service_qty in zip(service_ids, service_quantities):
            print(service_id, service_qty,type(service_qty))
            if int(service_qty) == 0:
                continue
            # check
            query = "SELECT * FROM job_service WHERE job_id = %s AND service_id = %s"
            cursor = getCursor()
            cursor.execute(query, (job_id, service_id))
            result = cursor.fetchone()

            if result:
                # update
                update_query = "UPDATE job_service SET qty = %s WHERE job_id = %s AND service_id = %s"
                cursor.execute(update_query, (service_qty, job_id, service_id))
            else:
                # insert
                insert_query = "INSERT INTO job_service (job_id, service_id, qty) VALUES (%s, %s, %s)"
                cursor.execute(insert_query, (job_id, service_id, service_qty))

            cursor.close()
        return redirect('/currentjobs')
    if request.method == 'GET':
        return render_template('job.html', job_id=job_id, services=service_results, parts=part_results)

@app.route('/complete_job/<int:job_id>')
def complete_job(job_id):
    # mark completed
    cursor = getCursor()
    update_query = "UPDATE job SET completed = 1 WHERE job_id = %s"
    cursor.execute(update_query, (job_id,))
    cursor.close()
    # total cost is calculated
    part_results, service_results = search_part_service(job_id)
    cost = 0
    for part in part_results:
        print(part)
        cost+=part['cost'] *part['qty']
    for service in service_results:
        print(service)
        cost+=service['cost'] *service['qty']
    print(cost)
    cursor = getCursor()
    update_query = "UPDATE job SET total_cost = %s WHERE job_id = %s"
    cursor.execute(update_query, (cost, job_id,))
    cursor.close()
    return redirect(url_for('currentjobs'))


@app.route("/administrator")
def administrator():
    return render_template("administrator.html")


@app.route("/administrator/customer", methods=['GET', 'POST'])
def customer(per_page=10):
    page = int(request.args.get('page', 1))
    search_value = request.args.get('search', '').strip()

    cursor = getCursor()
    total_count, results = get_customer_results(cursor, page, search_value, per_page)
    total_pages = (total_count + per_page - 1) // per_page
    return render_template("customer.html", results=results, page=page, total_pages=total_pages,
                           search_value=search_value)


def get_customer_results(cursor, page, search_value, per_page):
    offset = (page - 1) * per_page
    query = "SELECT * FROM customer"
    params = ()
    if search_value:
        query += " WHERE family_name LIKE %s OR first_name LIKE %s"
        params = (f'%{search_value}%', f'%{search_value}%')
    query += "\nORDER BY family_name, first_name;"
    cursor.execute(query, params)
    results = cursor.fetchall()
    results = [{'customer_id': row[0], 'first_name': row[1], 'family_name': row[2], 'email': row[3], 'phone': row[4]}
               for row in results]
    total_count = cursor.rowcount
    results = results[offset:offset + per_page]
    cursor.close()
    return total_count, results


@app.route('/administrator/customer/add', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        # get from data
        first_name = request.form['first_name']
        family_name = request.form['family_name']
        email = request.form['email']
        phone = request.form['phone']
        print('first_name:', first_name)
        # Perform additional custom validation if needed
        if len(first_name) != 0 and not first_name.isalpha():
            error_msg = 'Invalid first name. First name must be a string and should not contain symbols.'
            return render_template('addcustomer.html', error_msg=error_msg)

        if not family_name.isalpha():
            error_msg = 'Invalid family name. Family name must be a string and should not contain symbols.'
            return render_template('addcustomer.html', error_msg=error_msg)
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            error_msg = 'Invalid email address format.'
            return render_template('addcustomer.html', error_msg=error_msg)
        try:
            phone = int(phone)  # Assuming phone should be an integer
        except ValueError:
            error_msg = 'Invalid phone number. Phone must be a number.'
            return render_template('addcustomer.html', error_msg=error_msg)

        # insert new part info in to database
        cursor = getCursor()
        if first_name is not None:
            cursor.execute("INSERT INTO customer (first_name, family_name, email, phone) VALUES (%s, %s, %s, %s)",
                           (first_name, family_name, email, phone))
        else:
            cursor.execute("INSERT INTO customer (family_name, email, phone) VALUES (%s, %s, %s)",
                           (family_name, email, phone))

        cursor.close()

        return redirect('/administrator/customer')

    return render_template('addcustomer.html')


@app.route('/administrator/customer/create_job/<int:customer_id>', methods=['GET', 'POST'])
def create_job(customer_id):
    family_name = request.args.get('family_name')
    if request.method == 'POST':
        job_date = request.form['job_date']
        date_format = "%Y-%m-%d"
        job_date = datetime.strptime(job_date, date_format).date()
        today = datetime.today().date()
        print(job_date, today)
        if job_date < today:
            error_msg = 'The date must be today or in the future.'
            return render_template('create_job.html', customer_id=customer_id, family_name=family_name,
                                   error_msg=error_msg)
        cursor = getCursor()
        cursor.execute("INSERT INTO job (`job_date`, `customer`) VALUES (%s, %s)", (job_date, customer_id))
        cursor.close()
        return redirect('/administrator/customer')
    return render_template('create_job.html', customer_id=customer_id, family_name=family_name)


@app.route("/administrator/service")
def service(per_page=10):
    page = int(request.args.get('page', 1))
    search_value = request.args.get('search', '').strip()

    cursor = getCursor()
    total_count, results = get_service_results(cursor, page, search_value, per_page)
    total_pages = (total_count + per_page - 1) // per_page
    return render_template("service.html", results=results, page=page, total_pages=total_pages,
                           search_value=search_value)


def get_service_results(cursor, page, search_value, per_page):
    offset = (page - 1) * per_page
    query = "SELECT * FROM service"
    params = ()
    if search_value:
        query += " WHERE service_name LIKE %s"
        params = (f'%{search_value}%',)
    cursor.execute(query, params)
    results = cursor.fetchall()
    results = [{'service_id': row[0], 'service_name': row[1], 'cost': row[2]} for row in results]
    total_count = cursor.rowcount
    results = results[offset:offset + per_page]
    cursor.close()
    return total_count, results


@app.route('/administrator/service/add', methods=['GET', 'POST'])
def add_service():
    if request.method == 'POST':
        # get from data
        name = request.form['name']
        cost = request.form['cost']

        if not name or not name.isalpha():
            error_msg = 'Invalid name. Name must be a string and should not contain symbols.'
            return render_template('addpart.html', error_msg=error_msg)

        try:
            cost = float(cost)
        except ValueError:
            error_msg = 'Invalid cost. Cost must be a number.'
            return render_template('addpart.html', error_msg=error_msg)

        # insert new part info in to database
        cursor = getCursor()
        cursor.execute("INSERT INTO service (service_name, cost) VALUES (%s, %s)", (name, cost))
        cursor.close()

        return redirect('/administrator/service')

    return render_template('addservice.html')


@app.route("/administrator/part", methods=['GET'])
def part(per_page=10):
    page = int(request.args.get('page', 1))
    search_value = request.args.get('search', '').strip()

    cursor = getCursor()
    total_count, results = get_part_results(cursor, page, search_value, per_page)
    total_pages = (total_count + per_page - 1) // per_page
    return render_template("part.html", results=results, page=page, total_pages=total_pages, search_value=search_value)


def get_part_results(cursor, page, search_value, per_page):
    offset = (page - 1) * per_page
    query = "SELECT * FROM part"
    params = ()
    if search_value:
        query += " WHERE part_name LIKE %s"
        params = (f'%{search_value}%',)
    cursor.execute(query, params)
    results = cursor.fetchall()
    results = [{'part_id': row[0], 'part_name': row[1], 'cost': row[2]} for row in results]
    total_count = cursor.rowcount
    results = results[offset:offset + per_page]
    cursor.close()
    return total_count, results


@app.route('/administrator/part/add', methods=['GET', 'POST'])
def add_part():
    if request.method == 'POST':
        # get from data
        name = request.form['name']
        cost = request.form['cost']

        if not name or not name.isalpha():
            error_msg = 'Invalid name. Name must be a string and should not contain symbols.'
            return render_template('addpart.html', error_msg=error_msg)

        try:
            cost = float(cost)
        except ValueError:
            error_msg = 'Invalid cost. Cost must be a number.'
            return render_template('addpart.html', error_msg=error_msg)

        # insert new part info in to database
        cursor = getCursor()
        cursor.execute("INSERT INTO part (part_name, cost) VALUES (%s, %s)", (name, cost))
        cursor.close()

        return redirect('/administrator/part')

    return render_template('addpart.html')


@app.route("/administrator/unpaidbills")
def unpaidbills():
    cursor = getCursor()
    query = """
            SELECT j.job_id, IFNULL(CONCAT(c.first_name, ' ', c.family_name), c.family_name) AS full_name, j.job_date
            FROM job j
            INNER JOIN customer c ON j.customer = c.customer_id
            WHERE j.completed = 1
        """
    return render_template("unpaidbills.html")


@app.route('/administrator/unpaidbills/filter_bills', methods=['POST'])
def filter_bills():
    selected_customer = request.form['customer']
    filtered_bills = [bill for bill in unpaid_bills if bill[1] == selected_customer]
    return render_template('index.html', unpaid_bills=filtered_bills)


@app.route("/administrator/billinghistory")
def billinghistory():
    return render_template("billinghistory.html")


if __name__ == '__main__':
    app.run(port=5000, debug=True)
