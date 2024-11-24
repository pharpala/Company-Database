import csv
from io import StringIO
import psycopg2
import uuid


DATABASE_CONFIG = {
    "dbname": "flask_db",
    "user": "postgres",
    "password": "password",
    "host": "localhost",
    "port": "5432"
}

#Database Class
class DataBase():
    def __init__(self) -> None:
        self.create_sql_objects()
        self.populate_fake_data()
    
    def get_db_connection(self):
        conn = psycopg2.connect(**DATABASE_CONFIG)
        return conn

    def create_sql_objects(self):
        #drop the tables so we create new ones - gets rid of relationship already exists error
        #create tables 
        conn = self.get_db_connection()
        sql = '''
        DROP VIEW IF EXISTS AllEmployeeData;
        DROP TABLE IF EXISTS Employee;
        DROP TABLE IF EXISTS Project;
        DROP TABLE IF EXISTS Works_On;
        DROP TABLE IF EXISTS Dept_Location;
        
        CREATE TABLE Employee (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role INT NOT NULL,
        Dno INT,
        Fname VARCHAR(10) NOT NULL,
        Minit CHAR NOT NULL,
        Lname VARCHAR(10) NOT NULL,
        SSN CHAR(9) UNIQUE NOT NULL,
        Address VARCHAR(15) NOT NULL,
        Sex CHAR NOT NULL,
        Salary INT NOT NULL
        );
        
        CREATE TABLE Project (
        Pname VARCHAR(15) NOT NULL,
        Pnumber INT NOT NULL,
        Plocation VARCHAR(15) NOT NULL,
        Dnum INT NOT NULL,
        PRIMARY KEY (Pnumber),
        UNIQUE (Pname)
        );

        CREATE TABLE Works_On (
        Essn CHAR(9) NOT NULL,
        Pno INT NOT NULL,
        PRIMARY KEY (Essn, Pno)
        );
        
        CREATE TABLE Dept_Location (
        Dnumber INT NOT NULL,
        Dlocation VARCHAR(15) NOT NULL,
        PRIMARY KEY (Dnumber, Dlocation)
        );

        
        CREATE VIEW AllEmployeeData AS
        SELECT
        E.id, E.username, E.password_hash, E.role, E.Dno, E.Fname, E.Minit, E.Lname, E.SSN, E.Address, E.Sex, E.Salary, P.Pname, P.Pnumber, P.Plocation, P.Dnum, D.Dlocation
        FROM
        Employee E
        LEFT JOIN
        Works_On WO ON E.SSN = WO.Essn
        LEFT JOIN
        Project P ON WO.Pno = P.Pnumber
        LEFT JOIN
        Dept_Location D ON E.Dno = D.Dnumber;
        '''
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
        
    def populate_fake_data(self):
        conn = self.get_db_connection()
        #all the passwords are 'password'
        sql= '''
        INSERT INTO Employee (username, password_hash, role, Fname, Minit, Lname, SSN, Address, Sex, Salary, Dno)
        VALUES
        ('admin1', 'scrypt:32768:8:1$QiBEDDOix2grtGrL$b310f2cdc064aebf4820f089fd358b4d1cafff57b1d95153f30c0d09acf86a66269a63050c2c5c1982c82594bb6db1479218d4287fdd00436dd4a8181c50a6e3', 1, 'John', 'A', 'Doe', '123456789', '123 Main St', 'M', 80000, 1), -- Super Admin
        ('mgr_jane', 'scrypt:32768:8:1$QiBEDDOix2grtGrL$b310f2cdc064aebf4820f089fd358b4d1cafff57b1d95153f30c0d09acf86a66269a63050c2c5c1982c82594bb6db1479218d4287fdd00436dd4a8181c50a6e3', 2, 'Jane', 'B', 'Smith', '987654321', '456 Maple St', 'F', 75000, 2), -- Department Admin
        ('pm_mike', 'scrypt:32768:8:1$QiBEDDOix2grtGrL$b310f2cdc064aebf4820f089fd358b4d1cafff57b1d95153f30c0d09acf86a66269a63050c2c5c1982c82594bb6db1479218d4287fdd00436dd4a8181c50a6e3', 3, 'Mike', 'C', 'Johnson', '111222333', '789 Elm St', 'M', 70000, 2), -- Normal User
        ('hr_susan', 'scrypt:32768:8:1$QiBEDDOix2grtGrL$b310f2cdc064aebf4820f089fd358b4d1cafff57b1d95153f30c0d09acf86a66269a63050c2c5c1982c82594bb6db1479218d4287fdd00436dd4a8181c50a6e3', 1, 'Susan', 'D', 'Lee', '444555666', '321 Oak St', 'F', 65000, 1), -- Super Admin
        ('emp_tim', 'scrypt:32768:8:1$QiBEDDOix2grtGrL$b310f2cdc064aebf4820f089fd358b4d1cafff57b1d95153f30c0d09acf86a66269a63050c2c5c1982c82594bb6db1479218d4287fdd00436dd4a8181c50a6e3', 2, 'Tim', 'E', 'Brown', '777888999', '654 Pine St', 'M', 60000, 2); -- Department Admin
        
        INSERT INTO Project (PName, Pnumber, PLocation, Dnum)
        VALUES
        ('ProductX', 1, 'Bellaire', 5),
        ('ProductY', 2, 'Sugarland', 5),
        ('ProductZ', 3, 'Houston', 5),
        ('Computerization', 10, 'Stafford', 4),
        ('Reorganization', 20, 'Houston', 1),
        ('Newbenefits', 30, 'Stafford', 4);
        
        
        INSERT INTO Works_On (Essn, Pno)
        VALUES
        ('123456789',1),
        ('987654321',2),
        ('111222333',3),
        ('444555666',10),
        ('777888999',20);
        
        INSERT INTO Dept_Location (Dnumber, Dlocation)
        VALUES
        (1, 'Guelph'),
        (2, 'Milton'),
        (3, 'Mississauga'),
        (4, 'Brampton'),
        (5, 'Toronto');
        '''
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
    
    def get_all_employee_data(self):
        sql = f' select * from Employee'
        conn = self.get_db_connection()
        cur = conn.cursor()
        cur.execute(sql)
        users = cur.fetchall()
        cur.close()
        conn.close()
        return users
    
    def get_all_project_data(self):
        sql = f' select * from project'
        conn = self.get_db_connection()
        cur = conn.cursor()
        cur.execute(sql)
        projects = cur.fetchall()
        cur.close()
        conn.close()
        return projects
    
    def get_all_employee_data_from_a_department(self, department_id):
        sql = f' select * from Employee where Dno = {department_id}'
        conn = self.get_db_connection()
        cur = conn.cursor()
        cur.execute(sql)
        users = cur.fetchall()
        cur.close()
        conn.close()
        return users
    
    def get_all_project_data_from_a_department(self, department_id):
        sql = f' select * from project where Dnum = {department_id}'
        conn = self.get_db_connection()
        cur = conn.cursor()
        cur.execute(sql)
        projects = cur.fetchall()
        cur.close()
        conn.close()
        return projects
        
    def export_db_as_csv(self):
        sql = "SELECT * FROM AllEmployeeData"
        conn = self.get_db_connection()
        cur = conn.cursor()
        cur.execute(sql)
        users = cur.fetchall()
        headers = [desc[0] for desc in cur.description]  
        filename = f"employee_data_{uuid.uuid4()}.csv"
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)  
            writer.writerows(users)   
        cur.close()
        conn.close()
        return filename
    
    def import_db_from_csv(self, csv_data):
        conn = self.get_db_connection()
        cur = conn.cursor()
        try:
            csv_file = StringIO(csv_data)
            reader = csv.DictReader(csv_file)
            for row in reader:
                sql_employee = """
                INSERT INTO Employee (username, password_hash, role, Dno, Fname, Minit, Lname, SSN, Address, Sex, Salary)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values_employee = (
                    row['username'], row['password_hash'], row['role'], row['dno'],
                    row['fname'], row['minit'], row['lname'], row['ssn'],
                    row['address'], row['sex'], row['salary']
                )
                cur.execute(sql_employee, values_employee)

                if row['pnumber']:
                    sql_works_on = "INSERT INTO Works_On (Essn, Pno) VALUES (%s, %s)"
                    values_works_on = (row['ssn'], row['pnumber'])
                    cur.execute(sql_works_on, values_works_on)

                if row['pname'] and row['pnumber'] and row['plocation'] and row['dnum']:
                    sql_project = """
                    INSERT INTO Project (Pname, Pnumber, Plocation, Dnum)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (Pnumber) DO NOTHING
                    """
                    values_project = (row['pname'], row['pnumber'], row['plocation'], row['dnum'])
                    cur.execute(sql_project, values_project)

                if row['dno'] and row['dlocation']:
                    sql_dept_location = """
                    INSERT INTO Dept_Location (Dnumber, Dlocation)
                    VALUES (%s, %s)
                    ON CONFLICT (Dnumber, Dlocation) DO NOTHING
                    """
                    values_dept_location = (row['dno'], row['dlocation'])
                    cur.execute(sql_dept_location, values_dept_location)
            conn.commit()
            print("Data imported successfully")
        except Exception as e:
            conn.rollback()
            print(f"Error importing data: {str(e)}")
        finally:
            cur.close()
            conn.close()
    
    def get_employee_view_data(self, id):
        sql = "SELECT * FROM AllEmployeeData where id = %s"
        conn = self.get_db_connection()
        cur = conn.cursor()
        cur.execute(sql, (id,))
        employee = cur.fetchone()
        cur.close()
        conn.close()
        return employee
    

