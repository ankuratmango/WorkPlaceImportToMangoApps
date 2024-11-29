import sys
from Constants.constants import Constants
import scim_agent
import export_user_data
import workplace_etl_pipeline_xmlink

SCIM_URL = 'https://scim.workplace.com/'
access_token = "DQWRLZA29QUVprNDNaZAjk1d3ZAud2xPT0JmWmZAPVmhacXpXQ0daMGhBQ3YwamhhRU03LUxKNTJWbkdTTGlQWU5OLUtaX2RSOUJBdHJSd19nQWRzaTJWeGY4Y2p3QU95ZAkViZAHkwTGlIX3BUWmNkdnktRnNNUXpCSFFiTTllQVlkczdJNzRES1ByT2psN2pHTG55ekpVV1BHaEFlOW9YcjA0U3hpWGM1U0JIYnA5aFBHR3FZAeWZAlRFZAfTzFMdWdJY19jT0xjdG9xeTJVNDhSWUhjYktB" 
file_name = "all_users_new.csv"
days = 30;

#https://ankurqa.mangopulse.com/ce/pulse/admin/colleague/invite_colleagues

my_constant = Constants()
print(my_constant.GRAPH_URL_PREFIX)

#-----------------IMPORT USER------------------------

#user_data = scim_agent.exportUsers(file_name, access_token, SCIM_URL);
#print(user_data)

#-----------------IMPORT GROUPS------------------------
group_members_data = {}
all_group = workplace_etl_pipeline_xmlink.elt_main(access_token, days);
print(all_group)
for item in all_group:
    group_id = item['id']  
    members = workplace_etl_pipeline_xmlink.getGroupMembers(access_token, group_id)  
    group_members_data[group_id] = members  
