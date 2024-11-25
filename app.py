from flask import Flask, flash, redirect, render_template, request, session, url_for
from database import DataBase 
from werkzeug.security import generate_password_hash, check_password_hash
from flask import send_file



app = Flask(__name__)
db = DataBase() 
app.secret_key = "secret_key"


# --------------- function to check the if admin or not  ----------------------


def is_admin_or_department_admin(department) -> bool:
    if "user_info" in session and session["user_info"][3] == 1 or (session["user_info"][3] == 2 and session["user_info"][4] == department):
        return True
    else:
        return False


# --------------- function to import from csv  --------------------------------
    

@app.route("/insert_from_csv", methods=["POST"])
def insert_from_csv():
    try:
        csv_data: str = request.form.get("csv")
        # Check if the user is an admin
        if "user_info" in session and session["user_info"][3] == 1:
            if not csv_data:
                flash("No CSV data provided", "error")
                return redirect(url_for("main_page"))

            db.import_db_from_csv(csv_data)
            flash("Data imported successfully", "success")
            return redirect(url_for("main_page"))
        else:
            flash("Unauthorized to perform this action", "error")
            return render_template("error.html", error="Unauthorized")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return render_template("error.html", error="An unexpected error occurred")

# ---------------------- Export database route ------------------------------


@app.route("/export")
def export():
    try:
        # Ensure user is logged in and is a super admin
        if "user_info" in session and session['user_info'][3] == 1:
            # Send the file for download
            db_export = db.export_db_as_csv()
            return send_file(db_export, as_attachment=True)

        # Unauthorized access
        flash("Unauthorized to export the database", "error")
        return render_template("error.html", error="Unauthorized to export the database")

    except FileNotFoundError:
        flash("Error: Exported file not found", "error")
        return render_template("error.html", error="Exported file not found")

    except Exception as e:
        flash(f"An error occurred during export: {str(e)}", "error")
        return render_template("error.html", error="An error occurred during database export")



# -------------------- All employee edit routes  ---------------------------------
@app.route("/delete_employee", methods=["POST"])
def delete_employee():
    employee_id = request.form.get("id")
    department = request.form.get("department")
    ssn = request.form.get("ssn")

    try:
        if is_admin_or_department_admin(department):
            conn = db.get_db_connection()
            cur = conn.cursor()

            # Delete from Employee table
            sql = "DELETE FROM Employee WHERE id = %s"
            cur.execute(sql, (employee_id,))

            # Delete from Works_On table
            sql = "DELETE FROM Works_On WHERE Essn = %s"
            cur.execute(sql, (ssn,))

            conn.commit()
            flash("Employee deleted successfully", "success")
        else:
            flash("Unauthorized to delete this employee", "error")
            return render_template("error.html", error="Unauthorized")

    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Error occurred while deleting employee: {str(e)}", "error")
        return render_template("error.html", error="An error occurred")

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    return redirect(url_for("main_page"))


@app.route("/update_employee", methods=["POST"])
def update_employee():
    try:
        # Gather input data
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
        project_number = request.form.get("project_number")
        department_location = request.form.get("department_location")

        if is_admin_or_department_admin(department):
            conn = db.get_db_connection()
            cur = conn.cursor()

            # Update Employee table
            sql = """
            UPDATE Employee
            SET username = %s, role = %s, Dno = %s, Fname = %s, Minit = %s, 
                Lname = %s, SSN = %s, Address = %s, Sex = %s, Salary = %s
            WHERE id = %s
            """
            cur.execute(sql, (username, role, department, fname, minit, lname, ssn, address, sex, salary, employee_id))
            conn.commit()

            # Update Works_On table
            if project_number:
                sql = "UPDATE Works_On SET Pno = %s WHERE Essn = %s"
                cur.execute(sql, (project_number, ssn))
                conn.commit()

            # Update Dept_Location table
            if department_location and department:
                sql = "UPDATE Dept_Location SET Dlocation = %s WHERE Dnumber = %s"
                cur.execute(sql, (department_location, department))
                conn.commit()

            flash("Employee updated successfully", "success")
        else:
            flash("Unauthorized to update this employee", "error")
            return render_template("error.html", error="Unauthorized")

    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Error occurred while updating employee: {str(e)}", "error")
        return render_template("error.html", error="An error occurred")

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    return redirect(url_for("main_page"))


