from asyncio import constants
import sys
import os
from Constants.constants import Constants
import time
import json
from Helper.rest_client import RestClient
import pandas as pd
import Helper.group_posts_detail as group_posts_detail
from Helper.mangoapps_rest_client import MangoAuth

since_date = '31-12-2020'
df_all_users = pd.read_csv(Constants.ALL_USER_DATA)
df_all_groups = pd.read_csv(Constants.ALL_GROUP_DATA)
df_group_members = pd.read_csv(Constants.ALL_GROUP_MEMBDER_DATA)

#----- GET MANGOAPPS AUTH -------
# mango_auth = MangoAuth()
# token = mango_auth.get_auth_token()
first = True
for index, row in df_all_groups.iterrows():
    data = row.to_dict()
    print(data)
    group_data = group_posts_detail.getGroupData(Constants.META_ACCESS_TOKEN, str(data['Group Id']))
    data = group_posts_detail.processGroupPosts(Constants.META_ACCESS_TOKEN, group_data, since_date)
    print (data);
    group_posts_detail.exportToCSV(data, first);
    first = False


    