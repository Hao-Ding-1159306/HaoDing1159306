# HaoDing1159306

## Web application structure

### 1.Technician

#### Current Job

The Current Job page not only contains all the information about the current job, but also needs to add two buttons to
each line, "Edit" and "Complete"

"Edit" will jump a page named "Job Details" to edit all parts and services

"Complete" will mark the job has finished, than change the completed in table job

#### Job Details

This a page for add parts or services for the job. After confirming the addition of the item, modify the corresponding
table job_service and job_part. It will also return to the "Current Job" page

### 2.Admin

#### Customer List

This page contains a search bar, customer details, an "Add Customer" button, and an "Add Job" button for each customer

Search bar terms is used for filter customers

The "Add Customer" button is used to add new customer. It will jump to a new page to enter customer details. After
confirmation, a new piece of data will be inserted into the customer table.

The "Add Job" button is used to add jobs to customer. It will jump to a new page to select the job date. After
confirmation, a new piece of data will be inserted into the job table.

#### Service List

This page contains a search bar, service details and an add "Add Service" button

Search bar terms is used for filter service

The "Add Service" button is used to add a new service. It will jump to a new page to enter service details. After
confirmation, a new piece of data will be inserted into the service table.

#### Part List

This page contains a search bar, part details and an add "Add Part" button

Search bar terms is used for filter part

The "Add Part" button is used to add a new part. It will jump to a new page to enter part details. After
confirmation, a new piece of data will be inserted into the part table.

#### Unpaid Bills List

This page contains a filter bar, unpaid bill details and an add "Mark Paid" button

filter bar terms is used for filter customer

The "Mark Paid" button is used to mark the bill paid, than change the paid in table job

#### Bill History List

This page searches for all completed bills in the job and groups them according to customer information. In addition, it
also filters out long-term unpaid orders and marks them. Finally, it displays all historical orders based on the
processed information.

## Design decisions

- Since Admin needs a common navigation bar, I inherited base.html and wrote administrator.html as a template file for
  most pages that Admin needs to operate.
- Most of the add and edit buttons open a new page for entering or confirming information. On this new page, there are
  usually two buttons: Cancel and Add, which are used for regret and confirmation respectively. After clicking, it will
  return to the original page to continue the operation and confirm the modified information.
- I use a lot of GET or POST to request and send data. For example, on the customer page, I not only need to send search
  terms to filter customers, but also accept filtered information for display.
- I try to minimize the use of if statements and other statements in html pages. The front end only displays the
  information sent by the back end and sends the filled in information to the back end. All additions, deletions,
  modifications and other logical processing related to the database are completed in the backend (app.py). Try to
  ensure the separation of front and back ends

## Database questions

1. What SQL statement creates the job table and defines its fields/columns? (Copy and paste the relevant lines of SQL.)

- **A:**

```sql
 CREATE TABLE IF NOT EXISTS job
(
job_id INT auto_increment PRIMARY KEY NOT NULL,
job_date date NOT NULL,
customer int NOT NULL,
total_cost decimal(6,2) default null,
completed tinyint default 0,
paid tinyint default 0,

FOREIGN KEY (customer) REFERENCES customer(customer_id)
ON UPDATE CASCADE
);
```

2. Which line of SQL code sets up the relationship between the customer and job tables?

- **A:** Use the following line when create the job table

```sql
FOREIGN KEY (customer) REFERENCES customer(customer_id)
ON UPDATE CASCADE
```

3. Which lines of SQL code insert details into the parts table?

- **A:**

```sql
INSERT INTO part (`part_name`, `cost`) VALUES ('Windscreen', '560.65');
INSERT INTO part (`part_name`, `cost`) VALUES ('Headlight', '35.65');
INSERT INTO part (`part_name`, `cost`) VALUES ('Wiper blade', '12.43');
INSERT INTO part (`part_name`, `cost`) VALUES ('Left fender', '260.76');
INSERT INTO part (`part_name`, `cost`) VALUES ('Right fender', '260.76');
INSERT INTO part (`part_name`, `cost`) VALUES ('Tail light', '120.54');
INSERT INTO part (`part_name`, `cost`) VALUES ('Hub Cap', '22.89');
```

4. Suppose that as part of an audit trail, the time and date a service or part was added to a job needed to be recorded,
   what fields/columns would you need to add to which tables? Provide the table name, new column name and the data
   type. (Do not implement this change in your app.)

- **A:** I will add a columns named "create_time" to both job_part and job_service tables. The type of "create_time" is
  datetime

5. Suppose logins were implemented. Why is it important for technicians and the office administrator to access different
   routes? As part of your answer, give two specific examples of problems that could occur if all of the web app
   facilities were available to everyone.

- **A:** Different people often have different responsibilities and authorities. We cannot allow people to do something
  beyond their authority.

  For example, if a technician can mark an order as paid, he can earn
  additional revenue by charging the customer half the money and then changing the order's payment status.

  Furthermore, if an administrator can fabricate sales by adding items privately without confirmation from technical
  staff.