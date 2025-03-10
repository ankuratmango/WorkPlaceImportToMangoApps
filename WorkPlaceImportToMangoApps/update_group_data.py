from asyncio import constants
import sys
import os
from threading import ThreadError
from Constants.constants import Constants
import time
import json
import csv
from Helper.rest_client import RestClient
import pandas as pd
import Helper.group_posts_detail as group_posts_detail
from Helper.mangoapps_rest_client import MangoAuth
from urllib.parse import urlparse
from datetime import datetime, timedelta

#since_date = '31-12-2020'
df_all_users = pd.read_csv(Constants.ALL_USER_DATA)
df_all_groups = pd.read_csv(Constants.ALL_GROUP_DATA)
df_group_members = pd.read_csv(Constants.ALL_GROUP_MEMBDER_DATA)


mango_meta_groupid = {}
mango_user_id_pswd = {}
mango_user_id_token = {}
mango_email_userid = {}
mango_auth = MangoAuth()

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
        return "NONE"

def get_mango_token(meta_user_id):
    user_email = get_email_by_employee_id(df_all_users, meta_user_id)
    if(user_email != "NONE"):
        if(user_email in mango_user_id_token):
            return mango_user_id_token[user_email]
        parsed_data = mango_auth.get_auth_data(user_email, mango_user_id_pswd[user_email])
        token = parsed_data["ms_response"]["user"]["session_id"]
        mango_email_userid[user_email] = parsed_data["ms_response"]["user"]["id"]
        if(token):
            mango_user_id_token[user_email] = token
        return token
    return ""

token = mango_auth.get_auth_token_by_api_key()

def update_comment(mango_auth, mango_post, post_id, comment, parent_id = 0):
    comment_message = comment['message']
    if(len(comment_message) > 0):
        comment_user_id = comment['from']['id']
        if(mango_post["ms_response"] and 
                           mango_post["ms_response"]['feeds'] and
                           mango_post["ms_response"]['feeds'][0] and
                           mango_post["ms_response"]['feeds'][0]["id"]):
            user_token = get_mango_token(comment_user_id)
            print("Comment Updated = " + str(comment_message))
            return mango_auth.post_comment(user_token, post_id, comment_message, parent_id)
            
        
def update_reaction_post(mango_auth, post_id, reaction):
    reaction_user_id = reaction['id']
    reaction_type = reaction['type']
    user_token = get_mango_token(reaction_user_id)
    if(user_token):
        mango_auth.post_reaction(user_token, post_id, reaction_type)
        print("Reaction Updated = " + str(reaction['type']) + " - " + str(reaction_user_id))

def get_post_message(post):
    message = ""
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
                    if('media' in  attachment):
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

def update_into_mapping_feeds(mango_group_id, mango_post, post, meta_group_id):
    mango_post_time = datetime.utcfromtimestamp(int(mango_post["ms_response"]['feeds'][0]["updated_at"]))
    print("UTC Time:", mango_post_time.strftime('%Y-%m-%d %H:%M:%S UTC'))
    meta_post_time = datetime.strptime(post["updated_time"], "%Y-%m-%dT%H:%M:%S%z")

    mango_id = mango_post["ms_response"]['feeds'][0]["id"]
    meta_id = post["id"]

    group_feeds_file_name = str(mango_group_id) + "_" + str(meta_group_id) + ".csv"
    group_feeds_file_path = os.path.join(Constants.FOLDER_GROUPFEEDS, group_feeds_file_name)

    df_group_mango_meta_feed_id = pd.DataFrame(columns=["mango_id", "meta_id", "mango_time", "meta_time", "status","comments"])

    if os.path.exists(group_feeds_file_path):
        df_group_mango_meta_feed_id = pd.read_csv(group_feeds_file_path)

    if meta_id in df_group_mango_meta_feed_id['meta_id'].values:
        print(f"Meta ID {meta_id} already exists. No new row added.")
        return

    new_row = {
        'mango_id': mango_id,
        'meta_id': meta_id,
        'mango_time': mango_post_time,
        'meta_time': meta_post_time,
        'status': "START"
    }
    
    df_group_mango_meta_feed_id = pd.concat([df_group_mango_meta_feed_id, pd.DataFrame([new_row])], ignore_index=True)
    df_group_mango_meta_feed_id.to_csv(group_feeds_file_path, index=False)

