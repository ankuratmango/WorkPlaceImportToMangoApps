from asyncio import constants
from functools import total_ordering
import sys
import os
from Constants.constants import Constants
import time
import csv
import json
from Helper.rest_client import RestClient
import pandas as pd
from Helper.mangoapps_rest_client import MangoAuth


def get_group_member_employee_ids(group_external_id):
    print("Get Members = " + str(group_external_id))
    mask = df_group_members.apply(lambda row: group_external_id in row.values, axis=1)
    employee_ids = df_group_members.loc[mask, 'EmployeeID']
    return employee_ids.astype(str).tolist()

def create_group(name, permission ,count = 0):
    privacy = "R"
    if(permission.upper() == "OPEN"):
        privacy = "P"
    group_data_response = mango_auth.create_group(token, name, privacy)
    if ("ms_errors" in group_data_response and 
        group_data_response['ms_errors']['errors']['error'][1]['field'].upper() == 'NAME'):
        new_name = name + "_" + str((count + 1))
        print("Update New Name = " + new_name)
        return create_group(new_name, permission, count + 1)
    return group_data_response;

def add_users_in_group(group_data, group_user_id_list, group_id):
    print("GROUP CREATED = " + group_data['GroupName']) 
    member_resp = mango_auth.add_users_in_group(token, group_id, group_user_id_list)
    if(member_resp['ms_response']['group_id'] == group_id):
        print("ADDED USERS IN GROUP = " + str(group_user_id_list))
        filename = Constants.ALL_MANGO_META_GROUP_ID
        df_group_mango_meta_id = pd.read_csv(filename)
        df_group_mango_meta_id.loc[df_group_mango_meta_id['mango_group_id'] == group_id, ['member']] = ['END']
        df_group_mango_meta_id.to_csv(filename, index=False)
        return group_id

def add_external_id_in_group(group_data, group_id, group_external_id):
    print("ADD EXTERNAL ID GROUP = " + group_data['GroupName']) 
    mango_auth.add_external_id_in_group(token, group_data, group_id, group_external_id)

def update_admin_group(mangoapps_users, group_external_id, group_id):
    df_all_group_admin = df_all_groups[['Team Admins', 'Group Id']]
    team_admins = df_all_group_admin.loc[df_all_group_admin['Group Id'] == group_external_id, 'Team Admins']
    all_success = False
    if(len(team_admins) > 0 and not team_admins.isna().any()):
        email_list = team_admins.iloc[0].split(' | ')
        all_success = False
        for email in email_list:
            print(email) 
            df_all_email_employeeid = df_all_users[['Email', 'EmployeeID']]
            employeeid = df_all_email_employeeid.loc[df_all_email_employeeid['Email'] == email, 'EmployeeID']
            if(len(employeeid) > 0):
                all_success = False
                admin_resp = mango_auth.add_admin_in_group(token, group_id, mangoapps_users[str(employeeid.iloc[0])]['id'])
                if('ms_response' in admin_resp and 
                    'conversation' in admin_resp['ms_response'] and 
                    'id' in admin_resp['ms_response']['conversation'] and 
                    admin_resp['ms_response']['conversation']['id'] == group_id) or \
                    ('ms_errors' in admin_resp and 
                    'error' in admin_resp['ms_errors'] and 
                    'error_code' in admin_resp['ms_errors']['error'] and 
                    admin_resp['ms_errors']['error']['error_code'] == 'ALREADY_ADMIN'):
                    all_success = True
                time.sleep(2)
    if(all_success == True or len(team_admins) == 0 or 
       not team_admins.isna().any() == False):
        filename = Constants.ALL_MANGO_META_GROUP_ID
        df_group_mango_meta_id = pd.read_csv(filename)
        df_group_mango_meta_id.loc[df_group_mango_meta_id['mango_group_id'] == group_id, ['admin']] = ['END']
        df_group_mango_meta_id.to_csv(filename, index=False)


def update_group_meta_mango_id(mango_id, meta_id):
    filename = Constants.ALL_MANGO_META_GROUP_ID
    df_group_mango_meta_id = pd.DataFrame(columns=["mango_group_id", "meta_group_id", "member", "admin", "post", "chat"])

    if os.path.exists(filename):
        df_group_mango_meta_id = pd.read_csv(filename)

    new_row = {
        'mango_group_id': mango_id,
        'meta_group_id': meta_id,
        'member': "START",
        'admin': "START",
        'post': "START",
        'chat': "START"
    }
    df_group_mango_meta_id = pd.concat([df_group_mango_meta_id, pd.DataFrame([new_row])], ignore_index=True)
    df_group_mango_meta_id.to_csv(filename, index=False)
    print(f"Added ({mango_id}, {meta_id}) to {filename}")


df_all_users = pd.read_csv(Constants.ALL_USER_DATA)
df_all_groups = pd.read_csv(Constants.ALL_GROUP_DATA)
df_group_members = pd.read_csv(Constants.ALL_GROUP_MEMBDER_DATA)

#----- GET MANGOAPPS AUTH -------
mango_auth = MangoAuth()
token = mango_auth.get_auth_token_by_api_key()

#-------- GET ALL MANGOAPPS USER DATA -------
mangoapps_users = mango_auth.get_all_users(token)
print(mangoapps_users)

df_group_mango_meta_id = {}
if os.path.exists(Constants.ALL_MANGO_META_GROUP_ID):
    df_group_mango_meta_id = pd.read_csv(Constants.ALL_MANGO_META_GROUP_ID)

#------ CREATE GROUP ------------
for index, row in df_all_groups.iterrows():
    print("----------- GROUP PROCESS START = " + str(index+1) + "/" + str(len(df_all_groups)))
    group_data = row.to_dict()
    group_external_id = group_data['Group Id']
    group_users_employee_ids = get_group_member_employee_ids(group_external_id)
    mango_group_if_exists = {}
    if(len(df_group_mango_meta_id) > 0):
        mango_group_if_exists = df_group_mango_meta_id.loc[df_group_mango_meta_id["meta_group_id"] == group_external_id]
    
    group_user_id_list = [str(mangoapps_users[user_employee_id]['id']) for user_employee_id in group_users_employee_ids if user_employee_id in mangoapps_users]
    group_id = ''
    if(len(mango_group_if_exists) == 0):
        group_data_response = create_group(group_data['GroupName'], group_data['Permission'])
        if (group_data_response and "ms_response" in group_data_response
        and "group" in group_data_response['ms_response']
        and "id" in group_data_response['ms_response']["group"]):
            group_id = group_data_response['ms_response']['group']['id']
            update_group_meta_mango_id(group_id, group_data['Group Id'])
            time.sleep(1)
        else:
            print(f"Error in Group Creation: Name = {group_data['GroupName']}")
            time.sleep(1)
    else:
        print("Group Already Available ID = " + str(mango_group_if_exists['mango_group_id'].values[0]));
        group_id = int(mango_group_if_exists['mango_group_id'].values[0])
    print("----------- GROUP COMPLETED = " + str(index+1) + "/" + str(len(df_all_groups)))
    
   
    #----- Update Members
    if(len(mango_group_if_exists) == 0 or mango_group_if_exists['member'].values[0] == "START"):
        add_users_in_group(group_data, group_user_id_list, group_id) 
        time.sleep(1)
    else:
        print("Members Already Added")
    #----- Updated Admins
    if(len(mango_group_if_exists) == 0 or mango_group_if_exists['admin'].values[0] == "START"):
        update_admin_group(mangoapps_users, group_external_id, group_id)
        time.sleep(1)
    else:
        print("Admins Already Added")
    





