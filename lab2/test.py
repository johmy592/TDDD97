import unittest
from test_helper import *
import json
#Selenium

"""
Test cases for server.py functions. 
Should be run with and empty database for correct results.
"""
ERROR_MSG_not_signed_in = "You are not signed in."
ERROR_MSG_no_such_user = "No such user."
ERROR_MSG_wrong_pwd = "Wrong password."
ERROR_MSG_short_pwd = "Password too short."
ERROR_MSG_bad_login = "Wrong username or password."
ERROR_MSG_user_exists = "User already exists."
ERROR_MSG_invalid_signup_data = "Form data missing or incorrect type."


class SomethingTestCase(unittest.TestCase):
    """
    Tests for sign up functionality.
    """
    """
    Test case with one user and all data valid.
    """

    def test_case1(self):

        email = "test1@email.com"
        password = "asdasdasd"
        firstname = "name1"
        familyname = "name2"
        gender = "Male"
        city = "Testington"
        country = "Testland"

        # Valid sign up
        response = http_signup(email, password, firstname, familyname, gender, city, country)
        assert response.status_code == 200
        json_sign_up = json.loads(response.text)
        self.assertEqual(json_sign_up["success"], True, json_sign_up["message"])

        # Valid sign in
        response = http_sign_in(email, password)
        assert response.status_code == 200
        json_sign_in = json.loads(response.text)
        self.assertEqual(json_sign_up["success"], True, json_sign_in["message"])
        assert "data" in json_sign_in
        token1 = json_sign_in["data"]

        # Valid sign in again (Should only update token)
        response = http_sign_in(email, password)
        assert response.status_code == 200
        json_sign_in = json.loads(response.text)
        self.assertEqual(json_sign_up["success"], True, json_sign_in["message"])
        assert "data" in json_sign_in
        token2 = json_sign_in["data"]
        assert token1 != token2

        # Valid change pwd
        new_password = "qweqweqwe"
        response = http_change_pwd(token2, password, new_password)
        assert response.status_code == 200
        json_change_pwd = json.loads(response.text)
        self.assertEqual(json_change_pwd["success"], True, json_change_pwd["message"])

        # Get user data by valid token
        response = http_user_data_by_token(token2)
        assert response.status_code == 200
        json_user_data = json.loads(response.text)
        self.assertEqual(json_user_data["success"], True, json_user_data["message"])
        assert json_user_data["data"]["email"] == email
        assert json_user_data["data"]["firstname"] == firstname
        assert json_user_data["data"]["familyname"] == familyname
        assert json_user_data["data"]["gender"] == gender
        assert json_user_data["data"]["city"] == city
        assert json_user_data["data"]["country"] == country

        # Post message on own wall
        message = "Testing test test"
        response = http_post_message(token2, email, message)
        assert response.status_code == 200
        json_post_message = json.loads(response.text)
        self.assertEqual(json_post_message["success"], True, json_post_message["message"])

        # Get messages by valid token
        response = http_user_messages_by_token(token2)
        assert response.status_code == 200
        json_messages = json.loads(response.text)
        self.assertEqual(json_messages["success"], True, json_messages["message"])
        message_dict = json_messages["data"][0]
        assert message_dict["writer"] == email
        assert message_dict["content"] == message

        # Sign out valid token.
        response = http_sign_out(token2)
        assert response.status_code == 200
        json_sign_out = json.loads(response.text)
        self.assertEqual(json_sign_out["success"], True, json_sign_out["message"])

    """
    TestCase that tries all invalid Sign up and in options.
    """
    def test_case2(self):
        valid_email = "test2@email.com"
        valid_password = "asdasdasd"
        valid_firstname = "name1"
        valid_familyname = "name2"
        valid_gender = "Female"
        valid_city = "Testington"
        valid_country = "Testland"

        # Valid sign up
        response = http_signup(valid_email, valid_password, valid_firstname, valid_familyname, valid_gender, valid_city,
                               valid_country)
        assert response.status_code == 200
        json_sign_up = json.loads(response.text)
        self.assertEqual(json_sign_up["success"], True, json_sign_up["message"])

        email = "invalid@email.com"
        password = "asdasdasd"
        firstname = "name1"
        familyname = "name2"
        gender = "Male"
        city = "Testington"
        country = "Testland"

        invalid_password = "invalid_password"
        invalid_email = "invalid@email.com"

        # --------------------------Sign up tests----------------------------- #
        # Sign up with missing input
        response = http_signup(email, password, "", familyname, gender, city, country)
        assert response.status_code == 200
        json_sign_up = json.loads(response.text)
        self.assertEqual(json_sign_up["success"], False, json_sign_up["message"])
        self.assertEqual(json_sign_up["message"], ERROR_MSG_invalid_signup_data, "Wrong error message.")

        # Sign up with too short password
        response = http_signup(email, "short", firstname, familyname, gender, city, country)
        assert response.status_code == 200
        json_sign_up = json.loads(response.text)
        self.assertEqual(json_sign_up["success"], False, json_sign_up["message"])
        self.assertEqual(json_sign_up["message"], ERROR_MSG_invalid_signup_data, "Wrong error message.")

        # Sign up with already existing email
        response = http_signup(valid_email, password, firstname, familyname, gender, city, country)
        assert response.status_code == 200
        json_sign_up = json.loads(response.text)
        self.assertEqual(json_sign_up["success"], False, json_sign_up["message"])
        self.assertEqual(json_sign_up["message"], ERROR_MSG_user_exists, "Wrong error message.")

        # ----------------------------Sign in tests--------------------------- #
        # Sign in with invalid email
        response = http_sign_in(invalid_email, password)
        assert response.status_code == 200
        json_sign_in = json.loads(response.text)
        self.assertEqual(json_sign_in["success"], False, json_sign_up["message"])
        self.assertEqual(json_sign_in["message"], ERROR_MSG_bad_login, "Wrong error message.")

        # Sign in with invalid password
        response = http_sign_in(valid_email, invalid_password)
        assert response.status_code == 200
        json_sign_in = json.loads(response.text)
        self.assertEqual(json_sign_in["success"], False, json_sign_up["message"])
        self.assertEqual(json_sign_in["message"], ERROR_MSG_bad_login, "Wrong error message.")

    """
    TestCase that tries invalid options for change_password, get_user_data_by_token, post_message, 
    get_user_messages_by_token and sign_out
    """
    def test_case3(self):
        email = "test3@email.com"
        password = "asdasdasd"
        firstname = "name1"
        familyname = "name2"
        gender = "Male"
        city = "Testington"
        country = "Testland"

        invalid_token = "invalid_token"

        # Sign up with valid data
        response = http_signup(email, password, firstname, familyname, gender, city, country)
        assert response.status_code == 200
        json_sign_up = json.loads(response.text)
        self.assertEqual(json_sign_up["success"], True, json_sign_up["message"])

        # Sign in with valid data
        response = http_sign_in(email, password)
        assert response.status_code == 200
        json_sign_in = json.loads(response.text)
        self.assertEqual(json_sign_in["success"], True, json_sign_up["message"])
        token = json_sign_in["data"]

        # Change password with invalid old password
        new_password = "qweqweqwe"
        response = http_change_pwd(token, "invalid_password", new_password)
        assert response.status_code == 200
        json_change_pwd = json.loads(response.text)
        self.assertEqual(json_change_pwd["success"], False, json_change_pwd["message"])
        self.assertEqual(json_change_pwd["message"], ERROR_MSG_wrong_pwd, "Wrong error message.")

        # Change password with too short new password
        new_password = "short"
        response = http_change_pwd(token, password, new_password)
        assert response.status_code == 200
        json_change_pwd = json.loads(response.text)
        self.assertEqual(json_change_pwd["success"], False, json_change_pwd["message"])
        self.assertEqual(json_change_pwd["message"], ERROR_MSG_short_pwd, "Wrong error message.")

        # Get user data with invalid token
        response = http_user_data_by_token(invalid_token)
        assert response.status_code == 200
        json_user_data = json.loads(response.text)
        self.assertEqual(json_user_data["success"], False, json_user_data["message"])
        self.assertEqual(json_user_data["message"], ERROR_MSG_not_signed_in, "Wrong error message.")

        # Post message with invalid token
        message = "Testing test test"
        response = http_post_message(invalid_token, email, message)
        assert response.status_code == 200
        json_post_message = json.loads(response.text)
        self.assertEqual(json_post_message["success"], False, json_post_message["message"])
        self.assertEqual(json_post_message["message"], ERROR_MSG_not_signed_in, "Wrong error message.")

        # Post message with invalid email
        invalid_email = "invalid@email.com"
        message = "Testing test test"
        response = http_post_message(token, invalid_email, message)
        assert response.status_code == 200
        json_post_message = json.loads(response.text)
        self.assertEqual(json_post_message["success"], False, json_post_message["message"])
        self.assertEqual(json_post_message["message"], ERROR_MSG_no_such_user, "Wrong error message.")

        # get user message by token with invalid token
        response = http_user_messages_by_token(invalid_token)
        assert response.status_code == 200
        json_messages = json.loads(response.text)
        self.assertEqual(json_messages["success"], False, json_messages["message"])
        self.assertEqual(json_messages["message"], ERROR_MSG_not_signed_in, "Wrong error message.")

        # Sign out with invalid token
        response = http_sign_out(invalid_token)
        assert response.status_code == 200
        json_sign_out = json.loads(response.text)
        self.assertEqual(json_sign_out["success"], False, json_sign_out["message"])
        self.assertEqual(json_sign_out["message"], ERROR_MSG_not_signed_in, "Wrong error message.")

        # Sign out with valid token
        response = http_sign_out(token)
        assert response.status_code == 200
        json_sign_out = json.loads(response.text)
        self.assertEqual(json_sign_out["success"], True, json_sign_out["message"])

    """
    TestCase for functionality that needs more than one user. Both valid and invalid.
    """
    def test_case4(self):
        email1 = "test4@email.com"
        password1 = "asdasdasd"
        firstname1 = "name1"
        familyname1 = "name2"
        gender1 = "Male"
        city1 = "Testington"
        country1 = "Testland"

        email2 = "test5@email.com"
        password2 = "asdasdasd"
        firstname2 = "name1"
        familyname2 = "name2"
        gender2 = "Male"
        city2 = "Testington"
        country2 = "Testland"

        invalid_token = "invalid token"
        invalid_email = "invalid@email.com"

        # Sign up and sign in with valid data
        response = http_signup(email1, password1, firstname1, familyname1, gender1, city1, country1)
        assert response.status_code == 200
        json_sign_up = json.loads(response.text)
        self.assertEqual(json_sign_up["success"], True, json_sign_up["message"])

        response = http_sign_in(email1, password1)
        assert response.status_code == 200
        json_sign_in = json.loads(response.text)
        self.assertEqual(json_sign_in["success"], True, json_sign_up["message"])
        token1 = json_sign_in["data"]

        # Sign up and sign in with valid data
        response = http_signup(email2, password2, firstname2, familyname2, gender2, city2, country2)
        assert response.status_code == 200
        json_sign_up = json.loads(response.text)
        self.assertEqual(json_sign_up["success"], True, json_sign_up["message"])

        response = http_sign_in(email2, password2)
        assert response.status_code == 200
        json_sign_in = json.loads(response.text)
        self.assertEqual(json_sign_in["success"], True, json_sign_up["message"])
        token2 = json_sign_in["data"]

        # ------------------------------Tests----------------------------------- #

        # Get_user_data_by_email with invalid email
        response = http_user_data_by_email(token1, invalid_email)
        assert response.status_code == 200
        json_user_data = json.loads(response.text)
        self.assertEqual(json_user_data["success"], False, json_sign_up["message"])
        self.assertEqual(json_user_data["message"], ERROR_MSG_no_such_user, "Wrong error message.")

        # get user data by email with invalid token
        response = http_user_data_by_email(invalid_token, email2)
        assert response.status_code == 200
        json_user_data = json.loads(response.text)
        self.assertEqual(json_user_data["success"], False, json_sign_up["message"])
        self.assertEqual(json_user_data["message"], ERROR_MSG_not_signed_in, "Wrong error message.")

        # get user data by email with valid data
        response = http_user_data_by_email(token1, email2)
        assert response.status_code == 200
        json_sign_up = json.loads(response.text)
        self.assertEqual(json_sign_up["success"], True, json_sign_up["message"])

        # Post message on other users wall with valid data
        message = "Testing test test"
        response = http_post_message(token1, email2, message)
        assert response.status_code == 200
        json_post_message = json.loads(response.text)
        self.assertEqual(json_post_message["success"], True, json_post_message["message"])

        # get user messages by email with invalid email
        response = http_user_messages_by_email(token1, invalid_email)
        assert response.status_code == 200
        json_messages = json.loads(response.text)
        self.assertEqual(json_messages["success"], False, json_messages["message"])
        self.assertEqual(json_messages["message"], ERROR_MSG_no_such_user, "Wrong error message.")

        # get user messages by email with invalid token
        response = http_user_messages_by_email(invalid_token, email2)
        assert response.status_code == 200
        json_messages = json.loads(response.text)
        self.assertEqual(json_messages["success"], False, json_messages["message"])
        self.assertEqual(json_messages["message"], ERROR_MSG_not_signed_in, "Wrong error message.")

        # get user messages by email with valid data
        response = http_user_messages_by_email(token1, email2)
        assert response.status_code == 200
        json_messages = json.loads(response.text)
        self.assertEqual(json_messages["success"], True, json_messages["message"])
        message_dict = json_messages["data"][0]
        assert message_dict["writer"] == email1
        assert message_dict["content"] == message

        # Sign out both users with valid token.
        response = http_sign_out(token1)
        assert response.status_code == 200
        json_sign_out = json.loads(response.text)
        self.assertEqual(json_sign_out["success"], True, json_sign_out["message"])

        response = http_sign_out(token2)
        assert response.status_code == 200
        json_sign_out = json.loads(response.text)
        self.assertEqual(json_sign_out["success"], True, json_sign_out["message"])


if __name__ == "__main__":
    unittest.main()
