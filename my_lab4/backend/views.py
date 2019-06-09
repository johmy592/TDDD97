from flask import Flask, request
from database_helper import *
import os
import binascii
import json


app = Flask(__name__)


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


@app.route("/sign_out", methods=["GET", "POST"])
def sign_out():
    input_data = request.json
    token = input_data["token"]

    if user_signed_in(token):
        sign_out_user(token)
        response = {"success": True, "message": "Successfully signed out."}
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
    input_data = request.json
    token = input_data["token"]
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
    input_data = request.json
    token = input_data["token"]
    email = input_data["email"]

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
    return json.dumps(response)


@app.route("/home/get_user_messages_by_token", methods=["GET"])
def get_user_messages_by_token():
    input_data = request.json
    token = input_data["token"]
    email = email_from_token(token)

    if not user_signed_in(token):
        response = {"success": False, "message": "User not signed in."}
        return json.dumps(response)

    data = get_messages_from_db(email)
    response = {"success": True, "message": "User messages retrieved successfully.", "data": data}
    return json.dumps(response)


@app.route("/browse/get_user_messages_by_email", methods=["GET"])
def get_user_messages_by_email():
    input_data = request.json
    token = input_data["token"]
    email = input_data["email"]

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
    response = {"success": True, "message": "Message posted successfully."}
    return json.dumps(response)


if __name__ == "__main__":
    app.run()
