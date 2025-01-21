from asyncio import constants
import sys
import os
from Constants.constants import Constants
import time
import json
import csv
from Helper.rest_client import RestClient
import pandas as pd
import Helper.group_posts_detail as group_posts_detail
from Helper.mangoapps_rest_client import MangoAuth

since_date = '31-12-2020'
df_all_users = pd.read_csv(Constants.ALL_USER_DATA)
df_all_groups = pd.read_csv(Constants.ALL_GROUP_DATA)
df_group_members = pd.read_csv(Constants.ALL_GROUP_MEMBDER_DATA)
df_all_group_meta_mango = pd.read_csv(Constants.ALL_MANGO_META_GROUP_ID)

mango_meta_groupid = {}
mango_user_id_pswd = {}
mango_user_id_token = {}
mango_auth = MangoAuth()

# Open the file in read mode
with open(Constants.ALL_MANGO_META_GROUP_ID, mode='r') as file:
    reader = csv.reader(file)
    next(reader)
    for row in reader:
        key, value = row
        mango_meta_groupid[value] = key

# Open the file in read mode
with open(Constants.ALL_MANGO_USER_ID_PSWD, mode='r') as file:
    reader = csv.reader(file)
    next(reader)
    for row in reader:
        key, value = row
        mango_user_id_pswd[key] = value

#----- GET MANGOAPPS AUTH -------
def get_email_by_employee_id(df, employee_id):
    email = df.loc[df['EmployeeID'] == int(employee_id), 'Email'].values
    if len(email) > 0:
        return email[0]
    else:
        return "EmployeeID not found"

def get_mango_token(meta_user_id):
    user_email = get_email_by_employee_id(df_all_users, meta_user_id)
    if(user_email in mango_user_id_token):
        return mango_user_id_token[user_email]
    token = mango_auth.get_auth_token(user_email, mango_user_id_pswd[user_email])
    if(token):
        mango_user_id_token[user_email] = token
    return token

token = mango_auth.get_auth_token_by_api_key()

for index, row in df_all_groups.iterrows():
    data = row.to_dict()
    print(data)
    group_data = group_posts_detail.getGroupData(Constants.META_ACCESS_TOKEN, str(data['Group Id']))
    posts = group_posts_detail.processGroupPosts(Constants.META_ACCESS_TOKEN, group_data, since_date)
    mango_group_id = mango_meta_groupid[str(data['Group Id'])]
    for post in reversed(posts):
        message = ""
        meta_user_id = post['from']['id']
        if('story' in post and post['story']):
            message = post['story']
        if('message' in post and post['message']):
            message = post['message']
            print(post)
        user_token =  get_mango_token(meta_user_id)
        mango_post = mango_auth.post_feed_in_group(user_token, mango_group_id, message)
        post_id = mango_post["ms_response"]['feeds'][0]["id"]
        if('reactions' in post and len(post['reactions']) > 0):
            for reaction in post['reactions']:
                reaction_user_id = reaction['id']
                reaction_type = reaction['type']
                user_token = get_mango_token(reaction_user_id)
                mango_auth.post_reaction(user_token, post_id, reaction_type)
                print("")
        if('comments' in post and len(post['comments']) > 0):
            for comment in post['comments']:
                if('message' in comment):
                    comment_message = comment['message']
                    comment_user_id = comment['from']['id']
                    if(mango_post["ms_response"] and 
                       mango_post["ms_response"]['feeds'] and
                       mango_post["ms_response"]['feeds'][0] and
                       mango_post["ms_response"]['feeds'][0]["id"]):
                        user_token = get_mango_token(comment_user_id)
                        mango_auth.post_comment(user_token, post_id, comment_message)
                        print(comment)
    


    