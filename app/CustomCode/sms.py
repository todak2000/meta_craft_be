import requests
import json
from decouple import config


def send_sms(body, phone):
    url = "https://www.bulksmsnigeria.com/api/v2/sms/create"
    params = {
        "api_token": config("SMS_API_KEY"),
        "to": phone,
        "from": "Meta-Craft",
        "body": body,
        "gateway": "2",
        "append_sender": "0",
    }
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    response = requests.request("POST", url, headers=headers, params=params)
    response.json()
    # print(response.json(), "sms result")
    return response.status_code
