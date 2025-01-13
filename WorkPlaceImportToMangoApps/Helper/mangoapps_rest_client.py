import sys
import os
from Constants.constants import Constants
import time
import json
from Helper.rest_client import RestClient

def get_mango_auth():
    api_client = RestClient(Constants.MANGOAPPS_URL, headers={"Content-Type": "application/json"})
    payload = json.dumps({
      "ms_request": {
        "user": {
          "api_key": Constants.MANGOAPPS_API_KEY,
          "username": Constants.MANGOAPPS_USERNAME,
          "password": Constants.MANGOAPPS_PASSWORD,
        }
      }
    })
    response = api_client.post("/api/login.json", data=payload, headers={"Content-Type": "application/json"})
    parsed_data = json.loads(response.content.decode('utf-8'))
    token = parsed_data['ms_response']['user']['_token']
    return token