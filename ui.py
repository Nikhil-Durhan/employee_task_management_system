import streamlit as st
import pandas as pd
from database import create_task , update_task_status , get_all_employees

def display_employee_details(employees):
    st.subheader("Employee Details")
    if employees:
        column_names = ["ID", "Name", "Age", "Department", "Joining Date", "Username","Password", "Salary", "Qualification", "Profile Photo"]
        df = pd.DataFrame(employees, columns=column_names)
        st.table(df)
    else:
        st.error("No employees found in the database.")

def display_success(message):
    st.success(message)

def display_error(message):
    st.error(message)

def display_warning(message):
    st.warning(message)

def display_text_input(label, password=False):
    if password:
        return st.text_input(label, type="password")
    else:
        return st.text_input(label)

def display_number_input(label, min_value=None, max_value=None, step=None):
    return st.number_input(label, min_value=min_value, max_value=max_value, step=step)

def display_selectbox(label, options, location='default'):
    if location == 'sidebar':
        return st.sidebar.selectbox(label, options)
    else:
        return st.selectbox(label, options)


def display_button(label):
    return st.button(label)


#task display

def display_task_form(conn, c):
    st.subheader("Create Task")
    employees = get_all_employees(conn, c)  # Fetch all employees from the database
    employee_ids = [employee[0] for employee in employees]  # Extract employee IDs
    employee_names = [employee[1] for employee in employees]  # Extract employee names

    with st.form(key='task_form'):
        description = st.text_input("Description")
        assigned_employee_id = st.selectbox("Assign To", employee_ids, format_func=lambda x: employee_names[employee_ids.index(x)])  # Populate dropdown with employee names
        due_date = st.date_input("Due Date")
        submitted = st.form_submit_button("Create Task")
    if submitted:
        create_task(conn, c, description, assigned_employee_id, due_date)
        st.success("Task created successfully!")


def display_task_list(conn, c, tasks):
    st.subheader("Task List")
    if tasks:
        for task in tasks:
            st.write(f"**Task ID:** {task[0]}")
            st.write(f"**Description:** {task[1]}")
            st.write(f"**Assigned Employee ID:** {task[2]}")
            st.write(f"**Due Date:** {task[3]}")
            st.write(f"**Status:** {task[4]}")

            # Generate a unique key for the selectbox based on the task ID
            selectbox_key = f"update_status_{task[0]}"

            # Add task status update option with unique key
            new_status = st.selectbox("Update Status", ["Pending", "In Progress", "Completed"], key=selectbox_key)
            
            # Generate a unique key for the button based on the task ID
            button_key = f"update_button_{task[0]}"

            # Add update button with unique key
            if st.button("Update", key=button_key):
                update_task_status(conn, c, task[0], new_status)
                st.success("Task status updated successfully!")

            st.write("---")
    else:
        st.info("No tasks found.")



def display_task_details(task):
    st.subheader("Task Details")
    if task:
        st.write(f"**Task ID:** {task[0]}")
        st.write(f"**Description:** {task[1]}")
        st.write(f"**Assigned Employee ID:** {task[2]}")
        st.write(f"**Due Date:** {task[3]}")
        st.write(f"**Status:** {task[4]}")
    else:
        st.info("Task not found.")