@app.route("/register", methods=["POST"])
def register():
    try:
        # Gather input data
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)
        role = int(request.form["role"])
        department = request.form["department"]
        fname = request.form["fname"]
        minit = request.form["minit"]
        lname = request.form["lname"]
        ssn = request.form["ssn"]
        address = request.form["address"]
        sex = request.form["sex"]
        salary = request.form["salary"]
        pno = request.form["pno"]

        if role < 1 or role > 3:
            return render_template("error.html", error="Role must be between 1 and 3 inclusive")
        if sex not in ["M", "F"]:
            return render_template("error.html", error="Sex must be M or F")

        conn = db.get_db_connection()
        cursor = conn.cursor()

        # Insert into Employee table
        sql = """
        INSERT INTO Employee (username, password_hash, role, Dno, Fname, Minit, Lname, SSN, Address, Sex, Salary)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (username, hashed_password, role, department, fname, minit, lname, ssn, address, sex, salary))
        conn.commit()

        # Insert into Works_On table
        sql = "INSERT INTO Works_On (Essn, Pno) VALUES (%s, %s)"
        cursor.execute(sql, (ssn, pno))
        conn.commit()

        flash("Registration successful", "success")
        return redirect(url_for("login"))

    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Error occurred during registration: {str(e)}", "error")
        return render_template("error.html", error="An error occurred")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/employee/<int:id>", methods=["GET", "POST"])
def employee(id):
    try:
        # Validate employee ID
        conn = db.get_db_connection()
        cur = conn.cursor()
        sql = "SELECT * FROM Employee WHERE id = %s"
        cur.execute(sql, (id,))
        employee = cur.fetchone()
        cur.close()
        conn.close()

        if employee is None:
            flash("Invalid employee ID", "error")
            return redirect(url_for("main_page"))

        # Fetch employee data for the view
        employee_data = db.get_employee_view_data(id)
        return render_template("employee.html", employee=employee_data)

    except Exception as e:
        flash(f"Error occurred while fetching employee data: {str(e)}", "error")
        return render_template("error.html", error="An error occurred")


# ---------------------- Main page route ------------------------------
    

@app.route("/")
def main_page():
    try:
        # Check if the user is logged in
        if "user_info" in session:
            user_role = session['user_info'][3]
            department = session['user_info'][4] if len(session['user_info']) > 4 else None

            # Fetch data based on user role
            if user_role == 1:  # Super Admin
                employees = db.get_all_employee_data()
            elif user_role in [2, 3]:  # Department Admin or Normal User
                if department:
                    employees = db.get_all_employee_data_from_a_department(department)
                else:
                    employees = None
                    flash("Error: Missing department information for user.", "error")
            else:  # Unexpected user role
                employees = None
                flash("Error: Invalid user role.", "error")

            # Pass the session token and employee data to the webpage
            return render_template("index.html", user_info=session['user_info'], employees=employees)
        else:
            # User not logged in
            return render_template("index.html", user_info=False)

    except Exception as e:
        # Handle unexpected errors
        flash(f"An error occurred while loading the main page: {str(e)}", "error")
        return render_template("error.html", error="An error occurred while loading the main page")


# ---------------------- Login/Signup route ------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    try:
        if request.method == "POST":
            # Get data from login page
            username = request.form["username"]
            password = request.form["password"]

            # Query the employee table
            sql = "SELECT * FROM Employee WHERE username = %s"
            conn = db.get_db_connection()
            cur = conn.cursor()
            cur.execute(sql, (username,))
            user = cur.fetchone()

            # Check if user exists and the password hash matches
            if not user or not check_password_hash(user[2], password):
                flash("Invalid username or password", "error")
                return render_template("error.html", error="Invalid username or password")

            # Login success
            session["user_info"] = user
            flash("Login successful", "success")
            cur.close()
            conn.close()
            return redirect(url_for("main_page"))

        return render_template("login.html")

    except Exception as e:
        flash(f"An error occurred during login: {str(e)}", "error")
        return render_template("error.html", error="An error occurred during login")

@app.route("/logout")
def logout():
    try:
        # Remove the session token
        session.pop("user_info", None)
        flash("Logout successful", "success")
        return redirect(url_for("main_page"))

    except Exception as e:
        flash(f"An error occurred during logout: {str(e)}", "error")
        return render_template("error.html", error="An error occurred during logout")


# -------------------- All project edit routes  ---------------------------------


@app.route("/projects")
def projects():
    try:
        if session['user_info'][3] != 1:
            return render_template("error.html", error="Unauthorized to view projects")
        
        projects = db.get_all_project_data()
        return render_template("projects.html", projects=projects)

    except Exception as e:
        flash(f"An error occurred while retrieving projects: {str(e)}", "error")
        return render_template("error.html", error="An error occurred while retrieving projects")

@app.route("/add_project", methods=["POST"])
def add_project():
    try:
        if session['user_info'][3] != 1:
            return render_template("error.html", error="Unauthorized to add project")
        
        project_number = request.form.get("Pnumber")
        project_name = request.form.get("Pname")
        project_location = request.form.get("Plocation")
        department_number = request.form.get("Dnum")
        
        # SQL query to insert project
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

    except Exception as e:
        flash(f"An error occurred while adding the project: {str(e)}", "error")
        return render_template("error.html", error="An error occurred while adding the project")

@app.route("/delete_project", methods=["POST"])
def delete_project():
    try:
        if session['user_info'][3] != 1:
            return render_template("error.html", error="Unauthorized to delete project")
        
        project_number = request.form.get("Pnumber")

        # Check if any employees are working on the project
        conn = db.get_db_connection()
        sql = "SELECT * FROM Works_On WHERE Pno = %s"
        values = (project_number,)
        cur = conn.cursor()
        cur.execute(sql, values)
        works_on = cur.fetchall()
        if works_on:
            flash("Cannot delete project, employees are working on it", "error")
            return render_template("error.html", error="Cannot delete project, employees are working on it")
        
        # Delete project from Project table
        sql = "DELETE FROM Project WHERE Pnumber = %s"
        cur.execute(sql, values)
        conn.commit()
        cur.close()
        conn.close()
        
        flash("Project deleted successfully", "success")
        return redirect(url_for("projects"))

    except Exception as e:
        flash(f"An error occurred while deleting the project: {str(e)}", "error")
        return render_template("error.html", error="An error occurred while deleting the project")

@app.route("/update_project", methods=["POST"])
def update_project():
    try:
        if session['user_info'][3] != 1:
            return render_template("error.html", error="Unauthorized to update project")
        
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

    except Exception as e:
        flash(f"An error occurred while updating the project: {str(e)}", "error")
        return render_template("error.html", error="An error occurred while updating the project")


# -------------------- All department edit routes  ---------------------------------


@app.route("/departments")
def departments():
    try:
        if session['user_info'][3] != 1:
            return render_template("error.html", error="Unauthorized to view departments")
        
        departments = db.get_all_department_data()
        return render_template("departments.html", departments=departments)

    except Exception as e:
        flash(f"An error occurred while retrieving departments: {str(e)}", "error")
        return render_template("error.html", error="An error occurred while retrieving departments")


@app.route("/add_department", methods=["POST"])
def add_department():
    try:
        if session['user_info'][3] != 1:
            return render_template("error.html", error="Unauthorized to add department")
        
        department_number = request.form.get("Dnumber")
        department_name = request.form.get("Dname")
        
        # SQL query to insert department
        sql = """
        INSERT INTO department (Dname, Dnumber)
        VALUES (%s, %s)
        """
        values = (department_name, department_number)
        conn = db.get_db_connection()
        cur = conn.cursor()
        cur.execute(sql, values)
        conn.commit()
        cur.close()
        conn.close()
        
        flash("Department added successfully", "success")
        return redirect(url_for("departments"))

    except Exception as e:
        flash(f"An error occurred while adding the department: {str(e)}", "error")
        return render_template("error.html", error="An error occurred while adding the department")


@app.route("/update_department", methods=["POST"])
def update_department():
    try:
        if session['user_info'][3] != 1:
            return render_template("error.html", error="Unauthorized to update department")
        
        department_number = request.form.get("Dnumber")
        department_name = request.form.get("Dname")
        
        # SQL query to update department
        sql = "UPDATE Department SET Dname = %s WHERE Dnumber = %s"
        values = (department_name, department_number)
        conn = db.get_db_connection()
        cur = conn.cursor()
        cur.execute(sql, values)
        conn.commit()
        cur.close()
        conn.close()
        
        flash("Department updated successfully", "success")
        return redirect(url_for("departments"))

    except Exception as e:
        flash(f"An error occurred while updating the department: {str(e)}", "error")
        return render_template("error.html", error="An error occurred while updating the department")


@app.route("/delete_department", methods=["POST"])
def delete_department():
    try:
        if session['user_info'][3] != 1:
            return render_template("error.html", error="Unauthorized to delete department")
        
        department_number = request.form.get("Dnumber")

        # Check if there are employees in the department
        conn = db.get_db_connection()
        sql = "SELECT * FROM employee WHERE Dno = %s"
        values = (department_number,)
        cur = conn.cursor()
        cur.execute(sql, values)
        employees = cur.fetchall()
        if employees:
            flash("Cannot delete department, employees are working in it", "error")
            return render_template("error.html", error="Cannot delete department, employees are working on it")
        
        # SQL query to delete department
        sql = "DELETE FROM department WHERE Dnumber = %s"
        cur.execute(sql, values)
        conn.commit()
        cur.close()
        conn.close()
        
        flash("Department deleted successfully", "success")
        return redirect(url_for("departments"))

    except Exception as e:
        flash(f"An error occurred while deleting the department: {str(e)}", "error")
        return render_template("error.html", error="An error occurred while deleting the department")



# -------------------- Error handling function  ---------------------------------


@app.errorhandler(Exception)
def handle_error(e):
    return render_template("error.html", error=str(e))


# -------------------- Main  ---------------------------------


if __name__ == "__main__":
    app.run(debug=True)
