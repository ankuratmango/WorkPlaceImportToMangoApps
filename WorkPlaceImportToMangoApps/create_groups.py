from asyncio import constants
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
    mango_auth.add_users_in_group(token, group_id, group_user_id_list)
    print("ADDED USERS IN GROUP = " + str(group_user_id_list))
    return group_id

def add_external_id_in_group(group_data, group_id, group_external_id):
    print("ADD EXTERNAL ID GROUP = " + group_data['GroupName']) 
    mango_auth.add_external_id_in_group(token, group_data, group_id, group_external_id)

def update_admin_group(mangoapps_users, group_external_id, group_id):
    df_all_group_admin = df_all_groups[['Team Admins', 'Group Id']]
    team_admins = df_all_group_admin.loc[df_all_group_admin['Group Id'] == group_external_id, 'Team Admins']
    if(len(team_admins) > 0 and not team_admins.isna().any()):
        email_list = team_admins.iloc[0].split(' | ')
        for email in email_list:
            print(email) 
            df_all_email_employeeid = df_all_users[['Email', 'EmployeeID']]
            employeeid = df_all_email_employeeid.loc[df_all_email_employeeid['Email'] == email, 'EmployeeID']
            if(len(employeeid) > 0):
                mango_auth.add_admin_in_group(token, group_id, mangoapps_users[str(employeeid.iloc[0])]['id'])
                time.sleep(2)


def update_group_meta_mango_id(mango_id, meta_id):
    filename = Constants.ALL_MANGO_META_GROUP_ID
    file_exists = os.path.exists(filename)
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['mango_group_id', 'meta_group_id'])
        writer.writerow([mango_id, meta_id])
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

group_mango_meta_id = {}
if os.path.exists(Constants.ALL_MANGO_META_GROUP_ID):
    df = pd.read_csv(Constants.ALL_MANGO_META_GROUP_ID, usecols=['mango_group_id', 'meta_group_id'])
    group_mango_meta_id = df.set_index('mango_group_id')['meta_group_id'].to_dict()

#------ CREATE GROUP ------------
for index, row in df_all_groups.iterrows():
    group_data = row.to_dict()
    group_external_id = group_data['Group Id']
    group_users_employee_ids = get_group_member_employee_ids(group_external_id)
    mango_group_if_exists = [key for key, value in group_mango_meta_id.items() if value == group_external_id]
    
    group_user_id_list = [str(mangoapps_users[user_employee_id]['id']) for user_employee_id in group_users_employee_ids if user_employee_id in mangoapps_users]
    group_id = ''
    if(len(mango_group_if_exists) == 0  or 
       pd.isna(mango_group_if_exists[0]) or 
       len(mango_group_if_exists) == 0):
        group_data_response = create_group(group_data['GroupName'], group_data['Permission'])
        if (group_data_response and "ms_response" in group_data_response
        and "group" in group_data_response['ms_response']
        and "id" in group_data_response['ms_response']["group"]):
            group_id = group_data_response['ms_response']['group']['id']
            update_group_meta_mango_id(group_id, group_data['Group Id'])
            group_mango_meta_id[group_id] = group_data['Group Id']

        else:
            print(f"Error in Group Creation: Name = {group_data['GroupName']}")
            time.sleep(1)
    else:
        print("Group Already Available ID = " + str(mango_group_if_exists[0]));
        group_id = mango_group_if_exists[0]
    time.sleep(1)
   
    #----- Update Members
    add_users_in_group(group_data, group_user_id_list, group_id) 
    #----- Updated Admins
    update_admin_group(mangoapps_users, group_external_id, group_id)
    time.sleep(1)





