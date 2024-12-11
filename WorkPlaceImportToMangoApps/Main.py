import sys
import os
from Constants.constants import Constants
import scim_agent
import export_user_data
import workplace_etl_pipeline_xmlink
import csv
import time

SCIM_URL = 'https://scim.workplace.com/'
access_token = "DQWRLZA29QUVprNDNaZAjk1d3ZAud2xPT0JmWmZAPVmhacXpXQ0daMGhBQ3YwamhhRU03LUxKNTJWbkdTTGlQWU5OLUtaX2RSOUJBdHJSd19nQWRzaTJWeGY4Y2p3QU95ZAkViZAHkwTGlIX3BUWmNkdnktRnNNUXpCSFFiTTllQVlkczdJNzRES1ByT2psN2pHTG55ekpVV1BHaEFlOW9YcjA0U3hpWGM1U0JIYnA5aFBHR3FZAeWZAlRFZAfTzFMdWdJY19jT0xjdG9xeTJVNDhSWUhjYktB" 
file_name = "all_users_new.csv"
days = 30;

#https://ankurqa.mangopulse.com/ce/pulse/admin/colleague/invite_colleagues

my_constant = Constants()
print(my_constant.GRAPH_URL_PREFIX)

#-----------------IMPORT USER------------------------

output_file = "C:\\Users\\Ankur\\Downloads\\importdata\\users.csv"

if os.path.exists(output_file):
    os.remove(output_file)
    print(f"Existing file '{output_file}' deleted.")

user_data = scim_agent.exportUsers(file_name, access_token, SCIM_URL);
print(user_data)

fields = ['Firstname', 'Lastname', 'Email', 'EmployeeID', 'Phone', 'Title', 'Enabled']
csv_data = []
uniqueNumber = int(time.time() * 1000)
for item in user_data:
    uniqueNumber = uniqueNumber + 1
    csv_data.append({
        'Firstname': item.get('name', {}).get('givenName', ''),
        'Lastname': item.get('name', {}).get('familyName', ''),
        'Email': item.get('userName', ''),
        'EmployeeID': uniqueNumber, #item.get('id', ''),
        'Phone': '',  
        'Title': item.get('title', ''),
        'Enabled': item.get('active', False)
    })

