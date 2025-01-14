from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from meta_craft_be import settings
from .auth.auth import token_required
from .models import (
    Client,
    Otp,
    Service,
    Service_Provider,
    Sub_Service,
    Review,
    Gallery,
    Provider_Services_Rendered,
    Service_Request,
    format_data,
    format_sp_data,
    listToString,
)
from .CustomCode import validator, string_generator, password_functions, sms

from pysendpulse.pysendpulse import PySendPulse
import json
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


# @api_view(["POST"])
# def test_auth(request):
#     # print(request.META["HTTP_AUTHORIZATION"], "rereere")
#     return_data = {
#         "success": True,
#         "status": 200,
#     }
#     return Response(return_data)


@api_view(["POST"])
@token_required
def test_auth(request, payload):
    return_data = {"success": True, "status": 200, "payload": payload}
    return Response(return_data)


# SIGN UP API
@api_view(["POST"])
def signup(request):
    try:
        firstName = request.data.get("firstname", None).replace(" ", "").lower()
        lastName = request.data.get("lastname", None).replace(" ", "").lower()
        phoneNumber = request.data.get("phone", None).replace(" ", "").lower()
        email = request.data.get("email", None).replace(" ", "").lower()
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
                code = string_generator.numeric(5)
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
                    "role": role,
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
                        "isValidated": validated,
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


@api_view(["POST"])
@token_required
def verify(request, payload):
    try:
        code = request.data.get("code", None)
        user_id = payload["user_id"]
        validated = payload["validated"]
        role = payload["role"]

        reg_field = [code, user_id, validated]
        if not None in reg_field and not "" in reg_field:
            # get user info
            otpData = Otp.objects.get(user_id=user_id)
            if otpData.otp_code == code:
                otpData.validated = True
                otpData.save()
                return_data = {
                    "success": True,
                    "status": 200,
                    "role": role,
                    "code": code,
                    "reset": False,
                    "message": "Your Account is now Validated!",
                }
                return Response(return_data)
            elif otpData.password_reset_code == code:
                return_data = {
                    "success": True,
                    "status": 200,
                    "reset": True,
                    "role": role,
                    "message": "Kindly reset your password!",
                }
                return Response(return_data)
            else:
                return_data = {
                    "success": False,
                    "status": 422,
                    "message": "Wrong Code Entered. Try again!",
                }
                return Response(return_data)
        else:
            return_data = {
                "success": False,
                "status": 409,
                "message": "Kindly enter the codes sent to your email",
            }
            return Response(return_data)
    except Exception as e:
        return_data = {"success": False, "status": 502, "message": str(e)}
    return Response(return_data)


# RESEND VERIFICATION CODE API
@api_view(["POST"])
@token_required
def resend_code(request, payload):
    try:
        user_id = payload["user_id"]
        role = payload["role"]
        field = [user_id, role]
        if not None in field and not "" in field:
            # if User.objects.filter(user_id=user_id).exists():
            getOtp = Otp.objects.get(user_id=user_id)
            if role == "provider":
                userData = Service_Provider.objects.get(_id=user_id)
            else:
                userData = Client.objects.get(_id=user_id)
            firstName = userData.firstname
            code = getOtp.otp_code
            if code:
                # Resend mail using SMTP
                mail_subject = "Activate Code Sent again for your MetaCraft account."
                resentEmail = {
                    "subject": mail_subject,
                    "html": "<h4>Hello, "
                    + firstName
                    + "!</h4><p>Kindly find the Verification Code below sent again to activate your MetaCraft Account</p> <h1>"
                    + code
                    + "</h1>",
                    "text": "Hello, "
                    + firstName
                    + "!\nKindly find the Verification Code below sent again to activate your MetaCraft Account",
                    "from": {
                        "name": "MetaCraft",
                        "email": "donotreply@wastecoin.co",
                    },
                    "to": [{"name": firstName, "email": userData.email}],
                }
                SPApiProxy.smtp_send_mail(resentEmail)
                msg_body = (
                    "Kindly verify your MetaCraft account using this code: " + str(code)
                )
                phone = userData.phone
                send_sms = sms.send_sms(msg_body, phone)
                return_data = {
                    "success": True,
                    "status": 200,
                    "message": "Verfication Code sent again!",
                }
                return Response(return_data)
            else:
                return_data = {
                    "success": False,
                    "status": 422,
                    "message": "We could not retrieve your Verification Code. Kindly register!",
                }
                return Response(return_data)

    except Exception as e:
        return_data = {
            "success": False,
            "status": 502,
            "message": str(e)
            # "message": "Something went wrong!"
        }
    return Response(return_data)


