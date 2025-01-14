import sys
import os
from Constants.constants import Constants
import time
import json
from Helper.rest_client import RestClient
import pandas as pd
from Helper.mangoapps_rest_client import MangoAuth


def get_group_member_employee_ids(group_external_id):
    print("Get Members = " + str(group_external_id))
    mask = df_group_members.apply(lambda row: group_external_id in row.values, axis=1)
    employee_ids = df_group_members.loc[mask, 'EmployeeID']
    return employee_ids.astype(str).tolist()

def create_group(name, count = 0):
    group_data_response = mango_auth.create_group(token, name)
    if ("ms_errors" in group_data_response and 
        group_data_response['ms_errors']['errors']['error'][1]['field'].upper() == 'NAME'):
        new_name = name + "_" + str((count + 1))
        print("Update New Name = " + new_name)
        return create_group(new_name, count + 1)
    return group_data_response;

def add_users_in_group(group_data, group_user_id_list, group_data_response):
    print("GROUP CREATED = " + group_data['GroupName']) 
    group_id = group_data_response['ms_response']['group']['id']
    mango_auth.add_users_in_group(token, group_id, group_user_id_list)
    print("ADDED USERS IN GROUP = " + str(group_user_id_list))
    return group_id

def update_admin_group(mangoapps_users, group_external_id, group_id):
    df_all_group_admin = df_all_groups[['Team Admins', 'Group External Id']]
    team_admins = df_all_group_admin.loc[df_all_group_admin['Group External Id'] == group_external_id, 'Team Admins']
    if(len(team_admins) > 0 and not team_admins.isna().any()):
        email_list = team_admins.iloc[0].split(' | ')
        for email in email_list:
            print(email) 
            df_all_email_employeeid = df_all_users[['Email', 'EmployeeID']]
            employeeid = df_all_email_employeeid.loc[df_all_email_employeeid['Email'] == email, 'EmployeeID']
            if(len(employeeid) > 0):
                mango_auth.add_admin_in_group(token, group_id, mangoapps_users[str(employeeid.iloc[0])]['id'])
                time.sleep(2)


all_users_data = "C:\\Users\\Ankur\\Downloads\\importdata\\users.csv"
all_groups_data = "C:\\Users\\Ankur\\Downloads\\importdata\\groups.csv"
all_group_members = "C:\\Users\\Ankur\\Downloads\\importdata\\members.csv"

df_all_users = pd.read_csv(all_users_data)
df_all_groups = pd.read_csv(all_groups_data)
df_group_members = pd.read_csv(all_group_members)

#----- GET MANGOAPPS AUTH -------
mango_auth = MangoAuth()
token = mango_auth.get_auth_token()

#-------- GET ALL MANGOAPPS USER DATA -------
mangoapps_users = mango_auth.get_all_users(token)
print(mangoapps_users)

#------ CREATE GROUP ------------
for index, row in df_all_groups.iterrows():
    group_data = row.to_dict()
    group_external_id = group_data['Group External Id']
    group_users_employee_ids = get_group_member_employee_ids(group_external_id)
    group_user_id_list = [str(mangoapps_users[user_employee_id]['id']) for user_employee_id in group_users_employee_ids]
    group_data_response = create_group(group_data['GroupName'])
    group_id = ''
    time.sleep(1)
    #----- Add Users in Group
    if ("ms_response" in group_data_response
        and "group" in group_data_response['ms_response']
        and "id" in group_data_response['ms_response']["group"]):
        group_id = add_users_in_group(group_data, group_user_id_list, group_data_response) 
        time.sleep(1)
    else:
        print(f"Error in Group Creation: Name = {group_data['GroupName']}")
    #----- Updated Admins
    update_admin_group(mangoapps_users, group_external_id, group_id)
    time.sleep(1)



