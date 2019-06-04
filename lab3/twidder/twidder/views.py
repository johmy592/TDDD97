from flask import Flask, request
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket import WebSocketError
import os
import binascii
import json
from database_helper import *

app = Flask(__name__)


user_socket_dict = {}


@app.route("/")
def index():
    return app.send_static_file('client.html')


@app.route('/api')
def api():
    print "Entered api"
    if request.environ.get('wsgi.websocket'):
        print "WSGI.WEBSOCKET"
        ws = request.environ['wsgi.websocket']
        while True:
            try:
                user = ws.receive()
                if user in user_socket_dict:
                    user_socket_dict[str(user)].send('Force log out.')
                user_socket_dict[str(user)] = ws
                print("Added user: " + str(user))
            except WebSocketError:
                print "WebSocketError"
                break
    return ""


@app.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    input_data = request.json
    email = input_data["email"]
    password = input_data["password"]
    if not user_and_password_match(email, password):
        response = {"success": False, "message": "Wrong username or password."}
        return json.dumps(response)
    token = binascii.b2a_hex(os.urandom(18))
    sign_in_user(email, token)
    response = {"success": True, "message": "Successfully signed in.", "data": token}
    return json.dumps(response)


@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    input_data = request.json
    email = input_data["email"]
    password = input_data["password"]
    firstname = input_data["firstname"]
    familyname = input_data["familyname"]
    gender = input_data["gender"]
    city = input_data["city"]
    country = input_data["country"]
    if user_exists(email):
        response = {"success": False, "message": "User already exists."}
        return json.dumps(response)
    if email and password and firstname and familyname and gender and city and country:
        if len(password) > 7:
            add_user_to_db(email, password, firstname, familyname, gender, city, country)
            response = {"success": True, "message": "Successfully signed up."}
            return json.dumps(response)
    response = {"success": False, "message": "Form data missing or incorrect type."}
    return json.dumps(response)


@app.route("/account/sign_out", methods=["GET", "POST"])
def sign_out():
    input_data = request.json
    token = input_data["token"]
    if not user_logged_in(token):
        response = {"success": False, "message": "You are not signed in."}
        return json.dumps(response)
    sign_out_user(token)
    response = {"success": True, "message": "Successfully signed out."}
    connection.commit()
    return json.dumps(response)


@app.route("/account/change_password", methods=["GET", "POST"])
def change_password():
    input_data = request.json
    token = input_data["token"]
    old_password = input_data["oldPassword"]
    new_password = input_data["newPassword"]
    email = token_to_email(token)
    if not email:
        response = {"success": False, "message": "You are not signed in."}
        return json.dumps(response)
    if len(new_password) < 8:
        response = {"success": False, "message": "Password too short."}
        return json.dumps(response)
    if user_and_password_match(email, old_password):
        update_password(email, new_password)
        response = {"success": True, "message": "Password changed."}
        return json.dumps(response)
    response = {"success": False, "message": "Wrong password."}
    return json.dumps(response)


@app.route("/home/get_user_data_by_token", methods=["GET"])
def get_user_data_by_token():
    token = request.args.get("token", None)
    email = token_to_email(token)
    if not email:
        response = {"success": False, "message": "You are not signed in."}
        return json.dumps(response)
    user_data_list = get_user_data_from_db(email)
    if not user_data_list:
        response = {"success": False, "message": "No such user."}
        return json.dumps(response)
    user_data = user_data_list[0]
    match = {"email": user_data[0], "firstname": user_data[2], "familyname": user_data[3], "gender": user_data[4],
             "city": user_data[5], "country": user_data[6]}
    response = {"success": True, "message": "User data retrieved.", "data": match}
    return json.dumps(response)


@app.route("/browse/get_user_data_by_email", methods=["GET"])
def get_user_data_by_email():
    token = request.args.get("token", None)
    email = request.args.get("email", None)
    if not user_logged_in(token):
        response = {"success": False, "message": "You are not signed in."}
        return json.dumps(response)
    user_data_list = get_user_data_from_db(email)
    if not user_data_list:
        response = {"success": False, "message": "No such user."}
        return json.dumps(response)
    user_data = user_data_list[0]
    match = {"email": user_data[0], "firstname": user_data[2], "familyname": user_data[3], "gender": user_data[4],
             "city": user_data[5], "country": user_data[6]}
    response = {"success": True, "message": "User data retrieved.", "data": match}
    return json.dumps(response)


@app.route("/home/get_user_messages_by_token", methods=["GET"])
def get_user_messages_by_token():
    token = request.args.get("token", None)
    email = token_to_email(token)
    if not user_logged_in(token):
        response = {"success": False, "message": "You are not signed in."}
        return json.dumps(response)
    data = get_messages_from_db(email)
    response = {"success": True, "message": "User messages retrieved.", "data": data}
    return json.dumps(response)


@app.route("/browse/get_user_messages_by_email", methods=["GET"])
def get_user_messages_by_email():
    token = request.args.get("token", None)
    email = request.args.get("email", None)
    if not user_logged_in(token):
        response = {"success": False, "message": "You are not signed in."}
        return json.dumps(response)
    if not user_exists(email):
        response = {"success": False, "message": "No such user."}
        return json.dumps(response)
    data = get_messages_from_db(email)
    response = {"success": True, "message": "User messages retrieved.", "data": data}
    return json.dumps(response)


@app.route("/post_message", methods=["GET", "POST"])
def post_message():
    input_data = request.json
    token = input_data["token"]
    message = input_data["message"]
    receiver = input_data["email"]
    sender_email = token_to_email(token)
    if not sender_email:
        response = {"success": False, "message": "You are not signed in."}
        return json.dumps(response)
    if not user_exists(receiver):
        response = {"success": False, "message": "No such user."}
        return json.dumps(response)
    add_message_to_db(receiver, sender_email, message)
    response = {"success": True, "message": "Message posted"}
    return json.dumps(response)


if __name__ == '__main__':
    app.debug = True
    http_server = WSGIServer(('127.0.0.1', 5000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