with open(output_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()
    writer.writerows(csv_data)

#-----------------IMPORT GROUPS------------------------

def getGroupOwner(group_id):
    members = group_members_data[group_id]  
    for member in members:
        if(member['administrator'] == True and 'email' in member):
            return member['email']

def getGroupAdmins(group_id):
    members = group_members_data[group_id]  
    admins = ''
    for member in members:
        if(member['administrator'] == True and 'email' in member):
            if(len(admins) == 0):
                admins = member['email']
            else:
                admins = admins + " | " + member['email']
    return admins

def add_single_quotes(value):
    return f"{value}"


output_file = "C:\\Users\\Ankur\\Downloads\\importdata\\groups.csv"
if os.path.exists(output_file):
    os.remove(output_file)
    print(f"Existing file '{output_file}' deleted.")

fields = [
    'Group Image', 'GroupName', 'Group Id', 'Group External Id', 'State', 'Owner',
    'Permission', 'Modules', 'Show In Navigation', 'Team Admins', 'Automation Trigger',
    'Automation Rule', 'Admin Only Post', 'Admin Poll', 'Admin Update', 'Admin Questions',
    'Admin Events', 'LandingPage', 'Invite Network Users', 'Allow Join', 'Allow Guest User',
    'Categories', 'Files - Upload Settings', 'File Network Member Permission',
    'File Guest Member Permission', 'File Non Member Permission', 'Chat - Send IM',
    'Chat - Send Important messages'
]
csv_data = []



group_members_data = {}
all_group = workplace_etl_pipeline_xmlink.elt_main(access_token, days);
print(all_group)
for item in all_group:
    group_id = item['id']  
    members = workplace_etl_pipeline_xmlink.getGroupMembers(access_token, group_id)  
    group_members_data[group_id] = members 
    print(members)

# with open(output_file, "a", encoding="utf-8") as file:
#     file.write('Group Image, GroupName, Group Id, Group External Id, State, Owner, Permission, Modules, Show In Navigation, Team Admins, Automation Trigger, Automation Rule, Admin Only Post, Admin Poll, Admin Update, Admin Questions,Admin Events, LandingPage, Invite Network Users, Allow Join, Allow Guest User,Categories, Files - Upload Settings, File Network Member Permission,File Guest Member Permission, File Non Member Permission, Chat - Send IM,Chat - Send Important messages, Firstname, Lastname, Email, EmployeeID,Phone, Title, Enabled')
#     file.write('\n')

for item in all_group:
    uniqueNumber = uniqueNumber + 1
    # with open(output_file, "a", encoding="utf-8") as file:
    #     if(getGroupOwner(item['id']) is not None):
    #         file.write("https://firstconnect.firststudentinc.com/ce/pulse/images/default_images/group-250.png?, \""+item.get('name', '')+", "+str(uniqueNumber)+"\",,"+str(uniqueNumber)+", Active, "+getGroupOwner(item['id'])+", Private, Newsfeed|Member|File|Post|Chat|Pages, Pages|Newsfeed|Member|File|Post|Calendar|Chat|Analytics|Media_gallery|Report|Tracker|Wiki|Idea, "+getGroupAdmins(item['id'])+", 8 Hours, <root><automations><rules><name>Cost Center ID</name><label>Cost Center ID</label><type>SLT</type><criteria>Equal To</criteria><value>23001</value><dimension>true</dimension></rules></automations></root>, TRUE, TRUE, TRUE, TRUE, TRUE, Pages, FALSE, TRUE, TRUE, Locations, Admin only, Viewer, No access, No access, Any Group Member, Domain Admins & Group Admins Only")
    #         file.write('\n')
    csv_data.append({
        'Group Image': 'https://firstconnect.firststudentinc.com/ce/pulse/images/default_images/group-250.png?',  
        'GroupName':  item.get('name', '') + "," + str(uniqueNumber),#item.get('id', '')
        'Group Id': '',
        'Group External Id': uniqueNumber,#item.get('id', ''),  
        'State': 'Active',
        'Owner': 'ankurt@mangospring.com',#getGroupOwner(item['id']),  
        'Permission': 'Private', 
        'Modules': 'Newsfeed|Member|File|Post|Chat|Pages',  
        'Show In Navigation': 'Pages|Newsfeed|Member|File|Post|Calendar|Chat|Analytics|Media_gallery|Report|Tracker|Wiki|Idea',  
        'Team Admins': getGroupAdmins(item['id']),  
        'Automation Trigger': '8 Hours',  
        'Automation Rule': '<root><automations><rules><name>Cost Center ID</name><label>Cost Center ID</label><type>SLT</type><criteria>Equal To</criteria><value>23001</value><dimension>true</dimension></rules></automations></root>',  
        'Admin Only Post': 'TRUE',  
        'Admin Poll': 'TRUE',  
        'Admin Update': 'TRUE',  
        'Admin Questions': 'TRUE',  
        'Admin Events': 'TRUE',  
        'LandingPage': 'Pages',  
        'Invite Network Users': 'FALSE',  
        'Allow Join': 'TRUE',  
        'Allow Guest User': 'TRUE',  
        'Categories': 'Locations',  
        'Files - Upload Settings': 'Admin only',  
        'File Network Member Permission': 'Viewer',  
        'File Guest Member Permission': 'No access	',  
        'File Non Member Permission': 'No access	',  
        'Chat - Send IM': 'Any Group Member',  
        'Chat - Send Important messages': 'Domain Admins & Group Admins Only'
    })

# Write data to CSV
# for line in csv_data:
#     with open(output_file, "w", encoding="utf-8") as file:
#         file.write(str(line))
#         file.write("\n")

with open(output_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()
    writer.writerows(csv_data)

print(f"Data has been written to {output_file}.")
