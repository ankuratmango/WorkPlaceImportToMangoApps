import sys
import os
from Constants.constants import Constants
import Helper.scim_agent as scim_agent
import Helper.export_user_data as export_user_data
import Helper.export_kl_category as export_kl_category
import Helper.workplace_etl_pipeline_xmlink as workplace_etl_pipeline_xmlink
import Helper.groups_categories as groups_categories
import csv
import time
import json

SCIM_URL = 'https://scim.workplace.com/'

file_name = "all_users_new.csv"
days = 30;
csv_data = []
group_members_data = {}

my_constant = Constants()
print(my_constant.GRAPH_URL_PREFIX)

#-----------------IMPORT USER------------------------
current_directory = os.getcwd()
output_file = current_directory + "\\importdata\\users.csv"

if os.path.exists(output_file):
    os.remove(output_file)
    print(f"Existing file '{output_file}' deleted.")

user_data = scim_agent.exportUsers(file_name, Constants.META_ACCESS_TOKEN, SCIM_URL);
print(user_data)

fields = ['Firstname', 'Lastname', 'Email', 'EmployeeID', 'Phone', 'Title', 'Enabled']
csv_data = []
assign_id = {}
uniqueNumber = int(time.time() * 1000)
for item in user_data:
    uniqueNumber = uniqueNumber + 1
    email = item.get('userName', '');
    if(len(email) == 0):
        email = item.get('id', '') #uniqueNumber
    csv_data.append({
        'Firstname': item.get('name', {}).get('givenName', ''),
        'Lastname': item.get('name', {}).get('familyName', ''),
        'Email': email,
        'EmployeeID': item.get('id', ''),#uniqueNumber, #item.get('id', ''),
        'Phone': '',  
        'Title': item.get('title', ''),
        'Enabled': item.get('active', False),
    })
    assign_id[item.get('id', '')] = item.get('id', '') #uniqueNumber

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


output_file = current_directory + "\\importdata\\groups.csv"
if os.path.exists(output_file):
    os.remove(output_file)
    print(f"Existing file '{output_file}' deleted.")

csv_data = []
fields = [
    'Group Image', 'GroupName', 'Group Id', 'Group External Id', 'State', 'Owner',
    'Permission', 'Modules', 'Show In Navigation', 'Team Admins', 'Automation Trigger',
    'Automation Rule', 'Admin Only Post', 'Admin Poll', 'Admin Update', 'Admin Questions',
    'Admin Events', 'LandingPage', 'Invite Network Users', 'Allow Join', 'Allow Guest User',
    'Categories', 'Files - Upload Settings', 'File Network Member Permission',
    'File Guest Member Permission', 'File Non Member Permission', 'Chat - Send IM',
    'Chat - Send Important messages'
]

all_group = workplace_etl_pipeline_xmlink.elt_main(Constants.META_ACCESS_TOKEN, days);
print(all_group)
for item in all_group:
    group_id = item['id']  
    members = workplace_etl_pipeline_xmlink.getGroupMembers(Constants.META_ACCESS_TOKEN, group_id)  
    group_members_data[group_id] = members 
    print(members)

for item in all_group:
    uniqueNumber = uniqueNumber + 1
    csv_data.append({
        'Group Image': 'https://firstconnect.firststudentinc.com/ce/pulse/images/default_images/group-250.png?',  
        'GroupName':  item.get('name', ''), #+ "," + str(uniqueNumber),#item.get('id', '')
        'Group Id': item.get('id', ''),
        'Group External Id': uniqueNumber,#item.get('id', ''),  
        'State': 'Active',
        'Owner': 'ankurt@mangospring.com',#getGroupOwner(item['id']),  
        'Permission': item.get('privacy', ''), 
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

with open(output_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()
    writer.writerows(csv_data)

print(f"Data has been written to {output_file}.")


# ------------- IMPORT GROUP MEMBERS --------------
user_group_mapping = {}

for group_id, user_list in group_members_data.items():
    for user in user_list:
        if(user["id"] in assign_id):
            user_id = assign_id[user["id"]]
            if user_id not in user_group_mapping:
                user_group_mapping[user_id] = []
            user_group_mapping[user_id].append(group_id)

max_groups = max(len(groups) for groups in user_group_mapping.values())
headers = ["EmployeeID"] + [f"Grouplevel{i+1}" for i in range(max_groups)]

csv_filename = current_directory + "\\importdata\\members.csv"
with open(csv_filename, mode="w", newline="", encoding="utf-8") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(headers)
    for user_id, groups in user_group_mapping.items():
        row = [user_id] + groups + ["" for _ in range(max_groups - len(groups))] 
        writer.writerow(row)

print(f"CSV file '{csv_filename}' has been created.")


# ------------- KNOWLEDGE LIBRARY --------------
def exportToFile(category_data, cid, cname):
    file_name = current_directory + "\\importdata\\categorie_" + cname + "_" + cid + ".txt"
    if os.path.exists(file_name):
        os.remove(file_name)
        print(f"Existing file '{file_name}' deleted.")
    f = open(file_name, 'w')
    f.write(json.dumps(category_data))
    f.close()

## START
all_categories = groups_categories.elt_main_categories(Constants.META_ACCESS_TOKEN, days);
#category_id = '371425217800259'
#category_id = '337195997889848'
for item in all_categories:
    category_data = export_kl_category.getCategoryDataById(Constants.META_ACCESS_TOKEN, item['id'])
    print (category_data)
    exportToFile(category_data, item['id'], item['title'])