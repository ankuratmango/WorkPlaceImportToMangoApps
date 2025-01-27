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
from urllib.parse import urlparse
import datetime

since_date = '31-12-2020'
df_all_users = pd.read_csv(Constants.ALL_USER_DATA)
df_all_groups = pd.read_csv(Constants.ALL_GROUP_DATA)
df_group_members = pd.read_csv(Constants.ALL_GROUP_MEMBDER_DATA)
df_all_group_meta_mango = pd.read_csv(Constants.ALL_MANGO_META_GROUP_ID)

mango_meta_groupid = {}
mango_user_id_pswd = {}
mango_user_id_token = {}
mango_email_userid = {}
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

def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder created: {folder_path}")
    else:
        print(f"Folder already exists: {folder_path}")

def get_file_extension(url):
    parsed = urlparse(url)
    path = os.path.splitext(parsed.path)
    return path[1]


def get_datetime_unique_number():
    unique_number = int(time.time() * 1000)
    return int(unique_number)

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
    parsed_data = mango_auth.get_auth_data(user_email, mango_user_id_pswd[user_email])
    token = parsed_data["ms_response"]["user"]["session_id"]
    mango_email_userid[user_email] = parsed_data["ms_response"]["user"]["id"]
    if(token):
        mango_user_id_token[user_email] = token
    return token

token = mango_auth.get_auth_token_by_api_key()

def update_comment(mango_auth, mango_post, post_id, comment):
    comment_message = comment['message']
    comment_user_id = comment['from']['id']
    if(mango_post["ms_response"] and 
                       mango_post["ms_response"]['feeds'] and
                       mango_post["ms_response"]['feeds'][0] and
                       mango_post["ms_response"]['feeds'][0]["id"]):
        user_token = get_mango_token(comment_user_id)
        mango_auth.post_comment(user_token, post_id, comment_message)
        print("Comment Updated = " + str(comment_message))
        

def update_reaction_post(mango_auth, post_id, reaction):
    reaction_user_id = reaction['id']
    reaction_type = reaction['type']
    user_token = get_mango_token(reaction_user_id)
    mango_auth.post_reaction(user_token, post_id, reaction_type)
    print("Reaction Updated = " + str(reaction['type']) + " - " + str(reaction_user_id))

def get_post_message(post):
    if('story' in post and post['story']):
        message = post['story']
    if('message' in post and post['message']):
        message = post['message']
        print("Post Updated = " + message)
    return message


def get_attachments_urls():
    attachment_url = []
    if(post['type'].lower() == 'video'):
        attachment_url.append(post['source']);

    if('attachment' in post and len(post['attachment']) > 0):
        for attachment in post['attachment']:
            if('media' in attachment):
                if('image' in attachment['media']):
                    attachment_url.append(attachment['media']['image']['src']);
                if('video' in attachment['media']):
                    attachment_url.append(attachment['media']['video']['src']);

        if('subattachments' in attachment):
            for attachment in attachment['subattachments']['data']:
                if('url' in attachment):
                    attachment_url.append(attachment['url']);
                else:
                    if('image' in attachment['media']):
                        attachment_url.append(attachment['media']['image']['src']);
                    if('video' in attachment['media']):
                        attachment_url.append(attachment['media']['video']['src']);

def get_photo_attachments_urls(post):
    attachment_url = {}
    if('attachments' in post and len(post['attachments']) > 0):
        for attachment in post['attachments']['data']:
            if('media' in attachment):
                if('image' in attachment['media']):
                    attachment_url["image_1"] = attachment['media']['image']['src']
    return attachment_url