def update_status_to_end(mango_group_id, mango_id, meta_id, meta_group_id, comments_ids):
    group_feeds_file_name = str(mango_group_id) + "_" + str(meta_group_id) + ".csv"
    group_feeds_file_path = os.path.join(Constants.FOLDER_GROUPFEEDS, group_feeds_file_name)
    df_group_mango_meta_feed_id = pd.read_csv(group_feeds_file_path)
    df_group_mango_meta_feed_id.loc[df_group_mango_meta_feed_id['mango_id'] == mango_id, ['status', 'comments']] = ['END', json.dumps(comments_ids)]
    df_group_mango_meta_feed_id.to_csv(group_feeds_file_path, index=False)
    print(f"Status updated to 'end' for Mango ID {mango_id}.")

def is_post_exist(mango_group_id, post, meta_group_id):
    meta_id = post["id"]
    meta_user_id = post['from']['id']
    group_feeds_file_name = str(mango_group_id) + "_" + str(meta_group_id) + ".csv"
    group_feeds_file_path = os.path.join(Constants.FOLDER_GROUPFEEDS, group_feeds_file_name)
    if os.path.exists(group_feeds_file_path):
        df_group_mango_meta_feed_id = pd.read_csv(group_feeds_file_path)
        if meta_id in df_group_mango_meta_feed_id['meta_id'].values:
            row = df_group_mango_meta_feed_id.loc[df_group_mango_meta_feed_id["meta_id"] == meta_id]
            status_value = row["status"].values[0] if not row.empty else None
            meta_post_time_last = datetime.fromisoformat(row["meta_time"].values[0])
            meta_post_time_latest = datetime.strptime(post["updated_time"], "%Y-%m-%dT%H:%M:%S%z")
            if(status_value == "START" or meta_post_time_latest != meta_post_time_last):
                #Mango Feed Delete Code
                mango_id =  row["mango_id"].values[0]
                user_token = get_mango_token(meta_user_id)
                mango_auth.delete_post(user_token, mango_id, mango_group_id)
                df_group_mango_meta_feed_id = df_group_mango_meta_feed_id[df_group_mango_meta_feed_id["meta_id"] != meta_id] 
                df_group_mango_meta_feed_id.to_csv(group_feeds_file_path, index=False)
            if(status_value == "END"):
                return True
    return False

def update_post_reaction(mango_auth, post, post_id):
    if('reactions' in post and len(post['reactions']) > 0):
        for reaction in post['reactions']:
            update_reaction_post(mango_auth, post_id, reaction)
            time.sleep(2)

def update_comment_reply(mango_auth, mango_post, post_id, comments_ids, comment, comment_resp):
    for comment_reply in comment['comments']['data']:
         comments_ids[comment_reply['id']] = comment_reply['created_time'] 
         update_comment(mango_auth, mango_post, post_id, comment_reply, comment_resp['ms_response']['comment']['id'])

