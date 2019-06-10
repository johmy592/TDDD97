import sqlite3
import datetime

connection = sqlite3.connect('database.db')
c = connection.cursor()


def sign_in_user(email, token):
    c.execute("SELECT * FROM signedInUsers WHERE email = ?", (email,))
    if c.fetchone():
        c.execute("UPDATE signedInUsers SET token = ? WHERE email = ?", (token, email))
    else:
        c.execute("INSERT INTO signedInUsers(email, token) VALUES (?, ?)", (email, token))
    connection.commit()


def add_new_user(email, password, firstname, familyname, gender, city, country):
    c.execute("""INSERT INTO users(email, password, firstname, familyname, gender, city, country) VALUES
            (?, ?, ?, ?, ?, ?, ?)""", (email, password, firstname, familyname, gender, city, country))
    connection.commit()


def sign_out_user(token):
    c.execute('DELETE FROM signedInUsers WHERE token = ?', (token,))
    connection.commit()


def email_from_token(token):
    c.execute('SELECT email FROM signedInUsers WHERE token = ?', (token,))
    result = c.fetchone()
    if result:
        email = result[0]
        return email
    return ""


def get_messages_from_db(email):
    c.execute('SELECT sender, message FROM messages WHERE reciever=?', (email,))
    result = c.fetchall()
    data = []
    for i in range(len(result)):
        writer = result[i][0]
        content = result[i][1]
        message_dict = {"writer": writer, "content": content}
        data.append(message_dict)
    return data


def find_user(email):
    user_data = get_user_data_from_db(email)
    if user_data:
        return True
    return False


def get_user_data_from_db(email):
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    user_data = c.fetchone()
    return user_data


def create_post(recipient, sender, message):
    minute = datetime.datetime.now().minute
    c.execute('INSERT INTO messages(reciever, sender, message, minute) VALUES (?, ?, ?, ?)', (recipient, sender, message, minute))
    connection.commit()


def update_password(email, new_password):
    c.execute('UPDATE users SET password = ? WHERE email = ?', (new_password, email))
    connection.commit()


def email_and_password_match(email, password):
    c.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
    if c.fetchone():
        return True
    return False


def user_signed_in(token):
    email = email_from_token(token)
    if email:
        return True
    return False

def count_online_users():
    c.execute('SELECT count(*) AS users FROM signedInUsers')
    return c.fetchone()

def get_num_page_views(email):
    c.execute('SELECT views FROM users WHERE email = ?', (email,))
    return c.fetchone()

def update_db_views(email):
    c.execute('UPDATE users SET views = views + 1 WHERE email = ?', (email,))
    connection.commit()

def get_message_times(email):
    #seven_days_ago = (datetime.datetime.today() - datetime.timedelta(7)).timetuple().tm_yday
    #c.execute('SELECT count(*) FROM messages WHERE receiver=? AND day > ? GROUP BY day', (email, seven_days_ago))
    c.execute('SELECT minute FROM messages WHERE reciever=?', (email,))
    result = c.fetchall()
    data = {}
    for i in range(len(result)):
        minute = result[i][0]
        if minute in data:
            data[minute] += 1
        else:
            data[minute] = 1
    return data
