from django.test import TestCase
from decouple import config
import unittest
import json
import os
import datetime

# from flask_sqlalchemy import SQLAlchemy
from app.CustomCode import string_generator
import app

from .models import Service_Provider, Client
import jwt

# Create your tests here.


class MetaCraftTestCase(TestCase):
    def setUp(self):
        return
        # Animal.objects.create(name="lion", sound="roar")
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
            headers={"Authorization": "Bearer " + str(token)},
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
        # print(data, "dataa")
        if new_user["role"] == "provider":
            user = Service_Provider.objects.get(id=1)
        else:
            user = Client.objects.get(id=1)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["user_id"], user._id)

    def test_verify(self):  # Generate token
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
        code = string_generator.numeric(5)
        res = self.client.post(
            "/verify-user",
            headers={"Authorization": "Bearer " + str(token)},
            data={"code": code},
        )

        # res = self.client.post(
        #     "/signup",
        #     new_user,
        # )
        init = json.dumps(res.data)
        data = json.loads(init)
        # print(data, "dataa")
        # if new_user["role"] == "provider":
        #     user = Service_Provider.objects.get(id=1)
        # else:
        #     user = Client.objects.get(id=1)
        self.assertEqual(res.status_code, 200)
        # self.assertEqual(data["success"], True)
        # self.assertEqual(data["user_id"], user._id)