# SIGNIN API
@api_view(["POST"])
def signin(request):
    try:
        email = request.data.get("email", None).replace(" ", "").lower()
        password = request.data.get("password", None)
        field = [email, password]
        if not None in field and not "" in field:
            validate_mail = validator.checkmail(email)
            if validate_mail == True:
                # print(Service_Provider.objects.filter(email=email).exists(), "chek")
                if (
                    Service_Provider.objects.filter(email=email).exists() == False
                    and Client.objects.filter(email=email).exists() == False
                ):
                    return_data = {
                        "success": False,
                        "status": 409,
                        "message": "User does not exist",
                    }
                else:
                    if Service_Provider.objects.filter(email=email).exists():
                        user_data = Service_Provider.objects.get(email=email)
                        role = "provider"
                    elif Client.objects.filter(email=email).exists():
                        user_data = Client.objects.get(email=email)
                        role = "client"
                    is_valid_password = password_functions.check_password_match(
                        password, user_data.password
                    )
                    validated = Otp.objects.get(user_id=user_data._id).validated
                    # Generate token
                    timeLimit = datetime.datetime.utcnow() + datetime.timedelta(
                        minutes=1440
                    )  # set limit for user
                    payload = {
                        "user_id": f"{user_data._id}",
                        "validated": validated,
                        "role": role,
                        "exp": timeLimit,
                    }
                    token = jwt.encode(payload, settings.SECRET_KEY)
                    # request.session['token'] = token.decode('UTF-8')
                    if is_valid_password and validated:
                        user = {
                            "name": str(user_data.firstname)
                            + " "
                            + str(user_data.lastname)
                        }
                        # services = Service.objects.all()
                        # formatted_services = [service.long() for service in services]
                        # service_requests = []
                        data = [user]
                        return_data = {
                            "success": True,
                            "status": 200,
                            "message": "Successfull",
                            "token": token,
                            "user_id": user_data._id,
                            "data": data,
                            "role": role,
                            "isValidated": validated,
                        }
                        # print(return_data, "return data")
                        return Response(return_data)
                    elif is_valid_password and validated == False:

                        getOtp = Otp.objects.get(user_id=user_data._id)
                        firstName = user_data.firstname
                        code = getOtp.otp_code
                        if code:
                            # Resend mail using SMTP
                            mail_subject = (
                                "Activate Code Sent again for your MetaCraft account."
                            )
                            resentEmail = {
                                "subject": mail_subject,
                                "html": "<h4>Hello, "
                                + firstName
                                + "!</h4><p>Kindly find the Verification Code below sent again to activate your MetaCraft Account</p> <h1>"
                                + code
                                + "</h1>",
                                "text": "Hello, "
                                + firstName
                                + "!\nKindly find the Verification Code below sent againto activate your MetaCraft Account",
                                "from": {
                                    "name": "MetaCraft",
                                    "email": "donotreply@wastecoin.co",
                                },
                                "to": [{"name": firstName, "email": user_data.email}],
                            }
                            SPApiProxy.smtp_send_mail(resentEmail)
                            msg_body = (
                                "Kindly verify your MetaCraft account using this code: "
                                + str(code)
                            )
                            phone = user_data.phone
                            send_sms = sms.send_sms(msg_body, phone)
                            return_data = {
                                "success": True,
                                "status": 200,
                                "message": "Verfication Code sent again!",
                            }
                            return Response(return_data)
                        return_data = {
                            "success": False,
                            "user_id": user_data._id,
                            "isValidated": validated,
                            "message": "User is not verified",
                            "status": 408,
                            "token": token,
                        }
                        return Response(return_data)

                    else:
                        return_data = {
                            "success": False,
                            "status": 409,
                            "message": "Wrong Password",
                        }
                        return Response(return_data)
            else:
                return_data = {
                    "success": False,
                    "status": 409,
                    "message": "Email is Invalid",
                }
                return Response(return_data)
        else:
            return_data = {
                "success": False,
                "status": 409,
                "message": "Invalid Parameters",
            }
            return Response(return_data)
    except Exception as e:
        return_data = {"success": False, "status": 502, "message": str(e)}
    return Response(return_data)


