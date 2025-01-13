import sys
import os
import time
import json
from Constants.constants import Constants
from Helper.rest_client import RestClient

class MangoAuth:
    def __init__(self):
        self.api_client = RestClient(
            Constants.MANGOAPPS_URL,
            headers={"Content-Type": "application/json"}
        )

    def get_auth_token(self):
        payload = json.dumps({
            "ms_request": {
                "user": {
                    "api_key": Constants.MANGOAPPS_API_KEY,
                    "username": Constants.MANGOAPPS_USERNAME,
                    "password": Constants.MANGOAPPS_PASSWORD,
                }
            }
        })
        
        response = self.api_client.post(
            "/api/login.json",
            data=payload,
            headers={"Content-Type": "application/json"}
        )

        parsed_data = json.loads(response.content.decode('utf-8'))
        token = parsed_data['ms_response']['user']['_token']
        return token

    def create_group(self, token, name):
        payload = json.dumps({
           "ms_request": {
              "group": {
               "description": "group Description Here",
               "name": "groupFromApi_1122356"
            }
          }
        })

        headers = {
            'Content-Type': 'application/json',
            'Cookie': '_felix_session_id=' + token
        }

        response = self.api_client.post(
            "api/groups.json",
            data = payload,
            headers = headers
        )
        parsed_data = json.loads(response.content.decode('utf-8'))
        return parsed_data

    def get_all_users(self, token):
        limit = 500
        offset = 0
        employee_data = {}

        headers = {
            'Content-Type': 'application/json',
            'Cookie': '_felix_session_id=' + token
        }
        
        while True:
            response = self.api_client.get(
                f"/api/users.json?limit={limit}&offset={offset}",
                headers=headers
            )

            parsed_data = json.loads(response.content.decode('utf-8'))
            users = parsed_data["ms_response"].get("users", [])
            if not users:
                break

            for user in users:
                if user["employee_id"] is not None:
                    employee_data[user["employee_id"]] = user

            offset += limit

        return employee_data
