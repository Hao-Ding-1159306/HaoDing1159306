# HaoDing1159306

## Web application structure

## Design decisions

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

- **A:** Different people often have different responsibilities and authorities. We cannot allow people to do things
  beyond their authority.

  For example, if a technician can mark an order as paid, he can earn
  additional revenue by charging the customer half the money and then changing the order's payment status.

  Furthermore, if an administrator can fabricate sales by adding items privately without confirmation from technical
  staff.