# SEND PASSWORD LINK (FOROGT PASSWORD PAGE) API
@api_view(["POST"])
def forgot_password(request):
    try:
        email = request.data.get("email", None).replace(" ", "").lower()

        field = [email]
        if not None in field and not "" in field:
            if (
                Client.objects.filter(email=email).exists() == True
                or Service_Provider.objects.filter(email=email).exists() == True
            ):
                # user_data = Client.objects.get(
                #     email=email
                # ) or Service_Provider.objects.get(email=email)
                if Service_Provider.objects.filter(email=email).exists():
                    user_data = Service_Provider.objects.get(email=email)
                    role = "provider"
                elif Client.objects.filter(email=email).exists():
                    user_data = Client.objects.get(email=email)
                    role = "client"

                getOtp = Otp.objects.get(user_id=user_data._id)
                # userData = User.objects.get(email = email)
                firstName = user_data.firstname
                # Generate reset OTP
                resetCode = string_generator.numeric(5)
                # Save reset OTP
                getOtp.password_reset_code = resetCode
                getOtp.save()

                if getOtp:
                    # Resend mail using SMTP
                    mail_subject = "Reset your MetaCraft account Password Confirmation."
                    resentEmail = {
                        "subject": mail_subject,
                        "html": "<h4>Hi, "
                        + firstName
                        + "!</h4><p>Kindly find the Reset Code below to confirm that intend to change your MetaCraft Account Password</p> <h1>"
                        + getOtp.password_reset_code
                        + "</h1>",
                        "text": "Hello, "
                        + firstName
                        + "!\nKindly find the Reset Code below to confirm that intend to change your MetaCraft Account Password",
                        "from": {
                            "name": "MetaCraft",
                            "email": "donotreply@wastecoin.co",
                        },
                        "to": [{"name": firstName, "email": email}],
                    }
                    SPApiProxy.smtp_send_mail(resentEmail)

                    phone = user_data.phone
                    msg_body = (
                        "Kindly verify your MetaCraft account using this code: "
                        + str(getOtp.password_reset_code)
                    )
                    send_sms = sms.send_sms(msg_body, phone)
                    # Get User Validation
                    validated = getOtp.validated
                    # Generate token
                    timeLimit = datetime.datetime.utcnow() + datetime.timedelta(
                        minutes=1440
                    )  # set duration for token
                    payload = {
                        "user_id": f"{user_data._id}",
                        "validated": validated,
                        "role": role,
                        "exp": timeLimit,
                    }
                    token = jwt.encode(payload, settings.SECRET_KEY)
                    return_data = {
                        "success": True,
                        "status": 200,
                        "token": token,
                        "user_id": user_data._id,
                        "message": "Reset Code sent!",
                    }
                    return Response(return_data)
                else:
                    return_data = {
                        "success": False,
                        "status": 422,
                        "message": "Sorry! try again",
                    }
                    return Response(return_data)
            elif validator.checkmail(email) == False:
                return_data = {
                    "success": False,
                    "status": 409,
                    "message": "Email is Invalid",
                }
                return Response(return_data)
            else:
                return_data = {
                    "success": False,
                    "status": 404,
                    "message": "Email does not exist in our database",
                }
                return Response(return_data)
        else:
            return_data = {
                "success": False,
                "status": 422,
                "message": "One or more fields is empty!",
            }
            return Response(return_data)
    except Exception as e:
        return_data = {
            "success": False,
            "status": 502,
            "message": str(e)
            # "message": "Something went wrong!"
        }
    return Response(return_data)


# CHANGE PASSWORD API
@api_view(["POST"])
@token_required
def change_password(request, payload):
    try:
        user_id = payload["user_id"]
        new_password = request.data.get("password", None)
        confirm_new_password = request.data.get("confirm_password", None)
        if Service_Provider.objects.filter(_id=user_id).exists():
            user_data = Service_Provider.objects.get(_id=user_id)
        elif Client.objects.filter(_id=user_id).exists():
            user_data = Client.objects.get(_id=user_id)

        if user_data:
            if new_password != confirm_new_password:
                return_data = {
                    "success": False,
                    "status": 409,
                    "message": "Password do not match!",
                }
                return Response(return_data)
            else:
                encryptpassword = password_functions.generate_password_hash(
                    new_password
                )
                user_data.password = encryptpassword
                user_data.save()
                return_data = {
                    "success": True,
                    "status": 200,
                    "message": "Password Changed Successfully!",
                }
                return Response(return_data)
        else:
            return_data = {
                "success": False,
                "status": 404,
                "message": "Sorry, You are not Authorized to access this link!",
            }
            return Response(return_data)
    except Exception as e:
        return_data = {
            "success": False,
            "status": 502,
            "message": str(e)
            # "message": 'Sorry, Something went wrong!'
        }
    return Response(return_data)


