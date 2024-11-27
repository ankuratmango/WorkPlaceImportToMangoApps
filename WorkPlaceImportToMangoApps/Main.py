import sys
from Constants.constants import Constants
import scim_agent
import export_user_data

SCIM_URL = 'https://scim.workplace.com/'
access_token = "DQWRLZA29QUVprNDNaZAjk1d3ZAud2xPT0JmWmZAPVmhacXpXQ0daMGhBQ3YwamhhRU03LUxKNTJWbkdTTGlQWU5OLUtaX2RSOUJBdHJSd19nQWRzaTJWeGY4Y2p3QU95ZAkViZAHkwTGlIX3BUWmNkdnktRnNNUXpCSFFiTTllQVlkczdJNzRES1ByT2psN2pHTG55ekpVV1BHaEFlOW9YcjA0U3hpWGM1U0JIYnA5aFBHR3FZAeWZAlRFZAfTzFMdWdJY19jT0xjdG9xeTJVNDhSWUhjYktB" 
file_name = "all_users_new.csv"

#https://ankurqa.mangopulse.com/ce/pulse/admin/colleague/invite_colleagues

my_constant = Constants()
print(my_constant.GRAPH_URL_PREFIX)

user_data = scim_agent.exportUsers(file_name, access_token, SCIM_URL);
print(user_data)
