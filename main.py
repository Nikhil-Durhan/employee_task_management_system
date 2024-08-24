# import
import streamlit as st
import database as dbs
from auth import admin_login, employee_login
import ui 

#main function
def main():
    conn, c = dbs.initialize_database()

#streamlit configuration
    st.set_page_config(
        page_title="Employee Management System",
        page_icon=":bust_in_silhouette:",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    #session state initalization
    st.title("Employee Management System")

    session_state = st.session_state
    if 'logged_in' not in session_state:
        session_state.logged_in = False
        session_state.user_type = None
        session_state.username = None

    #login form
    if not session_state.logged_in:
        with st.sidebar.form(key='login_form'):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
        if submitted:
            if admin_login(username, password):
                session_state.logged_in = True
                session_state.user_type = 'admin'
                st.success("Admin Login successful!")
            elif employee_login(username, password, conn, c):
                session_state.logged_in = True
                session_state.user_type = 'employee'
                session_state.username = username
                st.success("Employee Login successful!")
            else:
                st.error("Invalid username or password!")

    #admin actions 
    if session_state.logged_in:
        if session_state.user_type == 'admin':
            st.sidebar.title("Admin Menu")
            menu = ["Add Employee", "View Employees", "Edit Employee", "Delete Employee", "Clear All Employees", "Task Management", "Logout"]
            choice = st.sidebar.selectbox("Select Action", menu)
     
    # employee operations 
            if choice == "Add Employee":
                st.sidebar.subheader("Add Employee")
                with st.sidebar.form(key='add_employee_form'):
                    id = st.text_input("Employee ID")
                    name = st.text_input("Name")
                    age = st.number_input("Age", min_value=18, max_value=100, step=1)
                    department = st.text_input("Department")
                    salary = st.number_input("Salary", min_value=0.0, step=1000.0)
                    submitted = st.form_submit_button("Add")
                if submitted:
                    username, password = dbs.add_employee(conn, c, id, name, age, department, salary)
                    st.success(f"Employee added successfully! Username and password set: {username}")

            elif choice == "View Employees":
                st.sidebar.subheader("View Employees")
                employees = dbs.get_all_employees(conn, c)
                ui.display_employee_details(employees)


            elif choice == "Edit Employee":
                st.sidebar.subheader("Edit Employee")
                with st.sidebar.form(key='edit_employee_form'):
                    employee_id = st.text_input("Employee ID")
                    attributes = ["Name", "Age", "Department", "Salary"]
                    attribute = st.selectbox("Select Attribute to Edit", attributes)
                    new_value = st.text_input("Enter New Data")
                    submitted = st.form_submit_button("Edit")
                if submitted:
                    dbs.edit_employee_details(conn, c, employee_id, attribute, new_value)
                    st.success("Employee details updated successfully!")

            elif choice == "Delete Employee":
                st.sidebar.subheader("Delete Employee")
                employees = dbs.get_all_employee_usernames(conn, c)  # Fetch existing employee usernames
                if employees:
                    with st.sidebar.form(key='delete_employee_form'):
                        username_to_delete = st.selectbox("Select Employee Username to Delete", employees)
                        submitted = st.form_submit_button("Delete")
                        if submitted:
                            if dbs.delete_employee(conn, c, username_to_delete):
                                st.success(f"Employee with username '{username_to_delete}' deleted successfully!")
                            else:
                                st.error(f"No employee found with username '{username_to_delete}'")
                else:
                    st.error("No employees found in the database.")



            elif choice == "Clear All Employees":
                st.sidebar.subheader("Clear EmpSss ?")
                task_action = st.sidebar.selectbox("Select Action", ["No", "Yes","Delete selected Employee"])
                if task_action == "NO":
                    choice == "View Employees"
                elif task_action== "Yes":
                    ch = st.selectbox("Are You Sure ?",["No","Yes"])
                    if ch == "Yes": 
                        dbs.clear_all_employees(conn,c)
                    elif ch == "No":
                        choice == "View Employees" 
                elif task_action == "Delete Selected Employee":
                    choice = "Delete Employee"

        #task management
            elif choice == 'Task Management': 
                st.sidebar.subheader("Task Management")
                task_action = st.sidebar.selectbox("Select Action", ["Create Task", "View Existing Tasks","Assign Task","View Task History"])
                if task_action == "Create Task":
                    ui.display_task_form(conn,c)
                elif task_action== "View Existing Tasks":
                    tasks = dbs.get_all_tasks(conn, c)  # Retrieve all tasks from the database
                    if tasks:
                        st.write("## Existing Tasks")
                        for task in tasks:
                            st.write(f"**Task ID:** {task[0]}")
                            st.write(f"**Description:** {task[1]}")
                            st.write(f"**Assigned Employee ID:** {task[2]}")
                            st.write(f"**Due Date:** {task[3]}")
                            st.write(f"**Status:** {task[4]}")
                            st.write("---")
                            if task[4] == 'Completed':
                                if st.button("Delete Task"):
                                    if dbs.delete_task(conn, c, task[0]):
                                        st.success("Task deleted successfully!")
                                    else:
                                        st.error("Error deleting task.")
                    else:
                        st.info("No tasks found.")

                elif task_action == "Assign Task":
                    st.sidebar.subheader("Assign Task")
                    tasks = dbs.get_all_tasks(conn, c)  # Retrieve all tasks
                    if tasks:
                        task_ids = [task[0] for task in tasks]
                        task_id_to_assign = st.sidebar.selectbox("Select Task ID", task_ids)
        
                        # Fetch existing employee IDs from the database
                        employee_ids = dbs.get_all_employee_ids(conn, c)
                        if employee_ids:
                            assigned_employee_id = st.sidebar.selectbox("Assign To", employee_ids)
                            if st.sidebar.button("Assign"):
                                dbs.assign_task(conn, c, task_id_to_assign, assigned_employee_id)
                                st.sidebar.success("Task assigned successfully!")
                        else:
                            st.sidebar.error("No employees found.")
                    else:
                        st.sidebar.info("No tasks found.")

                elif task_action == "View Task History":
                    st.sidebar.subheader("View Task History")
                    task_history = dbs.view_task_history(conn, c)
                    if task_history:
                        st.write("## Task History")
                        for task in task_history:
                            st.write(f"**Task ID:** {task[0]}")
                            st.write(f"**Description:** {task[1]}")
                            st.write(f"**Assigned Employee ID:** {task[2]}")
                            st.write(f"**Due Date:** {task[3]}")
                            st.write(f"**Status:** {task[4]}")
                            st.write("---")
                    else:
                        st.info("No task history found.")

                    
            elif choice == "Logout":
                session_state.logged_in = False
                session_state.user_type = None
                session_state.username = None
                st.success("Logged out successfully!")

#employee activity
        elif session_state.user_type == 'employee':
            # Fetch the employee ID based on the username
            employee_id = dbs.get_employee_id_by_username(conn, c, session_state.username)
            session_state.employee_id = employee_id  # Initialize employee_id attribute
            st.sidebar.title("Employee Menu")
            menu = ["View My Details", "My Tasks", "Profile Management","Logout"]
            choice = st.sidebar.selectbox("Select Action", menu)

            if choice == "View My Details":
                st.subheader("My Details")
                employee_details = dbs.get_employee_details(conn, c, session_state.username)
                if employee_details:
                    st.write("Name:", employee_details[1])
                    st.write("Age:", employee_details[2])
                    st.write("Department:", employee_details[3])
                    st.write("Joining Date:", employee_details[4])
                    st.write("Username:", employee_details[5])
                    st.write("Salary:", employee_details[7])
                    st.write("Qualification:", employee_details[8])  # Display qualification
                    st.write("Profile Photo:")
                    st.write("----------")
                    if employee_details[9]:  # Check if profile photo path exists
                        st.image(employee_details[9], caption='Profile Photo', use_column_width=True, output_format='JPEG')
                        st.write(
                                f'<style>img {{max-width: 300px;}}</style>',
                        unsafe_allow_html=True
                                )
                    else:
                        st.write("No profile photo available")
                else:
                    st.error("Employee details not found.")

            elif choice == "My Tasks":
                st.sidebar.subheader("My Tasks")
                employee_tasks = dbs.get_tasks_by_employee(conn,c,session_state.employee_id)  # Retrieve tasks assigned to the logged-in employee
                ui.display_task_list(conn,c,employee_tasks)

            elif choice == "Profile Management":
                st.sidebar.subheader("Profile Management")
                employee_details = dbs.get_employee_details(conn, c, session_state.username)
                if employee_details:
                    st.subheader("Update Profile")
                    with st.form(key='update_profile_form'):
                        # Add input fields for profile photo and qualification
                        new_qualification = st.text_area("New Qualification", value=employee_details[8])
                        new_profile_photo = st.file_uploader("Upload New Profile Photo", type=['jpg', 'jpeg', 'png'])

                        submitted = st.form_submit_button("Update Profile")
                        if submitted:
                            # Update the qualification in the database
                            dbs.edit_employee_details(conn, c, employee_details[0], "Qualification", new_qualification)
                            # Handle profile photo upload
                            if new_profile_photo is not None:
                                # Save the uploaded profile photo
                                profile_photo_path = dbs.save_profile_photo(new_profile_photo)
                                # Update the profile photo path in the database
                                dbs.edit_employee_details(conn, c, employee_details[0], "Profile Photo", profile_photo_path)
                                # Fetch the updated employee details again
                                employee_details = dbs.get_employee_details(conn, c, session_state.username)
                                st.success("Profile updated successfully!")
                else:
                    st.error("Employee details not found.")


        #log out
            elif choice == "Logout":
                session_state.logged_in = False
                session_state.user_type = None
                session_state.username = None
                st.success("Logged out successfully!")

#main entry point
if __name__ == "__main__":
    main()