@api_view(["POST"])
@token_required
def get_sp(request, payload):
    coordinates = request.data.get("coordinates", None)
    service = request.data.get("service", None)
    try:
        user_id = payload["user_id"]
        client_data = Client.objects.get(_id=user_id)
        sp__id_by_services = Provider_Services_Rendered.objects.filter(
            service=service
        ).values("sp_id")

        serviceProviders = Service_Provider.objects.filter(
            state=client_data.state, _id__in=sp__id_by_services
        )
        selected_sp = format_sp_data(
            serviceProviders,
            float(coordinates["longitude"]),
            float(coordinates["latitude"]),
        )

        num = len(selected_sp)

        if num == 1:
            return_data = {
                "success": True,
                "status": 200,
                "serviceProviders": selected_sp,
            }
        if num <= 0:
            return_data = {
                "success": True,
                "status": 409,
                "message": "Oops! there are no Providers of "
                + service
                + " around you.",
            }
    except Exception as e:
        return_data = {"success": False, "status": 502, "message": str(e)}
    return Response(return_data)


@api_view(["POST"])
@token_required
def client_dashboard(request, payload):
    try:
        user_id = payload["user_id"]
        services = Service.objects.all()
        formatted_services = [service.long() for service in services]
        # ongoing = Service_Request.objects.filter(isCompleted=False, client_id=user_id).value('service')
        # ongoingServices = Service.objects.filter(service_name=ongoing.service)
        service_requests = []
        return_data = {
            "success": True,
            "status": 200,
            "ongoingData": service_requests,
            "requestData": formatted_services,
        }
    except Exception as e:
        return_data = {"success": False, "status": 502, "message": str(e)}
    return Response(return_data)


@api_view(["POST"])
@token_required
def accept_sp(request, payload):
    sp_id = request.data.get("sp_id", None)
    service = request.data.get("service", None)
    address = request.data.get("address", None)
    quantity = request.data.get("quantity", None)
    service_list = request.data.get("serviceList", None)
    amount = request.data.get("totalAmount", None)
    payment_mode = request.data.get("paymentMode", None)
    formated_service_list = listToString(service_list)

    try:
        user_id = payload["user_id"]

        # client_data = Client.objects.get(_id=user_id)
        newService = Service_Request(
            client_id=user_id,
            sp_id=sp_id,
            service=service,
            amount=amount,
            service_address=address,
            quantity=quantity,
            payment_mode=payment_mode,
            service_list=formated_service_list,
        )
        newService.save()
        sp_data = Service_Provider.objects.get(_id=sp_id)
        if newService:
            # Send mail using SMTP
            mail_subject = sp_data.firstname + "! MetaCraft Job/Service Update"
            email = {
                "subject": mail_subject,
                "html": "<h4>Hello, "
                + sp_data.firstname
                + "!</h4><p> You have a new Job/Service Request from a client. Kindly login to your dashboard and accept/Reject the Job/Service.</p>",
                "text": "Hello, "
                + sp_data.firstname
                + "!\n You have a new Job/Service Request from a client. Kindly login to your dashboard and accept/Reject the Job/Service",
                "from": {"name": "MetaCraft", "email": "donotreply@wastecoin.co"},
                "to": [{"name": sp_data.firstname, "email": sp_data.email}],
            }
            SPApiProxy.smtp_send_mail(email)

            msg_body = "You have a new Job/Service Request from a client. Kindly login to your dashboard and accept/Reject the Job/Service"
            phone = sp_data.phone
            send_sms = sms.send_sms(msg_body, phone)

            return_data = {
                "success": True,
                "status": 200,
                "service_request_id": newService.id,
            }
    except Exception as e:
        return_data = {"success": False, "status": 502, "message": str(e)}
    return Response(return_data)


