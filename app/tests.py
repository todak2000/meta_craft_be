from django.test import TestCase
from decouple import config
import unittest
import json
import os
import datetime

# from flask_sqlalchemy import SQLAlchemy
from app.CustomCode import string_generator, password_functions
import app

from .models import Service_Provider, Client, Otp
import jwt

# Create your tests here.


class MetaCraftTestCase(TestCase):
    def setUp(self):
        new_user = {
            "firstname": "Daniel2",
            "lastname": "Testing2",
            "phone": "07038126700",
            "email": "todak1000@gmail.com",
            "password": "test1234",
            "role": "provider",
            # "role": "client",
            "code": "12345",
            "reset": "54321",
        }
        encryped_password = password_functions.generate_password_hash(
            new_user["password"]
        )
        # generate user_id
        if new_user["role"] == "provider":
            userRandomId = "SP" + string_generator.numeric(4)
            # Save user_data
            new_userData = Service_Provider(
                _id=userRandomId,
                firstname=new_user["firstname"],
                lastname=new_user["lastname"],
                email=new_user["email"],
                phone=new_user["phone"],
                password=encryped_password,
            )
            new_userData.save()
        else:
            userRandomId = "CT" + string_generator.numeric(4)
            # Save user_data
            new_userData = Client(
                _id=userRandomId,
                firstname=new_user["firstname"],
                lastname=new_user["lastname"],
                email=new_user["email"],
                phone=new_user["phone"],
                password=encryped_password,
            )
            new_userData.save()
        user_OTP = Otp(
            user_id=userRandomId,
            otp_code=new_user["code"],
            password_reset_code=new_user["reset"],
        )
        user_OTP.save()

        # Animal.objects.create(name="lion", sound="roar")
        return
        #
        # Animal.objects.create(name="cat", sound="meow")

    def test_home(self):
        """The api index page display accordinging"""
        res = self.client.get("/")
        init = json.dumps(res.data)
        data = json.loads(init)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    # lion = Animal.objects.get(name="lion")
    # cat = Animal.objects.get(name="cat")
    # self.assertEqual(lion.speak(), 'The lion says "roar"')
    # self.assertEqual(cat.speak(), 'The cat says "meow"')

    def test_auth(self):  # Generate token
        """Test to see if authenticaton with token works"""
        timeLimit = datetime.datetime.utcnow() + datetime.timedelta(
            minutes=1440
        )  # set duration for token
        payload = {
            "user_id": f"{string_generator.alphanumeric(5)}",
            "validated": True,
            "role": "provider",
            "exp": timeLimit,
        }
        token = jwt.encode(payload, config("SECRET_KEY"), algorithm="HS256")

        res = self.client.post(
            "/auth",
            HTTP_AUTHORIZATION="Bearer " + str(token),
            # headers={"Authorization": "Bearer " + str(token)},
        )
        init = json.dumps(res.data)
        data = json.loads(init)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_signup(self):  # Generate token
        """Test to see if authenticaton with token works"""
        country_code = "234"
        new_user = {
            "firstname": "Daniel",
            "lastname": "Testing",
            "phone": "07038126711",
            "email": "todak2000@gmail.com",
            "password": "test123",
            # "role": "provider",
            "role": "client",
        }

        res = self.client.post(
            "/signup",
            new_user,
        )
        init = json.dumps(res.data)
        data = json.loads(init)
        if new_user["role"] == "provider":
            user = Service_Provider.objects.get(phone=new_user["phone"])
        else:
            user = Client.objects.get(phone=new_user["phone"])
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["user_id"], user._id)

    def test_verify(self):  # Generate token
        """Test to see if authenticaton with token works"""
        new_user = {
            "firstname": "Daniel2",
            "lastname": "Testing2",
            "phone": "07038128700",
            "email": "todak20@gmail.com",
            "password": "test1234",
            # "role": "provider",
            "role": "client",
            "code": "12345",
            "reset": "54321",
        }
        encryped_password = password_functions.generate_password_hash(
            new_user["password"]
        )
        # generate user_id
        if new_user["role"] == "provider":
            userRandomId = "SP" + string_generator.numeric(4)
            # Save user_data
            new_userData = Service_Provider(
                _id=userRandomId,
                firstname=new_user["firstname"],
                lastname=new_user["lastname"],
                email=new_user["email"],
                phone=new_user["phone"],
                password=encryped_password,
            )
            new_userData.save()
        else:
            userRandomId = "CT" + string_generator.numeric(4)
            # Save user_data
            new_userData = Client(
                _id=userRandomId,
                firstname=new_user["firstname"],
                lastname=new_user["lastname"],
                email=new_user["email"],
                phone=new_user["phone"],
                password=encryped_password,
            )
            new_userData.save()
        user_OTP = Otp(
            user_id=userRandomId,
            otp_code=new_user["code"],
            password_reset_code=new_user["reset"],
        )
        user_OTP.save()
        timeLimit = datetime.datetime.utcnow() + datetime.timedelta(
            minutes=1440
        )  # set duration for token
        payload = {
            "user_id": f"{userRandomId}",
            "validated": False,
            "role": new_user["role"],
            "exp": timeLimit,
        }
        token = jwt.encode(payload, config("SECRET_KEY"), algorithm="HS256")
        # code = string_generator.numeric(5)
        code = "54321"
        res = self.client.post(
            "/verify-user",
            # headers={"Authorization": "Bearer " + str(token)},
            HTTP_AUTHORIZATION="Bearer " + str(token),
            data={"code": code},
        )

        init = json.dumps(res.data)
        data = json.loads(init)
        #
        self.assertEqual(res.status_code, 200)
        # self.assertEqual(data["reset"], False)
        self.assertEqual(data["reset"], True)

    def test_signin(self):  # test signin
        """Test to see if authenticaton with token works"""
        new_user = {
            "email": "todak1000@gmail.com",
            "password": "test123",
        }
        res = self.client.post(
            "/signin",
            new_user,
        )
        init = json.dumps(res.data)
        data = json.loads(init)
        print(data, "***** signin")
        # self.assertEqual(res.status_code, 200)
        # self.assertEqual(data["success"], True)
        # self.assertEqual(data["user_id"], Client.objects.get(id=1)._id)
        # self.assertEqual(data["message"], "The registration was successful.")

    def test_forgot_password(self):  # forgot password
        """Test to see if authenticaton with token works"""
        new_user = {
            "email": "todak1000@gmail.com",
        }
        res = self.client.post(
            "/forgot-password",
            new_user,
        )
        init = json.dumps(res.data)
        data = json.loads(init)
        print(data, "***** forgot passwrod")
        # self.assertEqual(res.status_code, 200)
        # self.assertEqual(data["success"], True)
        # self.assertEqual(data["message"], "Reset Code sent!")

    def test_change_password(self):  # test signin
        """Test to see if authenticaton with token works"""
        new_user = {
            "confirm_password": "test123",
            "password": "test123",
        }
        res = self.client.post(
            "/change-password",
            new_user,
        )
        init = json.dumps(res.data)
        data = json.loads(init)
        print(data, "*****")
        # self.assertEqual(res.status_code, 200)
        # self.assertEqual(data["success"], True)
        # self.assertEqual(data["user_id"], Client.objects.get(id=1)._id)
        # self.assertEqual(data["message"], "Password Changed Successfully!")
