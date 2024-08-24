import os
import uuid
import streamlit as st
import sqlite3
import datetime

def initialize_database():
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT,
                age INTEGER,
                department TEXT,
                joining_date DATE,
                username TEXT,
                password TEXT,
                salary REAL,
                qualification TEXT,
                profile_photo_path TEXT
            )''')
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    description TEXT,
                    assigned_employee_id INTEGER,
                    due_date DATE,
                    status TEXT,
                    acknowledged INTEGER DEFAULT 0
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS Task_history (
                    id INTEGER PRIMARY KEY,
                    description TEXT,
                    assigned_employee_id INTEGER,
                    due_date DATE,
                    status TEXT
                )''')
    conn.commit()
    return conn, c

#basic employee operation  
def add_employee(conn, c, id, name, age, department, salary):
    joining_date = datetime.date.today()
    username = f"{name.lower().split()[0]}_{id}"
    password = f"{name.lower().split()[0]}@123"
    c.execute('''INSERT INTO employees (id, name, age, department, joining_date, username, password, salary) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (id, name, age, department, joining_date, username, password, salary))
    conn.commit()
    return username, password

def get_all_employees(conn, c):
    c.execute('''SELECT * FROM employees''')
    return c.fetchall()

def delete_employee(conn, c, username):
    c.execute('''DELETE FROM employees WHERE username = ?''', (username,))
    conn.commit()
    return c.rowcount > 0

def clear_all_employees(conn, c):
    c.execute('''DELETE FROM employees''')
    conn.commit()
    st.warning("All employees deleted successfully!")


#modify employee details
def edit_employee_details(conn, c, employee_id, attribute, new_value):
    if attribute == "Name":
        # Update the name
        c.execute('''UPDATE employees SET name=? WHERE id=?''', (new_value, employee_id))

        # Generate new username based on the new name
        new_username = f"{new_value.lower().split()[0]}_{employee_id}"

        # Update the username
        c.execute('''UPDATE employees SET username=? WHERE id=?''', (new_username, employee_id))

        # Generate new password based on the new name
        new_password = f"{new_value.lower().split()[0]}@123"

        # Update the password
        c.execute('''UPDATE employees SET password=? WHERE id=?''', (new_password, employee_id))
    elif attribute == "Age":
        new_value = int(new_value)
        c.execute('''UPDATE employees SET age=? WHERE id=?''', (new_value, employee_id))
    elif attribute == "Department":
        c.execute('''UPDATE employees SET department=? WHERE id=?''', (new_value, employee_id))
    elif attribute == "Salary":
        new_value = float(new_value)
        c.execute('''UPDATE employees SET salary=? WHERE id=?''', (new_value, employee_id))
    elif attribute == "Qualification":  # Add condition for updating qualification
        c.execute('''UPDATE employees SET qualification=? WHERE id=?''', (new_value, employee_id))
    elif attribute == "Profile Photo":  # Add condition for updating profile photo path
        c.execute('''UPDATE employees SET profile_photo_path=? WHERE id=?''', (new_value, employee_id))
    conn.commit()


#get employee ids & usernames , deatils interconnection
def get_all_employee_ids(conn, c):
    c.execute('''SELECT id FROM employees''')
    return [row[0] for row in c.fetchall()]

def get_all_employee_usernames(conn, c):
    c.execute('''SELECT username FROM employees''')
    return [row[0] for row in c.fetchall()]

def get_employee_details(conn, c, username):
    c.execute('''SELECT *, profile_photo_path FROM employees WHERE username = ?''', (username,))
    return c.fetchone()

def get_employee_id_by_username(conn, c, username):
    """Retrieve the employee ID based on the username."""
    c.execute("SELECT id FROM employees WHERE username = ?", (username,))
    result = c.fetchone()
    if result:
        return result[0]
    else:
        return None



#profile photo
def save_profile_photo(profile_photo):
    # Generate a unique filename for the profile photo
    filename = str(uuid.uuid4()) + ".jpg"  # Assuming the photo format is JPG
    # Define the directory path to save the profile photos
    profile_photo_dir = "profile_photos"
    # Create the directory if it doesn't exist
    if not os.path.exists(profile_photo_dir):
        os.makedirs(profile_photo_dir)
    # Save the profile photo to the directory with the unique filename
    profile_photo_path = os.path.join(profile_photo_dir, filename)
    with open(profile_photo_path, "wb") as f:
        f.write(profile_photo.getvalue())
    # Return the profile photo path
    return profile_photo_path





#task functions

def create_task(conn, c, description, assigned_employee_id, due_date):
    c.execute('''INSERT INTO tasks (description, assigned_employee_id, due_date, status) VALUES (?, ?, ?, ?)''', (description, assigned_employee_id, due_date, 'Pending'))
    conn.commit()

def assign_task(conn, c, task_id, assigned_employee_id):
    c.execute('''UPDATE tasks SET assigned_employee_id = ? WHERE id = ?''', (assigned_employee_id, task_id))
    conn.commit()

def update_task_status(conn, c, task_id, status):
    c.execute('''UPDATE tasks SET status = ? WHERE id = ?''', (status, task_id))
    conn.commit()

def get_tasks_by_employee(conn, c, employee_id):
    c.execute('''SELECT * FROM tasks WHERE assigned_employee_id = ?''', (employee_id,))
    return c.fetchall()

def get_all_tasks(conn, c):
    c.execute('''SELECT * FROM tasks''')
    return c.fetchall()

def delete_task(conn, c, task_id):
    # Fetch the task details before deletion
    c.execute('''SELECT * FROM tasks WHERE id = ?''', (task_id,))
    task_details = c.fetchone()

    if task_details:
        # Extract relevant information from task_details
        task_info = (task_details[1], task_details[2], task_details[3], task_details[4])
        # Move the task to Task_history table
        c.execute('''INSERT INTO Task_history (description, assigned_employee_id, due_date, status) VALUES (?, ?, ?, ?)''', task_info)

        # Delete the task from the tasks table
        c.execute('''DELETE FROM tasks WHERE id = ?''', (task_id,))
        conn.commit()

        # Increase the employee's salary by 2%
        assigned_employee_id = task_details[2]
        c.execute('''UPDATE employees SET salary = salary * 1.02 WHERE id = ?''', (assigned_employee_id,))
        conn.commit()

        return c.rowcount > 0
    else:
        return False

def view_task_history(conn, c):
    c.execute('''SELECT * FROM Task_history''')
    task_history = c.fetchall()
    return task_history


    