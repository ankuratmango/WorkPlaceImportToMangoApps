from asyncio import constants
import sys
import os
from Constants.constants import Constants
import time
import json
from Helper.rest_client import RestClient
import pandas as pd
from Helper.mangoapps_rest_client import MangoAuth


df_all_users = pd.read_csv(Constants.ALL_USER_DATA)
df_all_groups = pd.read_csv(Constants.ALL_GROUP_DATA)
df_group_members = pd.read_csv(Constants.ALL_GROUP_MEMBDER_DATA)

#----- GET MANGOAPPS AUTH -------
mango_auth = MangoAuth()
token = mango_auth.get_auth_token()

for index, row in df_all_groups.iterrows():
    group_data = row.to_dict()
    print(group_data)