def admin_login(username, password):
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "admin123"
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

def employee_login(username, password, conn, c):
    c.execute('''SELECT * FROM employees WHERE username = ? AND password = ?''', (username, password))
    return c.fetchone() is not None
