import unittest
from test_helper import *
import json


"""
Test cases for server functions.
Run
> sqlite3 database.db < schema.sql
before running tests for correct result.
"""
BAD_SIGNUP_ERROR_MSG = "Bad data."
WRONG_PWD_ERROR_MSG = "Wrong password."
SHORT_PWD_ERROR_MSG = "New password too short."
BAD_LOGIN_ERROR_MSG = "Wrong username or password."
NOT_SIGNED_IN_ERROR_MSG = "User not signed in."
NO_USER_ERROR_MSG = "User does not exist."
EMAIL_IN_USE_ERROR_MSG = "Email already in use."


class WebprogTestCase(unittest.TestCase):

    def test_case1(self):
        """
        Test case with only valid requests.
        """

        email = "test1@email.com"
        password = "testtesttest"
        first_name = "name1"
        family_name = "name2"
        gender = "Male"
        city = "Testcity"
        country = "Testcountry"

        # test sign up
        response = test_sign_up(email, password, first_name, family_name, gender, city, country)
        assert response.status_code == 200
        sign_up_json = json.loads(response.text)
        self.assertEqual(sign_up_json["success"], True, sign_up_json["message"])

        # test sign in
        response = test_sign_in(email, password)
        assert response.status_code == 200
        sign_in_json = json.loads(response.text)
        self.assertEqual(sign_in_json["success"], True, sign_in_json["message"])
        token1 = sign_in_json["data"]

        # password change
        new_password = "huehuehuehue"
        response = test_change_pwd(token1, password, new_password)
        assert response.status_code == 200
        json_change_pwd = json.loads(response.text)
        self.assertEqual(json_change_pwd["success"], True, json_change_pwd["message"])

        # test sign in again
        response = test_sign_in(email, new_password)
        assert response.status_code == 200
        sign_in_json = json.loads(response.text)
        self.assertEqual(sign_in_json["success"], True, sign_in_json["message"])
        token2 = sign_in_json["data"]
        # token should have been updated
        assert token1 != token2

        # Get user data by valid token
        response = test_user_data_by_token(token2)
        assert response.status_code == 200
        json_user_data = json.loads(response.text)
        self.assertEqual(json_user_data["success"], True, json_user_data["message"])
        assert json_user_data["data"]["email"] == email
        assert json_user_data["data"]["firstname"] == first_name
        assert json_user_data["data"]["familyname"] == family_name
        assert json_user_data["data"]["gender"] == gender
        assert json_user_data["data"]["city"] == city
        assert json_user_data["data"]["country"] == country

        # Post message on own wall
        message = "Testmessage"
        response = test_post_message(token2, email, message)
        assert response.status_code == 200
        json_post_message = json.loads(response.text)
        self.assertEqual(json_post_message["success"], True, json_post_message["message"])

        # Get messages
        response = test_user_messages_by_token(token2)
        assert response.status_code == 200
        messages_json = json.loads(response.text)
        self.assertEqual(messages_json["success"], True, messages_json["message"])
        messages = messages_json["data"][0]
        assert messages["writer"] == email
        assert messages["content"] == message

        # Sign out
        response = test_sign_out(token2)
        assert response.status_code == 200
        json_sign_out = json.loads(response.text)
        self.assertEqual(json_sign_out["success"], True, json_sign_out["message"])


    def test_case2(self):
        """
        Test cases for invalid sign up and sign in.
        """

        valid_email = "test2@email.com"
        valid_password = "asdasdasd"
        valid_firstname = "name1"
        valid_familyname = "name2"
        valid_gender = "Female"
        valid_city = "Testcity"
        valid_country = "Testcountry"

        # Valid sign up
        response = test_sign_up(valid_email, valid_password, valid_firstname, valid_familyname, valid_gender, valid_city,
                               valid_country)
        assert response.status_code == 200
        sign_up_json = json.loads(response.text)
        self.assertEqual(sign_up_json["success"], True, sign_up_json["message"])

        email = "invalid@email.com"
        password = "asdasdasd"
        first_name = "name1"
        family_name = "name2"
        gender = "Male"
        city = "Testcity"
        country = "Testcountry"

        invalid_password = "invalid_password"
        unknown_email = "invalid@email.com"


        # Sign up with missing input
        response = test_sign_up(email, password, "", family_name, gender, city, country)
        assert response.status_code == 200
        sign_up_json = json.loads(response.text)
        self.assertEqual(sign_up_json["success"], False, sign_up_json["message"])
        self.assertEqual(sign_up_json["message"], BAD_SIGNUP_ERROR_MSG, "Wrong error message.")

        # Sign up with too short password
        response = test_sign_up(email, "short", first_name, family_name, gender, city, country)
        assert response.status_code == 200
        sign_up_json = json.loads(response.text)
        self.assertEqual(sign_up_json["success"], False, sign_up_json["message"])
        self.assertEqual(sign_up_json["message"], BAD_SIGNUP_ERROR_MSG, "Wrong error message.")

        # Sign up with already existing email
        response = test_sign_up(valid_email, password, first_name, family_name, gender, city, country)
        assert response.status_code == 200
        sign_up_json = json.loads(response.text)
        self.assertEqual(sign_up_json["success"], False, sign_up_json["message"])
        self.assertEqual(sign_up_json["message"], EMAIL_IN_USE_ERROR_MSG, "Wrong error message.")


        # Sign in with unknown email
        response = test_sign_in(unknown_email, password)
        assert response.status_code == 200
        sign_in_json = json.loads(response.text)
        self.assertEqual(sign_in_json["success"], False, sign_in_json["message"])
        self.assertEqual(sign_in_json["message"], BAD_LOGIN_ERROR_MSG, "Wrong error message.")

        # Sign in with invalid password
        response = test_sign_in(valid_email, invalid_password)
        assert response.status_code == 200
        sign_in_json = json.loads(response.text)
        self.assertEqual(sign_in_json["success"], False, sign_in_json["message"])
        self.assertEqual(sign_in_json["message"], BAD_LOGIN_ERROR_MSG, "Wrong error message.")


    def test_case3(self):
        """
        Test cases for invalid options for remaining single-user functions.
        """

        email = "test3@email.com"
        password = "huehuehuehue"
        first_name = "name1"
        family_name = "name2"
        gender = "Male"
        city = "Testcity"
        country = "Testcountry"

        bad_token = "bad token"

        # Sign up with valid data
        response = test_sign_up(email, password, first_name, family_name, gender, city, country)
        assert response.status_code == 200
        sign_up_json = json.loads(response.text)
        self.assertEqual(sign_up_json["success"], True, sign_up_json["message"])

        # Sign in with valid data
        response = test_sign_in(email, password)
        assert response.status_code == 200
        sign_in_json = json.loads(response.text)
        self.assertEqual(sign_in_json["success"], True, sign_in_json["message"])
        token = sign_in_json["data"]

        # Change password with invalid old password
        new_password = "qweqweqwe"
        response = test_change_pwd(token, "invalid_password", new_password)
        assert response.status_code == 200
        json_change_pwd = json.loads(response.text)
        self.assertEqual(json_change_pwd["success"], False, json_change_pwd["message"])
        self.assertEqual(json_change_pwd["message"], WRONG_PWD_ERROR_MSG, "Wrong error message.")

        # Change password with too short new password
        new_password = "short"
        response = test_change_pwd(token, password, new_password)
        assert response.status_code == 200
        json_change_pwd = json.loads(response.text)
        self.assertEqual(json_change_pwd["success"], False, json_change_pwd["message"])
        self.assertEqual(json_change_pwd["message"], SHORT_PWD_ERROR_MSG, "Wrong error message.")

        # Post message with invalid token
        message = "Testmessage"
        response = test_post_message(bad_token, email, message)
        assert response.status_code == 200
        json_post_message = json.loads(response.text)
        self.assertEqual(json_post_message["success"], False, json_post_message["message"])
        self.assertEqual(json_post_message["message"], NOT_SIGNED_IN_ERROR_MSG, "Wrong error message.")

        # Post message with invalid email
        unknown_email = "invalid@email.com"
        message = "Testing test test"
        response = test_post_message(token, unknown_email, message)
        assert response.status_code == 200
        json_post_message = json.loads(response.text)
        self.assertEqual(json_post_message["success"], False, json_post_message["message"])
        self.assertEqual(json_post_message["message"], NO_USER_ERROR_MSG, "Wrong error message.")

        # get user message by token with invalid token
        response = test_user_messages_by_token(bad_token)
        assert response.status_code == 200
        messages_json = json.loads(response.text)
        self.assertEqual(messages_json["success"], False, messages_json["message"])
        self.assertEqual(messages_json["message"], NOT_SIGNED_IN_ERROR_MSG, "Wrong error message.")

        # Get user data with invalid token
        response = test_user_data_by_token(bad_token)
        assert response.status_code == 200
        json_user_data = json.loads(response.text)
        self.assertEqual(json_user_data["success"], False, json_user_data["message"])
        self.assertEqual(json_user_data["message"], NOT_SIGNED_IN_ERROR_MSG, "Wrong error message.")


        # Sign out with invalid token
        response = test_sign_out(bad_token)
        assert response.status_code == 200
        json_sign_out = json.loads(response.text)
        self.assertEqual(json_sign_out["success"], False, json_sign_out["message"])
        self.assertEqual(json_sign_out["message"], NOT_SIGNED_IN_ERROR_MSG, "Wrong error message.")

        # Sign out with valid token
        response = test_sign_out(token)
        assert response.status_code == 200
        json_sign_out = json.loads(response.text)
        self.assertEqual(json_sign_out["success"], True, json_sign_out["message"])


    def test_case4(self):
        """
        Test cases for functionality that requires multiple users.
        """

        email1 = "test4@email.com"
        password1 = "asdasdasd"
        first_name1 = "name1"
        family_name1 = "name2"
        gender1 = "Male"
        city1 = "Testcity"
        country1 = "Testcountry"

        email2 = "test5@email.com"
        password2 = "asdasdasd"
        first_name2 = "name1"
        family_name2 = "name2"
        gender2 = "Male"
        city2 = "Testcity"
        country2 = "Testcountry"

        bad_token = "bad token"
        unknown_email = "invalid@email.com"

        # Sign up and sign in with valid data
        response = test_sign_up(email1, password1, first_name1, family_name1, gender1, city1, country1)
        assert response.status_code == 200
        sign_up_json = json.loads(response.text)
        self.assertEqual(sign_up_json["success"], True, sign_up_json["message"])

        response = test_sign_in(email1, password1)
        assert response.status_code == 200
        sign_in_json = json.loads(response.text)
        self.assertEqual(sign_in_json["success"], True, sign_in_json["message"])
        token1 = sign_in_json["data"]

        # Sign up and sign in with valid data
        response = test_sign_up(email2, password2, first_name2, family_name2, gender2, city2, country2)
        assert response.status_code == 200
        sign_up_json = json.loads(response.text)
        self.assertEqual(sign_up_json["success"], True, sign_up_json["message"])

        response = test_sign_in(email2, password2)
        assert response.status_code == 200
        sign_in_json = json.loads(response.text)
        self.assertEqual(sign_in_json["success"], True, sign_in_json["message"])
        token2 = sign_in_json["data"]

        
        # Post message on other users wall with valid data
        message = "Testmessage"
        response = test_post_message(token1, email2, message)
        assert response.status_code == 200
        json_post_message = json.loads(response.text)
        self.assertEqual(json_post_message["success"], True, json_post_message["message"])

        # get user messages by email with invalid email
        response = test_user_messages_by_email(token1, unknown_email)
        assert response.status_code == 200
        messages_json = json.loads(response.text)
        self.assertEqual(messages_json["success"], False, messages_json["message"])
        self.assertEqual(messages_json["message"], NO_USER_ERROR_MSG, "Wrong error message.")

        # get user messages by email with invalid token
        response = test_user_messages_by_email(bad_token, email2)
        assert response.status_code == 200
        messages_json = json.loads(response.text)
        self.assertEqual(messages_json["success"], False, messages_json["message"])
        self.assertEqual(messages_json["message"], NOT_SIGNED_IN_ERROR_MSG, "Wrong error message.")

        # get user messages by email with valid token and email
        response = test_user_messages_by_email(token1, email2)
        assert response.status_code == 200
        messages_json = json.loads(response.text)
        self.assertEqual(messages_json["success"], True, messages_json["message"])
        messages = messages_json["data"][0]
        assert messages["writer"] == email1
        assert messages["content"] == message

        # get user data with invalid email
        response = test_user_data_by_email(token1, unknown_email)
        assert response.status_code == 200
        json_user_data = json.loads(response.text)
        self.assertEqual(json_user_data["success"], False, sign_up_json["message"])
        self.assertEqual(json_user_data["message"], NO_USER_ERROR_MSG, "Wrong error message.")

        # get user data by email with invalid token
        response = test_user_data_by_email(bad_token, email2)
        assert response.status_code == 200
        json_user_data = json.loads(response.text)
        self.assertEqual(json_user_data["success"], False, sign_up_json["message"])
        self.assertEqual(json_user_data["message"], NOT_SIGNED_IN_ERROR_MSG, "Wrong error message.")

        # get user data by email with valid token and email
        response = test_user_data_by_email(token1, email2)
        assert response.status_code == 200
        sign_up_json = json.loads(response.text)
        self.assertEqual(sign_up_json["success"], True, sign_up_json["message"])


        # Sign out both users with valid token.
        response = test_sign_out(token1)
        assert response.status_code == 200
        json_sign_out = json.loads(response.text)
        self.assertEqual(json_sign_out["success"], True, json_sign_out["message"])

        response = test_sign_out(token2)
        assert response.status_code == 200
        json_sign_out = json.loads(response.text)
        self.assertEqual(json_sign_out["success"], True, json_sign_out["message"])


if __name__ == "__main__":
    unittest.main()
