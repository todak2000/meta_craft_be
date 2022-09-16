from rest_framework.response import Response
from rest_framework import status
import jwt
from meta_craft_be import settings

error_code = 401


def get_token_auth_header(request):
    auth = request.META["headers"]["Authorization"]

    if not auth:
        error = {
            "success": False,
            "status_code": error_code,
            "description": "Authorization header is expected.",
        }
        return Response(error, status=error_code)
    parts = auth.split()
    if parts[0].lower() != "bearer":
        error = {
            "success": False,
            "status_code": error_code,
            "message": 'Authorization header must start with "Bearer".',
        }
        return Response(error, status=error_code)
    elif len(parts) == 1:
        error = {
            "status_code": error_code,
            "message": "invalid_header",
            "success": False,
        }
        return Response(error, status=error_code)
    elif len(parts) > 2:
        error = {
            "status_code": error_code,
            "message": "Authorization header must be bearer token.",
            "success": False,
        }
        return Response(error, status=error_code)
    token = parts[1]

    return token


def verify_decode_jwt(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        error = {
            "status_code": error_code,
            "message": "Token expired",
            "success": False,
        }
        return Response(error, status=error_code)
    except Exception as e:
        error = {"status_code": error_code, "message": str(e), "success": False}
        return Response(error, status=error_code)


def token_required(something):
    def wrap(request):
        try:
            token = get_token_auth_header(request)

            if token:
                try:
                    payload = verify_decode_jwt(token)
                    return something(request, payload)
                except jwt.exceptions.ExpiredSignatureError:
                    return_data = {
                        "success": False,
                        "message": "Token has expired",
                        "status_code": error_code,
                    }
                    return Response(return_data, status=error_code)
                except Exception as e:
                    return_data = {
                        "success": False,
                        "message": str(e),
                        "status_code": error_code,
                    }
                    return Response(return_data, status=error_code)
            else:
                return_data = {
                    "success": False,
                    "message": "Token required",
                    "status_code": error_code,
                }
                return Response(return_data, status=error_code)
        except Exception as e:
            return_data = {
                "success": False,
                "message": str(e),
                "status_code": error_code,
            }
            return Response(return_data, status=error_code)

    return wrap
