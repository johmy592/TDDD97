import sqlite3

connection = sqlite3.connect('database.db')
c = connection.cursor()

"""
This is where all the code handeling the database should be.
"""


def add_user_to_db(email, password, firstname, familyname, gender, city, country):
    c.execute("""INSERT INTO users(email, password, firstname, familyname, gender, city, country) VALUES 
            (?, ?, ?, ?, ?, ?, ?)""", (email, password, firstname, familyname, gender, city, country))
    connection.commit()


def sign_in_user(email, token):
    c.execute("SELECT * FROM loggedInUsers WHERE email = ?", (email,))
    if c.fetchall():
        c.execute("UPDATE loggedInUsers SET token = ? WHERE email = ?", (token, email))
    else:
        c.execute("INSERT INTO loggedInUsers(email, token) VALUES (?, ?)", (email, token))
    connection.commit()


def sign_out_user(token):
    c.execute('DELETE FROM loggedInUsers WHERE token = ?', (token,))
    connection.commit()


def token_to_email(token):
    c.execute('SELECT email FROM loggedInUsers WHERE token = ?', (token,))
    result = c.fetchall()
    if result:
        email = result[0][0]
        return email
    return ""


def get_messages_from_db(email):
    c.execute('SELECT sender, message FROM messages WHERE reciever=?', (email,))
    result = c.fetchall()
    i = 0
    data = []
    while i < len(result):
        writer = result[i][0]
        content = result[i][1]
        message_dict = {"writer": writer, "content": content}
        data.append(message_dict)
        i = i + 1
    return data


def user_exists(email):
    user_data_list = get_user_data_from_db(email)
    if user_data_list:
        return True
    return False


def get_user_data_from_db(email):
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    user_data_list = c.fetchall()
    return user_data_list


def add_message_to_db(receiver, sender, message):
    c.execute('INSERT INTO messages(reciever, sender, message) VALUES (?, ?, ?)', (receiver, sender, message))
    connection.commit()


def user_exists(email):
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    user_data_list = c.fetchall()
    if user_data_list:
        return True
    return False


def update_password(email, new_password):
    c.execute('UPDATE users SET password = ? WHERE email = ?', (new_password, email))
    connection.commit()


def user_and_password_match(email, password):
    c.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
    if c.fetchall():
        return True
    return False


def user_logged_in(token):
    email = token_to_email(token)
    if email:
        return True
    return False
