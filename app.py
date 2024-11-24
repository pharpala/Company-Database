from flask import Flask, flash, redirect, render_template, request, session, url_for
from database import DataBase 
from werkzeug.security import generate_password_hash, check_password_hash
from flask import send_file

app = Flask(__name__)
db = DataBase() 
app.secret_key = "secret_key"

def is_admin_or_department_admin(department) -> bool:
    if "user_info" in session and session["user_info"][3] == 1 or (session["user_info"][3] == 2 and session["user_info"][4] == department):
        return True
    else:
        return False
    
@app.route("/inset_from_csv", methods=["POST"])
def insert_from_csv():
    csv_data:str = request.form.get("csv")
    #check if admin 
    if "user_info" in session and session["user_info"][3] == 1:
        db.import_db_from_csv(csv_data)
        flash("Imported successfully", "success")
        return redirect(url_for("main_page"))
    else:
        flash("Unauthorized to delete this employee", "error")
        return render_template("error.html", error= "Unauthorized")

@app.route("/delete_employee", methods=["POST"])
def delete_employee():
    employee_id = request.form.get("id")
    department = request.form.get("department")
    ssn = request.form.get("ssn")
     
    if is_admin_or_department_admin(department):
        #delete row from employee table
        sql = "DELETE FROM Employee WHERE id = %s"
        values = (employee_id,)
        conn = db.get_db_connection()
        cur = conn.cursor()
        cur.execute(sql, values)
        #delete row from work_on table 
        sql = "DELETE FROM Works_On WHERE Essn = %s"
        values = (ssn,)
        cur.execute(sql, values)
        #commit the changes
        conn.commit()
        cur.close()
        conn.close()
        flash("Employee updated successfully", "success")
        return redirect(url_for("main_page"))
    else:
        flash("Unauthorized to delete this employee", "error")
        return render_template("error.html", error= "Unauthorized")
    
@app.route("/update_employee", methods=["POST"])
def update_employee():
    #get data we are changing from html page 
    employee_id = request.form.get("id")
    username = request.form.get("username")
    role = request.form.get("role")
    department = request.form.get("department")
    fname = request.form.get("fname")
    minit = request.form.get("minit")
    lname = request.form.get("lname")
    ssn = request.form.get("ssn")
    address = request.form.get("address")
    sex = request.form.get("sex")
    salary = request.form.get("salary")  
    project_name = request.form.get("project_name")
    project_number = request.form.get("project_number")
    project_location = request.form.get("project_location")
    department_location = request.form.get("department_location")
    
    print(f"project number is {project_number}")
    
    if is_admin_or_department_admin(department):  
        #update employee
        sql = """
        UPDATE Employee
        SET username = %s, role = %s, Dno = %s, Fname = %s, Minit = %s, 
            Lname = %s, SSN = %s, Address = %s, Sex = %s, Salary = %s
        WHERE id = %s
        """
        values = (username, role, department, fname, minit, lname, ssn, address, sex, salary, employee_id)
        conn = db.get_db_connection()
        cur = conn.cursor()
        cur.execute(sql, values)
        conn.commit()
        
        #update works_on
        if project_number:
            sql = """
            UPDATE Works_On
            SET Pno = %s
            WHERE Essn = %s
            """
            values = (project_number, ssn)
            cur.execute(sql, values)
            conn.commit()
        
        #update project 
        #if project_name and project_location and  department and project_number:
        #    print("Updating project number")
        #    sql = """
        #    UPDATE Project
        #    SET Pname = %s, Plocation = %s, Dnum = %s
        #    WHERE Pnumber = %s
        #    """
        #    values = (project_name, project_location, department, project_number)
        #    cur.execute(sql, values)
        #    conn.commit()
            
        #update department 
        if department_location and department:
            sql = """
            UPDATE Dept_Location
            SET Dlocation = %s
            WHERE Dnumber = %s
            """
            values = (department_location, department)
            cur.execute(sql, values)
            conn.commit()

        cur.close()
        conn.close()
        flash("Employee updated successfully", "success")
        return redirect(url_for("main_page"))  
    else:
        flash("Unauthorized to update this employee", "error")
        return render_template("error.html", error= "Unauthorized")
    
@app.route("/")
def main_page():
    #if users logged in 
    if "user_info" in session:
        #if user is super admin get all data
        if session['user_info'][3] == 1:
            employees = db.get_all_employee_data()  
        #if user is normal user or department admin get employee data from department 
        elif session['user_info'][3] == 2 or session['user_info'][3] == 3:
            employees = db.get_all_employee_data_from_a_department(session['user_info'][4])
        #error case 
        else:
            employees = None 
        #pass the session token to the webpage and employee data 
        return render_template("index.html", user_info=session['user_info'], employees=employees)
    else:
        return render_template("index.html", user_info=False)
    