def get_status_attachments_urls(post):
    attachment_url = {}
    if(post['type'].lower() == 'video'):
        attachment_url['video'] = post['source'];

    if('attachment' in post and len(post['attachment']) > 0):
        for attachment in post['attachment']:
            if('media' in attachment):
                if('image' in attachment['media']):
                    attachment_url['file'] = attachment['media']['image']['src'];
                if('video' in attachment['media']):
                    attachment_url['file'] = attachment['media']['video']['src'];

        if('subattachments' in attachment):
            for attachment in attachment['subattachments']['data']:
                if('url' in attachment):
                    attachment_url['file'] = attachment['url'];
                else:
                    if('image' in attachment['media']):
                        attachment_url['file'] = attachment['media']['image']['src'];
                    if('video' in attachment['media']):
                        attachment_url['file'] = attachment['media']['video']['src'];
        return attachment_url

def get_attachment_ids(attachment_urls, mango_group_id, mango_user_id):
    attachment_ids = []
    for name,url in attachment_urls.items():
        file_extension = get_file_extension(url)
        filepath = os.path.join(
                Constants.DOWNLOAD_FOLDER_META, 
                f"file_{str(get_datetime_unique_number())}{file_extension}")
        mango_auth.download_image(url, filepath);
        if os.path.isfile(filepath):
            print("File Downloaded")
            print("Start Upload File to Mango")
        
        response = mango_auth.upload_file(token, filepath, mango_group_id, mango_user_id);
        parsed_data = json.loads(response.content.decode("utf-8"))
        attachment_ids.append(parsed_data['info'][0]['id'])
        print(name)
    return attachment_ids

def update_post(mango_auth, mango_group_id, post):
    try:
        time.sleep(2)
        message = ""
        meta_user_id = post['from']['id']
        message = get_post_message(post)
        user_token =  get_mango_token(meta_user_id)
        user_email = get_email_by_employee_id(df_all_users, meta_user_id)
        mango_user_id = mango_email_userid[user_email]
        attachment_ids = []
        create_folder(Constants.DOWNLOAD_FOLDER_META)
        if(post['type'].lower() == "photo"):
            attachment_urls = get_photo_attachments_urls(post)
            attachment_ids = get_attachment_ids(attachment_urls, mango_group_id, mango_user_id)
            print("Photo Post")
        elif(post['type'].lower() == "video"):
            attachment_urls = post['source']
            attachment_ids = get_attachment_ids(attachment_urls, mango_group_id, mango_user_id)
            print("Video Post")
        elif(post['type'].lower() == "status"):
            attachment_urls = get_status_attachments_urls(post)
            attachment_ids = get_attachment_ids(attachment_urls, mango_group_id, mango_user_id)
            print("Status Post")
        elif(post['type'].lower() == "link"):
            attachment_urls = get_status_attachments_urls(post)
            attachment_ids = get_attachment_ids(attachment_urls, mango_group_id, mango_user_id)
            print("Link Post")
        elif(post['type'].lower() == "event"):
            print("Event Post")
        elif(post['type'].lower() == "album"):
            print("Event Album")
      
        mango_post = mango_auth.post_feed_in_group(user_token, mango_group_id, message, attachment_ids)
        post_id = mango_post["ms_response"]['feeds'][0]["id"]
        if('reactions' in post and len(post['reactions']) > 0):
            for reaction in post['reactions']:
                update_reaction_post(mango_auth, post_id, reaction)
        if('comments' in post and len(post['comments']) > 0):
            for comment in post['comments']:
                if('message' in comment):
                    update_comment(mango_auth, mango_post, post_id, comment)
                    time.sleep(2)

    except Exception as exception:
        print(exception)

for index, row in df_all_groups.iterrows():
    data = row.to_dict()
    print(data)
    group_data = group_posts_detail.getGroupData(Constants.META_ACCESS_TOKEN, str(data['Group Id']))
    posts = group_posts_detail.processGroupPosts(Constants.META_ACCESS_TOKEN, group_data, since_date)
    mango_group_id = mango_meta_groupid[str(data['Group Id'])]
    for post in reversed(posts):
        try:
            if('attachment' in post and len(post['attachment']) > 0):#for testing
                update_post(mango_auth, mango_group_id, post)
        except Exception as exception:
            print(exception)


    