import sys
import os
from Constants.constants import Constants
import time
import json
from Helper.rest_client import RestClient
import pandas as pd
from Helper.mangoapps_rest_client import MangoAuth


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
employee_data = mango_auth.get_all_users(token)
print(employee_data)

#------ CREATE GROUP ------------
for index, row in df_all_groups.iterrows():
    group_data = row.to_dict()
    data = mango_auth.create_group(token, group_data['GroupName'])
    print(data)