@api_view(["POST"])
@token_required
def client_submit_report(request, payload):
    user_id = payload["user_id"]
    comment = request.data.get("comment", None)
    rating = request.data.get("rating", None)
    completion = request.data.get("completion", None)
    payment = request.data.get("payment", None)
    service_request_id = request.data.get("service_request_id", None)
    try:
        updateService = Service_Request.objects.get(id=int(service_request_id))
        if completion == "Yes":
            updateService.isCompleted = True
            updateService.save()
        if updateService.payment_mode == "cash" and payment == "Yes":
            updateService.client_paid = True
            updateService.save()
        # updateEscrow = Escrow.objects.get(job_id=int(job_id))
        # updateEscrow.isPaid = True
        # updateEscrow.save()

        sp_data = Service_Provider.objects.get(_id=updateService.sp_id)
        # sp_data.engaged = False
        # sp_data.save()
        newRatings = (sp_data.ratings + float(rating)) / 2
        sp_data.ratings = newRatings
        sp_data.save()
        newReview = Review(
            comment=comment,
            service_id=service_request_id,
            client_id=user_id,
            sp_id=sp_data._id,
        )
        newReview.save()
        # fees = updateService.amount * 0.9
        # if (
        #     updateService.payment_mode == "wallet"
        #     and updateService.sp_id != None
        #     or updateService.sp_id != ""
        # ):
        #     newClientBalance = sp_data.walletBalance + fees
        #     sp_data.walletBalance = newClientBalance
        #     sp_data.save()
        #     newTransaction = Transaction(
        #         from_id="MetaCraft",
        #         to_id=sp_data.user_id,
        #         transaction_type="Credit",
        #         transaction_message="Payment for Job order-" + job_id,
        #         amount=float(updateService.amount) * 0.9,
        #     )
        #     # newTransaction2 = Transaction(from_id=client_id, to_id="Vista", transaction_type="Debit", transaction_message="Payment for Job order-"+job_id, amount=float(updateService.amount))
        #     # newTransaction2.save()
        #     newTransaction.save()
        # if updateService and sp_data and updateService.payment_mode == "wallet":
        #     # Send mail using SMTP
        #     mail_subject = sp_data.firstname + "! MetaCraft Job/Service Update"
        #     email = {
        #         "subject": mail_subject,
        #         "html": "<h4>Hello, "
        #         + sp_data.firstname
        #         + "!</h4><p> Be kindly informed that the client have confirmed the Job Completion and you have been credited with the sum of NGN"
        #         + str(fees)
        #         + ". Please kindly check your wallet for your earnings</p>",
        #         "text": "Hello, "
        #         + sp_data.firstname
        #         + "!\n Be kindly informed that the client have confirmed the Job Completion and you have been credited with the sum of NGN"
        #         + str(fees)
        #         + ". Please kindly check your wallet for your earnings",
        #         "from": {"name": "MetaCraft", "email": "donotreply@wastecoin.co"},
        #         "to": [{"name": sp_data.firstname, "email": sp_data.email}],
        #     }
        #     SPApiProxy.smtp_send_mail(email)
        #     return_data = {
        #         "success": True,
        #         "status": 200,
        #     }
        # elif updateService and sp_data and updateService.payment_mode == "cash":
        #     sp_data2 = User.objects.get(user_id=sp_id)
        #     sp_data2.owingVistaCommission = True
        #     sp_data2.save()
        #     com = updateService.amount * 0.1
        #     newSPBalance = sp_data.walletBalance - com
        #     sp_data.walletBalance = newSPBalance
        #     sp_data.save()
        #     # Send mail using SMTP
        #     mail_subject = sp_data.firstname + "! MetaCraft Job/Service Update"
        #     email = {
        #         "subject": mail_subject,
        #         "html": "<h4>Hello, "
        #         + sp_data.firstname
        #         + "!</h4><p> Be kindly informed that the client have confirmed the Job Completion and you have collected the cash of sum of NGN"
        #         + str(updateService.amount)
        #         + ". The sum of "
        #         + str(com)
        #         + " has been deducted from your account. Kindly deposit that eaxct amount into your wallet to offset your debt. Your cooperation is highly appreciated. You wont be able to get another request until your debt is cleared. Thanks.</p>",
        #         "text": "Hello, "
        #         + sp_data.firstname
        #         + "!\n Be kindly informed that the client have confirmed the Job Completion and you have been credited with the sum of NGN"
        #         + str(updateService.amount)
        #         + ". The sum of "
        #         + str(com)
        #         + " has been deducted from your account. Kindly deposit that eaxct amount into your wallet to offset your debt. Your cooperation is highly appreciated. You wont be able to get another request until your debt is cleared. Thanks.",
        #         "from": {"name": "MetaCraft", "email": "donotreply@wastecoin.co"},
        #         "to": [{"name": sp_data.firstname, "email": sp_data.email}],
        #     }
        #     SPApiProxy.smtp_send_mail(email)
        #     return_data = {
        #         "success": True,
        #         "status": 200,
        #     }
    except Exception as e:
        return_data = {
            "success": False,
            "status": 201,
            "message": str(e),
            # "fees": fees,
            # "newBalance": newClientBalance
        }
    return Response(return_data)
