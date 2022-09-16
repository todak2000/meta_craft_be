from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from meta_craft_be import settings
from .auth.auth import token_required
from .models import Client, Otp, Service, Service_Provider, Sub_Service, Review, Gallery
from .CustomCode import validator, string_generator, password_functions, sms

from pysendpulse.pysendpulse import PySendPulse

from decouple import config
import datetime
import jwt
import requests

REST_API_ID = config("REST_API_ID")
REST_API_SECRET = config("REST_API_SECRET")
TOKEN_STORAGE = config("TOKEN_STORAGE")
MEMCACHED_HOST = config("MEMCACHED_HOST")
SPApiProxy = PySendPulse(
    REST_API_ID, REST_API_SECRET, TOKEN_STORAGE, memcached_host=MEMCACHED_HOST
)
# Create your views here.


@api_view(["GET"])
def index(request):
    return_data = {"success": True, "status": 200, "message": "Metacraft API home page"}
    return Response(return_data)


@api_view(["POST"])
@token_required
def test_auth(request, payload):
    return_data = {"success": True, "status": 200, "payload": payload}
    return Response(return_data)


# SIGN UP API
@api_view(["POST"])
def signup(request):
    try:
        firstName = request.data.get("firstname", None)
        lastName = request.data.get("lastname", None)
        phoneNumber = request.data.get("phone", None)
        email = request.data.get("email", None)
        password = request.data.get("password", None)
        role = request.data.get("role", None)
        reg_field = [firstName, lastName, phoneNumber, email, password, role]
        if not None in reg_field and not "" in reg_field:
            if (
                Client.objects.filter(phone=phoneNumber).exists()
                or Client.objects.filter(email=email).exists()
                or Service_Provider.objects.filter(phone=phoneNumber).exists()
                or Service_Provider.objects.filter(email=email).exists()
            ):
                return_data = {
                    "success": False,
                    "status": 409,  # conflict status
                    "message": "User Exists",
                }
            # elif (
            #     validator.checkmail(email)
            #     == False
            #     # or validator.checkphone(phoneNumber) == False
            # ):
            #     return_data = {
            #         "success": False,
            #         "status": 422,  # unprocessable entity
            #         "message": "Email or Phone number is Invalid",
            #     }
            else:
                # encrypt password
                encryped_password = password_functions.generate_password_hash(password)
                # generate user_id
                if role == "provider":
                    userRandomId = "SP" + string_generator.numeric(4)
                    # Save user_data
                    new_userData = Service_Provider(
                        _id=userRandomId,
                        firstname=firstName,
                        lastname=lastName,
                        email=email,
                        phone=phoneNumber,
                        password=encryped_password,
                    )
                    new_userData.save()
                else:
                    userRandomId = "CT" + string_generator.numeric(4)
                    # Save user_data
                    new_userData = Client(
                        _id=userRandomId,
                        firstname=firstName,
                        lastname=lastName,
                        email=email,
                        phone=phoneNumber,
                        password=encryped_password,
                    )
                    new_userData.save()

                # Generate OTP
                code = string_generator.numeric(6)
                # Save OTP
                user_OTP = Otp(user_id=userRandomId, otp_code=code)
                user_OTP.save()

                # add user to verification document model
                # newUserDoc = VerificationDocuments(user=new_userData)
                # newUserDoc.save()

                # Get User Validation
                validated = Otp.objects.get(user_id=userRandomId).validated
                # Generate token
                timeLimit = datetime.datetime.utcnow() + datetime.timedelta(
                    minutes=1440
                )  # set duration for token
                payload = {
                    "user_id": f"{userRandomId}",
                    "validated": validated,
                    "exp": timeLimit,
                }
                token = jwt.encode(payload, settings.SECRET_KEY)
                msg_body = (
                    "Kindly verify your MetaCraft account using this code: " + str(code)
                )
                phone = phoneNumber
                send_sms = sms.send_sms(msg_body, phone)
                # Send mail using SMTP
                mail_subject = "Activate your MetaCraft account."
                email = {
                    "subject": mail_subject,
                    "html": "<h4>Hello, "
                    + firstName
                    + "!</h4><p>Kindly use the Verification Code below to activate your MetaCraft Account</p> <h1>"
                    + code
                    + "</h1>",
                    "text": "Hello, "
                    + firstName
                    + "!\nKindly use the Verification Code below to activate your MetaCraft Account",
                    "from": {"name": "MetaCraft", "email": "donotreply@wastecoin.co"},
                    "to": [{"name": firstName, "email": email}],
                }
                sentMail = SPApiProxy.smtp_send_mail(email)
                if new_userData and user_OTP and sentMail or send_sms == 200:
                    return_data = {
                        "success": True,
                        "status": 200,
                        "message": "The registration was successful.",
                        "user_id": userRandomId,
                        "token": f"{token}",
                        "elapsed_time": f"{timeLimit}",
                    }
        else:
            return_data = {
                "success": False,
                "status": 422,
                "message": "Invalid Parameter",
            }
    except Exception as e:
        return_data = {"success": False, "status": 502, "message": str(e)}
    return Response(return_data)