def update_post(mango_auth, mango_group_id, post, meta_group_id):
    time.sleep(2)
    message = ""
    attachment_urls = {}
    meta_user_id = post['from']['id']
    message = get_post_message(post)
    user_token =  get_mango_token(meta_user_id)
    if(user_token == "NONE" or len(user_token) == 0):
        print("USER NOT FOUND IN MANGO")
        raise Exception("USER NOT FOUND IN MANGO")
    user_email = get_email_by_employee_id(df_all_users, meta_user_id)
    mango_user_id = mango_email_userid[user_email]
    attachment_ids = []
    create_folder(Constants.DOWNLOAD_FOLDER_META)
    if(post['type'].lower() == "photo"):
        attachment_urls = get_photo_attachments_urls(post)
        if(attachment_urls and len(attachment_urls)>0):
            attachment_ids = get_attachment_ids(attachment_urls, mango_group_id, mango_user_id)
        print("Photo Post")
    elif(post['type'].lower() == "video"):
        attachment_urls["video"] = post['source']
        if(attachment_urls and len(attachment_urls)>0):
            attachment_ids = get_attachment_ids(attachment_urls, mango_group_id, mango_user_id)
        print("Video Post")
    elif(post['type'].lower() == "status"):
        attachment_urls = get_status_attachments_urls(post)
        if(attachment_urls and len(attachment_urls)>0):
            attachment_ids = get_attachment_ids(attachment_urls, mango_group_id, mango_user_id)
        print("Status Post")
    elif(post['type'].lower() == "link"):
        attachment_urls = get_status_attachments_urls(post)
        if(len(attachment_urls) > 0):
            attachment_ids = get_attachment_ids(attachment_urls, mango_group_id, mango_user_id)
        print("Link Post")
    elif(post['type'].lower() == "event"):
        print("Event Post")
    elif(post['type'].lower() == "album"):
        print("Event Album")

    if(is_post_exist(mango_group_id, post, meta_group_id) == True):
        return

    if(len(message) > 0 or len(attachment_ids) > 0):
        if not message:
            message = post['type']
        mango_post = mango_auth.post_feed_in_group(user_token, mango_group_id, message, attachment_ids)
        post_id = mango_post["ms_response"]['feeds'][0]["id"]
            
        update_into_mapping_feeds(mango_group_id, mango_post, post, meta_group_id);
        update_post_reaction(mango_auth, post, post_id)
        comments_ids = {}
        if('comments' in post and len(post['comments']) > 0):
            for comment in post['comments']:
                if('message' in comment):
                    comments_ids[comment['id']] =comment['created_time'] 
                    comment_resp = update_comment(mango_auth, mango_post, post_id, comment)
                    if('comments' in comment and len(comment['comments']) > 0):
                        print("Reply In Comments")
                        update_comment_reply(mango_auth, mango_post, post_id, comments_ids, comment, comment_resp)
                    time.sleep(2)
        update_status_to_end(mango_group_id, post_id, post['id'], meta_group_id, comments_ids)

def check_date(last_date, current_date):
    last_update = datetime.strptime(last_date, "%d-%m-%Y")
    if last_update < current_date:
        return True
    return False

def update_post_group_time(mango_group_id, current_date, all_post_updated):
    if(all_post_updated == True):
        filename = Constants.ALL_MANGO_META_GROUP_ID
        df_group_mango_meta_id = pd.read_csv(filename)
        df_group_mango_meta_id.loc[df_group_mango_meta_id['mango_group_id'] == int(mango_group_id), ['post']] = [current_date.strftime("%d-%m-%Y")]
        df_group_mango_meta_id.to_csv(filename, index=False)

def check_update_post(mango_auth, update_post, mango_group_id, meta_group_id, posts):
    all_post_updated = True
    for post in reversed(posts):
        try:
            update_post(mango_auth, mango_group_id, post, meta_group_id)
        except Exception as exception:
            all_post_updated = False
            print(exception)
            break
    return all_post_updated

