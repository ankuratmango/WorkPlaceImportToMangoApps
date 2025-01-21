from math import fabs
import sys
import os
import time
import json
from Constants.constants import Constants
from Helper.rest_client import RestClient
import base64

class MangoAuth:
    def __init__(self):
        self.api_client = RestClient(
            Constants.MANGOAPPS_URL, headers={"Content-Type": "application/json"}
        )

    def get_auth_token_by_api_key(self):
        payload = json.dumps(
            {
                "ms_request": {
                    "user": {
                        "api_key": Constants.MANGOAPPS_API_KEY,
                        "username": Constants.MANGOAPPS_USERNAME,
                        "password": Constants.MANGOAPPS_PASSWORD,
                    }
                }
            }
        )

        response = self.api_client.post(
            "/api/login.json",
            data=payload,
            headers={"Content-Type": "application/json"},
        )

        parsed_data = json.loads(response.content.decode("utf-8"))
        token = parsed_data["ms_response"]["user"]["_token"]
        return token

    def get_auth_token(self, user_id, pswd):
        payload = json.dumps(
            {
                "ms_request": {
                    "user": {
                        "api_key": "MangoMessenger",
                        "username": str(user_id),
                        "password": self.get_base64(pswd)
                    }
                }
            }
        )

        response = self.api_client.post(
            "/api/login.json",
            data=payload,
            headers={"Content-Type": "application/json"},
        )

        parsed_data = json.loads(response.content.decode("utf-8"))
        token = parsed_data["ms_response"]["user"]["session_id"]
        return token

    def create_group(self, token, name, privacy):
        payload = json.dumps(
            {
                "ms_request": {
                    "group": {
                        "description": name,
                        "name": name,
                        "privacy_type": privacy,  # P
                    }
                }
            }
        )

        headers = {
            "Content-Type": "application/json",
            "Cookie": "_felix_session_id=" + token,
        }

        response = self.api_client.post(
            "api/groups.json", data=payload, headers=headers
        )
        parsed_data = json.loads(response.content.decode("utf-8"))
        return parsed_data

    def get_all_users(self, token):
        limit = 500
        offset = 0
        employee_data = {}

        headers = {
            "Content-Type": "application/json",
            "Cookie": "_felix_session_id=" + token,
        }

        while True:
            response = self.api_client.get(
                f"/api/users.json?limit={limit}&offset={offset}", headers=headers
            )

            parsed_data = json.loads(response.content.decode("utf-8"))
            users = parsed_data["ms_response"].get("users", [])
            if not users:
                break

            for user in users:
                if user["employee_id"] is not None:
                    if user["employee_id"] not in employee_data:
                        employee_data[user["employee_id"]] = user
                    else:
                        print("Already Exists")
                else:
                    print("None Employee ID")
            offset += limit

        return employee_data

    def add_users_in_group(self, token, group_id, group_user_ids):
        payload = json.dumps(
            {
                "ms_request": {
                    "group": {"add_member_ids": group_user_ids, "generate_feed": "Y"}
                }
            }
        )

        headers = {
            "Content-Type": "application/json",
            "Cookie": "_felix_session_id=" + token,
        }

        response = self.api_client.put(
            "/api/groups/"
            + str(group_id)
            + "/members/manage.json?send_member_list=false",
            data=payload,
            headers=headers,
        )
        parsed_data = json.loads(response.content.decode("utf-8"))
        return parsed_data

    def add_admin_in_group(self, token, group_id, admin_id):
        payload = json.dumps(
            {
                "ms_request": {
                    "conversation": {
                        "team_admin_action": {
                            "user_id": str(admin_id),
                            "user_type": "G",
                        }
                    }
                }
            }
        )

        headers = {
            "Content-Type": "application/json",
            "Cookie": "_felix_session_id=" + token,
        }

        response = self.api_client.post(
            "/api/conversations/" + str(group_id) + "/manage.json",
            data=payload,
            headers=headers,
        )
        parsed_data = json.loads(response.content.decode("utf-8"))
        return parsed_data

    def post_feed_in_group(self, token, group_id, message):
        payload = json.dumps(
            {
                "ms_request": {
                    "feed": {
                        "attachments": [""],
                        "feed_type": "group",
                        "group_id": str(group_id),
                        "body": message,
                    }
                }
            }
        )

        headers = {
            "Content-Type": "application/json",
            "Cookie": "_felix_session_id=" + token,
        }

        response = self.api_client.post(
            "/api/feeds.json",
            data=payload,
            headers=headers,
        )
        parsed_data = json.loads(response.content.decode("utf-8"))
        return parsed_data

    def post_comment(self, token, feed_id, comment):
        payload = json.dumps({
          "ms_request": {
            "comment": {
              "body": comment
            }
          }
        })
        headers = {
          'Content-Type': 'application/json',
          'Cookie': "_felix_session_id=" + token,
        }

        response = self.api_client.post(
            "/api/feeds/" + str(feed_id) + "/comment.json",
            data=payload,
            headers=headers,
        )
        parsed_data = json.loads(response.content.decode("utf-8"))
        print(response.text)


    def post_reaction(self, token, feed_id, reaction):
        headers = {
          'Content-Type': 'application/json',
          'Cookie': "_felix_session_id=" + token,
        }

        response = self.api_client.post(
            "/api/feeds/" + str(feed_id) + "/like.json?type=" + reaction,
            headers=headers,
        )
        parsed_data = json.loads(response.content.decode("utf-8"))
        print(response.text)


    def get_base64(self, value):
        encoded_bytes = base64.b64encode(value.encode('utf-8'))
        encoded_string = encoded_bytes.decode('utf-8')
        return encoded_string