@app.route("/register", methods=["POST"])
def register():
    #get the data from the register form 
    username = request.form["username"]
    password = request.form["password"]
    hashed_password = generate_password_hash(password)
    role = request.form["role"]
    department = request.form["department"]
    fname = request.form["fname"]
    minit = request.form["minit"]
    lname = request.form["lname"]
    ssn = request.form["ssn"]
    address = request.form["address"]
    sex = request.form["sex"]
    salary = request.form["salary"]
    pno = request.form["pno"]
    
    if role > 3 or role < 1:
        return render_template("error.html", error="Role must be between 1 and 3 inclusive")
    
    if sex != "M" and sex != "F":
        return render_template("error.html", error="Sex must be M or F")
    
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        #insert into the employee table
        sql = "INSERT INTO Employee (username, password_hash, role, Dno, Fname, Minit, Lname, SSN, Address, Sex, Salary) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (username, hashed_password, role, department, fname, minit, lname, ssn, address, sex, salary)
        cursor.execute(sql, values)
        conn.commit()
        
        #inset into work_on table 
        sql = "INSERT INTO Works_On (Essn, Pno) values (%s, %s)"
        values = (ssn, pno)
        cursor.execute(sql, values)
        conn.commit()
        
        flash("Registration successful", "success")
        return redirect(url_for('login'))
    except Exception as e:
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        #get data from login page
        username = request.form["username"]
        password = request.form["password"]
        #query the employee table
        sql = f' select * from Employee where username = \'{username}\''
        conn = db.get_db_connection()
        cur = conn.cursor()
        cur.execute(sql)
        user = cur.fetchone()
        #check if user row exists and the password hash matches
        if not user or not check_password_hash(user[2], password):
            flash("Invalid username or password", "error")
            return render_template("error.html", error="Invalid username or password")
        flash("Login successful", "success")
        #put the tuple into the session to read from later in html
        session["user_info"] = user
        cur.close()
        conn.close()
        return redirect(url_for("main_page"))
    return render_template("login.html")

@app.route("/export")
def export():
    #if user logged in and the user a super admin 
    if "user_info" in session and session['user_info'][3] == 1:
        #send the file over to download 
        db_export = db.export_db_as_csv()
        return send_file(db_export, as_attachment=True)
    else:
        flash("Unauthorized to export the database", "error")
        return render_template("error.html", error= "Unauthorized")

@app.route("/logout")
def logout():
    #remove the session token 
    session.pop("user_info", None)
    flash("Logout successful", "success")
    return redirect(url_for("main_page"))

@app.route("/employee/<int:id>" , methods=["GET", "POST"])
def employee(id):
    #check if id valid 
    sql = "select * from employee where id = %s"
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute(sql, (id,))
    employee = cur.fetchone()
    cur.close()
    conn.close()
    if employee is None:
        flash("Invalid employee ID", "error")
        return redirect(url_for("main_page"))
    
    employee_data = db.get_employee_view_data(id)
    return render_template("employee.html", employee=employee_data)

@app.route("/projects")
def projects():
    if session['user_info'][3] != 1:
        return render_template("error.html", error="Unauthorized to view projects")
    projects = db.get_all_project_data()
    return render_template("projects.html", projects=projects)

@app.route("/add_project", methods=["POST"])
def add_project():
    if session['user_info'][3] != 1:
        return render_template("error.html", error="Unauthorized to add project")
    
    project_number = request.form.get("Pnumber")
    project_name = request.form.get("Pname")
    project_location = request.form.get("Plocation")
    department_number = request.form.get("Dnum")
    
    sql = """
    INSERT INTO Project (Pname, Pnumber, Plocation, Dnum)
    VALUES (%s, %s, %s, %s)
    """
    values = (project_name, project_number, project_location, department_number)
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()
    cur.close()
    conn.close()
    flash("Project added successfully", "success")
    return redirect(url_for("projects"))

@app.route("/delete_project", methods=["POST"])
def delete_project():
    if session['user_info'][3] != 1:
        return render_template("error.html", error="Unauthorized to add project")
    project_number = request.form.get("Pnumber")

    conn = db.get_db_connection()
    sql = "SELECT * FROM Works_On WHERE Pno = %s"
    values = (project_number,)
    cur = conn.cursor()
    cur.execute(sql, values)
    works_on = cur.fetchall()
    if works_on:
        return render_template("error.html", error="Cannot delete project, employees are working on it")

    sql = "DELETE FROM Project WHERE Pnumber = %s"
    values = (project_number,)
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()
    cur.close()
    conn.close()
    flash("Project deleted successfully", "success")
    return redirect(url_for("projects"))

@app.route("/update_project", methods=["POST"])
def update_project():
    if session['user_info'][3] != 1:
        return render_template("error.html", error="Unauthorized to add project")
    project_number = request.form.get("Pnumber")
    project_name = request.form.get("Pname")
    project_location = request.form.get("Plocation")
    department_number = request.form.get("Dnum")
    sql = "UPDATE Project SET Pname = %s, Plocation = %s, Dnum = %s WHERE Pnumber = %s"
    values = (project_name, project_location, department_number, project_number)
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()
    cur.close()
    conn.close()
    flash("Project updated successfully", "success")
    return redirect(url_for("projects"))

@app.errorhandler(Exception)
def handle_error(e):
    return render_template("error.html", error=str(e))

if __name__ == "__main__":
    app.run(debug=True)