def start_update_post(mango_meta_groupid, mango_auth, update_post, check_date, update_post_group_time, check_update_post, data, data_days_per_batch, current_date, mango_group_if_exists):
    if(mango_group_if_exists['post'].values[0] == "START" or 
                    check_date(mango_group_if_exists['post'].values[0], current_date)):
        print(data)
        group_data = group_posts_detail.getGroupData(Constants.META_ACCESS_TOKEN, str(data['Group Id']))
        posts = group_posts_detail.processGroupPosts(Constants.META_ACCESS_TOKEN, group_data, 
                            current_date.strftime("%d-%m-%Y"), 
                            (current_date + timedelta(days=data_days_per_batch)).strftime("%d-%m-%Y"))
        mango_group_id = mango_meta_groupid[str(data['Group Id'])]
        meta_group_id = str(data['Group Id'])
        all_post_updated = check_update_post(mango_auth, update_post, mango_group_id, meta_group_id, posts)
        update_post_group_time(mango_group_id, current_date, all_post_updated)
    else:
        print("#-------------POSTS ALREADY CREATED--------------")

with open(Constants.ALL_MANGO_META_GROUP_ID, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)  
    for row in reader:
        mango_group_id = row['mango_group_id']
        meta_group_id = row['meta_group_id']
        mango_meta_groupid[meta_group_id] = mango_group_id

with open(Constants.ALL_MANGO_USER_ID_PSWD, mode='r') as file:
    reader = csv.reader(file)
    next(reader)
    for row in reader:
        key, value = row
        mango_user_id_pswd[key] = value

with open(Constants.SINCE_UNTIL_DATE_FILE, "r") as file:
    data = json.load(file)

since_date = datetime.strptime(data["since_date"], "%d-%m-%Y")
until_date = datetime.strptime(data["until_date"], "%d-%m-%Y")
data_days_per_batch = 1

#ignore_list = [1412403309212934, 2670655749898255]
#588447323888985, 1225491695279351,
ignore_list =[1003604680845459, 683794266600340, 693066472569014,
              3327576334156870, 855859935739661, 597681658792497, 680334146840275, 5961593197218391,
              927969741512288, 785900265831538, 470044731622027, 475179687979778, 883971562766228,
              3361835327382053, 465829044982370, 578988933803141, 737344630839806, 1412403309212934,
              1092471317986828, 444173807262481, 341853227750658, 239493118058165, 4597040463713861,
              2973005242954446, 405647357782615, 3170810336475591, 251904703414647, 671087450520603,
              972066943349971, 579208649955210, 270565461634046, 1045361812923418, 1220285855138416,
              4188813607913301, 3076519192593863, 3044345382487242, 3032934566959686, 1343383429410872,
              1245285202653823, 952887398628237, 914627555821561, 905556720339568, 883450445891390,
              881772592732873, 590631238739212, 568480764401998, 566290881349355, 537015447372925,
              371236531339462, 369807448215317, 340440071199285, 300636434727029, 289599869359783,
              220356160156428, 193648072852213, 171040701825965, 156779166649498, 152287970426641,
              132693762381068, 2670655749898255, 942124976570122, 568097734356556, 918451118737434,
              566030357901986, 500380054367287, 419163799575496, 717456189490594, 422599323417581,
              3280955308887569, 1133089240698702, 501525465189407, 1689101334822009, 431671232299688,
              405522091450195, 804988427045390]

os.makedirs(Constants.FOLDER_GROUPFEEDS, exist_ok=True)
df_group_mango_meta_id = {}

if os.path.exists(Constants.ALL_MANGO_META_GROUP_ID):
    df_group_mango_meta_id = pd.read_csv(Constants.ALL_MANGO_META_GROUP_ID)
    current_date = since_date
    while current_date <= until_date:
        print(current_date)  
        for index, row in df_all_groups.iterrows():
            data = row.to_dict()
            mango_group_if_exists = df_group_mango_meta_id.loc[df_group_mango_meta_id["meta_group_id"] == data['Group Id']]
            if(data['Group Id'] not in ignore_list):
                start_update_post(mango_meta_groupid, mango_auth, update_post, check_date, update_post_group_time, check_update_post, data, data_days_per_batch, current_date, mango_group_if_exists)
            else:
                print("#-------------GROUP IN IGNORE LIST--------------")
        current_date += timedelta(days=data_days_per_batch)
else:
    print("#-------------PLEASE CREATE GROUPS FIRST--------------")


    