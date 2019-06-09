import requests


def test_sign_in(email, password):
    url = 'http://127.0.0.1:5000/sign_in'
    login_data = {"email": email, "password": password}
    response = requests.post(url, json=login_data)
    return response


def test_sign_up(email, password, firstname, familyname, gender, city, country):
    url = 'http://127.0.0.1:5000/sign_up'
    signup_data = {"email": email, "password": password, "firstname": firstname, "familyname": familyname,
                   "gender": gender, "city": city, "country": country}
    response = requests.post(url, json=signup_data)
    return response


def test_sign_out(token):
    url = 'http://127.0.0.1:5000/sign_out'
    login_data = {"token": token}
    response = requests.post(url, json=login_data)
    return response


def test_change_pwd(token, old_password, new_password):
    url = "http://127.0.0.1:5000/account/change_password"
    data = {"token": token, "oldPassword": old_password, "newPassword": new_password}
    response = requests.post(url, json=data)
    return response


def test_user_data_by_token(token):
    url = "http://127.0.0.1:5000/home/get_user_data_by_token"
    data = {"token": token}
    response = requests.get(url, json=data)
    return response


def test_user_data_by_email(token, email):
    url = "http://127.0.0.1:5000/browse/get_user_data_by_email"
    data = {"token": token, "email": email}
    response = requests.get(url, json=data)
    return response


def test_user_messages_by_token(token):
    url = "http://127.0.0.1:5000/home/get_user_messages_by_token"
    data = {"token": token}
    response = requests.get(url, json=data)
    return response


def test_user_messages_by_email(token, email):
    url = "http://127.0.0.1:5000/browse/get_user_messages_by_email"
    data = {"token": token, "email": email}
    response = requests.get(url, json=data)
    return response


def test_post_message(token, email, message):
    url = "http://127.0.0.1:5000/post_message"
    data = {"token": token, "email": email, "message": message}
    response = requests.post(url, json=data)
    return response
