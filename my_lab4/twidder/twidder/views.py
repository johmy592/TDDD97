from flask import Flask, request
from database_helper import *
import os
import binascii
import json
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket import WebSocketError

from __init__ import app



socket_dict = {}

# Helper functions ##################################################
def update_num_online_users():
    users_online = count_online_users()[0]
    temp_dict = {"message": "online users", "data": users_online}
    unresponsive_sockets = []
    for user in socket_dict:
        web_socket = socket_dict[user]
        try:
            web_socket.send(json.dumps(temp_dict))
        except WebSocketError:
            unresponsive_socket = user
            unresponsive_sockets.append(unresponsive_socket)
    # Removes unresponsive sockets
    for user in unresponsive_sockets:
        del socket_dict[user]


def update_num_views(email):
    if email in socket_dict:
        num_views = get_num_page_views(email)[0]
        package = {"message": "update views", "data": num_views}
        web_socket = socket_dict[email]
        unresponsive_socket = ""
        try:
            web_socket.send(json.dumps(package))
        except WebSocketError:
            unresponsive_socket = email
        if unresponsive_socket:
            # Remove the socket if its unresponsive
            del socket_dict[unresponsive_socket]


def update_minutewise_posts(email):
    # Doing by the minute for demo purposes, makes more sense to do e.g. daily
    if email in socket_dict:
        message_times = get_message_times(email)
        package = {"message": "update posts chart", "data": message_times}
        web_socket = socket_dict[email]
        unresponsive_socket = ""
        try:
            web_socket.send(json.dumps(package))
        except WebSocketError:
            unresponsive_socket = email
        if unresponsive_socket:
            # Remove the socket if its unresponsive
            del socket_dict[unresponsive_socket]
# End of helper funcitons ###########################################



@app.route("/")
def index():
    return app.send_static_file('client.html')


@app.route('/api')
def api():
    if request.environ.get('wsgi.websocket'):
        web_socket = request.environ['wsgi.websocket']
        while True:
            try:
                user_token = web_socket.receive()
                user = email_from_token(user_token)
                if user in socket_dict:
                    message_dict = {"message": "Force log out."}
                    socket_dict[str(user)].send(json.dumps(message_dict))
                if user != None:
                    socket_dict[str(user)] = web_socket
                    update_num_online_users()
                    update_num_views(user)
                    update_minutewise_posts(user)
            except WebSocketError:
                print "WebSocketError"
                break
    return ""



@app.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    input_data = request.json
    password = input_data["password"]
    email = input_data["email"]

    if email_and_password_match(email, password):
        token = binascii.b2a_hex(os.urandom(18))
        sign_in_user(email, token)
        response = {"success": True, "message": "Successfully signed in.", "data": token}
        return json.dumps(response)

    response = {"success": False, "message": "Wrong username or password."}
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

    if find_user(email):
        response = {"success": False, "message": "Email already in use."}
        return json.dumps(response)

    if email and password and firstname and familyname and gender and city and country:
        if len(password) > 7:
            add_new_user(email, password, firstname, familyname, gender, city, country)
            response = {"success": True, "message": "Successfully signed up."}
            return json.dumps(response)

    response = {"success": False, "message": "Bad data."}
    return json.dumps(response)


@app.route("/account/sign_out", methods=["GET", "POST"])
def sign_out():
    input_data = request.json
    token = input_data["token"]

    if user_signed_in(token):
        sign_out_user(token)
        response = {"success": True, "message": "Successfully signed out."}
        print "Signed out boi"
        update_num_online_users();
        return json.dumps(response)

    response = {"success": False, "message": "User not signed in."}
    return json.dumps(response)


@app.route("/account/change_password", methods=["GET", "POST"])
def change_password():
    input_data = request.json
    token = input_data["token"]
    old_password = input_data["oldPassword"]
    new_password = input_data["newPassword"]
    email = email_from_token(token)

    if not email:
        response = {"success": False, "message": "User not signed in."}
        return json.dumps(response)

    if not email_and_password_match(email, old_password):
        response = {"success": False, "message": "Wrong password."}
        return json.dumps(response)

    if len(new_password) < 8:
        response = {"success": False, "message": "New password too short."}
        return json.dumps(response)

    update_password(email, new_password)
    response = {"success": True, "message": "Password changed successfully."}
    return json.dumps(response)


@app.route("/home/get_user_data_by_token", methods=["GET"])
def get_user_data_by_token():
    token = request.args.get("token", None)
    email = email_from_token(token)

    if not email:
        response = {"success": False, "message": "User not signed in."}
        return json.dumps(response)

    user_data = get_user_data_from_db(email)
    if not user_data:
        response = {"success": False, "message": "User does not exist."}
        return json.dumps(response)

    return_data = {"email": user_data[0], "firstname": user_data[2], "familyname": user_data[3], "gender": user_data[4],
             "city": user_data[5], "country": user_data[6]}
    response = {"success": True, "message": "User data retrieved.", "data": return_data}
    return json.dumps(response)


@app.route("/browse/get_user_data_by_email", methods=["GET"])
def get_user_data_by_email():
    token = request.args.get("token", None)
    email = request.args.get("email", None)
    if not user_signed_in(token):
        response = {"success": False, "message": "User not signed in."}
        return json.dumps(response)

    user_data = get_user_data_from_db(email)
    if not user_data:
        response = {"success": False, "message": "User does not exist."}
        return json.dumps(response)

    return_data = {"email": user_data[0], "firstname": user_data[2], "familyname": user_data[3], "gender": user_data[4],
             "city": user_data[5], "country": user_data[6]}
    response = {"success": True, "message": "User data retrieved.", "data": return_data}

    update_db_views(email)
    update_num_views(email)
    return json.dumps(response)


@app.route("/home/get_user_messages_by_token", methods=["GET"])
def get_user_messages_by_token():
    token = request.args.get("token", None)
    email = email_from_token(token)

    if not user_signed_in(token):
        response = {"success": False, "message": "User not signed in."}
        return json.dumps(response)

    data = get_messages_from_db(email)
    response = {"success": True, "message": "User messages retrieved successfully.", "data": data}
    return json.dumps(response)


@app.route("/browse/get_user_messages_by_email", methods=["GET"])
def get_user_messages_by_email():
    token = request.args.get("token", None)
    email = request.args.get("email", None)
    if not user_signed_in(token):
        response = {"success": False, "message": "User not signed in."}
        return json.dumps(response)

    if not find_user(email):
        response = {"success": False, "message": "User does not exist."}
        return json.dumps(response)

    data = get_messages_from_db(email)
    response = {"success": True, "message": "User messages retrieved successfully.", "data": data}
    return json.dumps(response)


@app.route("/post_message", methods=["GET", "POST"])
def post_message():
    input_data = request.json
    token = input_data["token"]
    recipient = input_data["email"]
    message = input_data["message"]

    sender = email_from_token(token)

    if not sender:
        response = {"success": False, "message": "User not signed in."}
        return json.dumps(response)

    if not find_user(recipient):
        response = {"success": False, "message": "User does not exist."}
        return json.dumps(response)

    create_post(recipient, sender, message)
    update_minutewise_posts(recipient)
    response = {"success": True, "message": "Message posted successfully."}
    return json.dumps(response)


if __name__ == "__main__":
    app.debug = True
    http_server = WSGIServer(('127.0.0.1', 5000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
