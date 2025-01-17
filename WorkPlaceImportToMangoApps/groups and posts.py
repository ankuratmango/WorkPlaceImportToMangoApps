import requests
import os
import csv
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path
import time
import logging
import json

# for current working directory use below function instead
#load_dotenv()
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=dotenv_path)

# Workplace graph API token
access_token = "DQWRLZA29QUVprNDNaZAjk1d3ZAud2xPT0JmWmZAPVmhacXpXQ0daMGhBQ3YwamhhRU03LUxKNTJWbkdTTGlQWU5OLUtaX2RSOUJBdHJSd19nQWRzaTJWeGY4Y2p3QU95ZAkViZAHkwTGlIX3BUWmNkdnktRnNNUXpCSFFiTTllQVlkczdJNzRES1ByT2psN2pHTG55ekpVV1BHaEFlOW9YcjA0U3hpWGM1U0JIYnA5aFBHR3FZAeWZAlRFZAfTzFMdWdJY19jT0xjdG9xeTJVNDhSWUhjYktB"
# Other ENV Variables
Days = ["15"]
data_for_how_many_days = int(Days[0])
LOGFILEPATH = "C:\\Users\\Ankur\\source\\repos\\WorkPlaceImportToMangoApps\\WorkPlaceImportToMangoApps"
logfilepath=os.getenv('LOGFILEPATH')
logfilename="workplace_etl_pipeline_production"+"_"+str("{:%Y_%m_%d_%H_%M_%S}".format(datetime.now()))+".log"
logfilepathandname= LOGFILEPATH+logfilename
headers = {"Authorization": f"Bearer {access_token}"}
print("------ 1")

#other variables
end_time = datetime.now()
start_time = end_time - timedelta(days=data_for_how_many_days)

# for ad-hoc run
# start_time = '2024-03-04 10:00:02.076580'
# end_time = '2024-03-06 10:00:02.076580'

try:
# logging default configurations
    logging.basicConfig(
        filename=logfilename,
        #filemode="a",
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s:%(message)s",
        datefmt="%Y-%m-%d %I:%M:%S%p",
    )
except Exception as e:
    print("------ Exception in logger")
    print(e)
#break

print("------ 2")

# Function to fetch all group IDs, handling pagination
def get_all_groups():
    url = "https://graph.facebook.com/community/groups?fields=id,cover,cover_url,description,icon,name,owner, privacy,purpose,join_setting,is_official_group&limit=100"
    #print(url)
    
    all_group = []
    logging.info('starting phase 1 of data extraction to fetch all group ids and associated metadata')
    #print("starting phase 1 of data extraction to fetch all group ids and associated metadata")
    page_number_groups = 0
    while url:
        page_number_groups = page_number_groups+1
        print(page_number_groups)
        if (page_number_groups%5==0):
            logging.info('on page number:'+str(page_number_groups))
        print("------- 3")    
        number_of_retries = 0
        response = https_get_call_handling_groups(url, headers, page_number_groups, number_of_retries)
        print(response)   
        status = response.status_code
        print(status)
        try: 
            json_output = response.json()
            #print(json_output)
        except Exception:
            logging.error('something wrong with parsing json',exc_info=True)
            print("------ Exception ")
        if status == 200:
            groups = json_output.get("data", [])
            all_group.extend(groups)
            # Check for pagination
            pagination = json_output.get("paging", {})
            next_url = pagination.get("next")
            url = next_url if next_url else None
            #print(url)
        elif status == 429:
            logging.info('sleeping for 30 seconds due to rate limit exceeding')
            time.sleep(30)
            response = https_get_call_handling_groups(url, headers, page_number_groups, number_of_retries)
            try: 
                json_output = response.json()
            except Exception:
                logging.error('something wrong with parsing json',exc_info=True)
            groups = json_output.get("data", [])
            all_group.extend(groups)
             # Check for pagination
            pagination = json_output.get("paging", {})
            next_url = pagination.get("next")
            url = next_url if next_url else None
        else: 
            logging.warn(str(status)+'exiting the loop early'+page_number_groups)
            break
       
    return all_group

# Creates arrays of arrays containing 50 ids each (can be reused for group ids or any ids)
def create_batches(ids):
    batches = []
    batch_size = 50
    for i in range(0, len(ids), batch_size):
        batches.append(ids[i:i+batch_size])
    return batches

def get_all_group_ids(all_group):
    group_ids = []
    for i in range(0, len(all_group)):
        group_ids.append(all_group[i]['id'])
    return group_ids

def make_batch_request(batch_payload, number_of_retries):
    try:
        response = requests.post(f'https://graph.facebook.com/?batch={batch_payload}&include_headers=false&access_token={access_token}', timeout=60)
        print('-----------------------')
        print(response)
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as e:
        number_of_retries = number_of_retries+1
        if number_of_retries <= 3:
            logging.warning(f'sleeping for 60 seconds and then retry making batch request - HTTP Error: {e}')
            time.sleep(60)
            response = make_batch_request(batch_payload, number_of_retries)
            return response
        else:
            logging.info('issue with batch request')
            logging.error("Http Error:", exc_info=True)
    except requests.exceptions.ConnectionError:
        number_of_retries = number_of_retries+1
        if number_of_retries <= 3:
            logging.warning(f'sleeping for 60 seconds and then retry making batch request - Connection Error')
            time.sleep(60)
            response = make_batch_request(batch_payload, number_of_retries)
            return response
        else:
            logging.info('issue with batch request')
            logging.error("Connection Error:", exc_info=True)
    except requests.exceptions.Timeout:
        number_of_retries = number_of_retries+1
        if number_of_retries <= 3:
            logging.warning(f'sleeping for 60 seconds and then retry making batch request - Timeout')
            time.sleep(60)
            response = make_batch_request(batch_payload, number_of_retries)
            return response
        else:
            logging.info('issue with batch request')
            logging.error("Timeout:", exc_info=True)
    except requests.exceptions.RequestException:
        number_of_retries = number_of_retries+1
        if number_of_retries <= 3:
            logging.warning(f'sleeping for 60 seconds and then retry making batch request - Request Exception')
            time.sleep(60)
            response = make_batch_request(batch_payload, number_of_retries)
            return response
        else:
            logging.info('issue with batch request')
            logging.error("Request Exception:", exc_info=True)

def get_all_subgroups(all_group):
    print("get_all_subgroups")
    logging.info('starting phase 2 of data extraction to fetch all sub-group ids and associated metadata')
    batches = create_batches(get_all_group_ids(all_group))
    print("--- 6")
    sub_groups = []
    for batch in batches:
        batch_payload = requests.utils.quote(
            json.dumps(
                [
                    {
                        "method": "GET",
                        "relative_url": f"{group_id}/groups?limit=100"
                    }
                    for group_id in batch
                ]
            )
        )
        #print(batch_payload)
        response = make_batch_request(batch_payload, 0)
        #print(response)
        logging.info(str(response))

        for group_num_in_batch, individual_response in enumerate(response.json()):
            # We need to retry individual responses within the batch of responses if the status code is not 200
            individual_response_retries = 0
            while individual_response.get('code') != 200:
                individual_response_retries = individual_response_retries + 1
                logging.warning('retrying individual response for group id: ' + str(batch[group_num_in_batch]))
                if individual_response_retries > 3:
                    logging.error('max retries reached for group id : ' + str(batch[group_num_in_batch]))
                    break

                batch_payload = requests.utils.quote(
                    json.dumps(
                        [
                            {
                                "method": "GET",
                                "relative_url": f"{batch[group_num_in_batch]}/groups?limit=100"
                            }
                        ]
                    )
                )
                individual_response = make_batch_request(batch_payload, 0).json()[0]
            
            body = json.loads(individual_response.get('body'))
            logging.info('response for group id ' + str(batch[group_num_in_batch]) + ': ' + str(body))
            logging.info('body.get(data) '+ str(body['data']) +" Length "+str(len(body['data'])))
            for item in body['data']:
                logging.info('Each data item of sub_group '+ item)
                sub_groups.append(item)

            if 'paging' in body and 'next' in body['paging']:
                logging.info('Paging for group id ' + str(batch[group_num_in_batch]))
                url = body['paging']['next']
                page_number_groups = 1
                while url:
                    #response = requests.get(url).json()
                    page_number_groups = page_number_groups + 1
                    response = https_get_call_handling_groups(url, {"Authorization": f"Bearer {access_token}"}, page_number_groups, 0).json()
                    logging.info('Paging response: ' + str(response))
                    for item in response.get('data'):
                        sub_groups.append(item)

                    if 'paging' in response and 'next' in response['paging']:
                        url = response['paging']['next']

                    else:
                        url = None

    logging.info('sub groups count: ' + str(len(sub_groups)))                    
    return sub_groups

def https_get_call_handling_groups(url, headers, page_number, number_of_retries):
    try:
        print("------ 3.1")
        retry = 1
        response = requests.get(url, headers=headers, timeout=60)
        print("------ 3.2")
        #print(response)
        response.raise_for_status()
        print("------ 4")
        return response
    except requests.exceptions.HTTPError:
        print("requests.exceptions.HTTPError")   
        number_of_retries = number_of_retries+1
        if number_of_retries <= retry:
            logging.warning('sleeping for 1 minute and get call to fetch group ids (HTTP error)')
            time.sleep(60)     
            return https_get_call_handling_groups(url, headers, page_number, number_of_retries)
        else:
            logging.info('page_number:'+str(page_number))
            logging.error("Http Error:", exc_info=True)  
    except requests.exceptions.ConnectionError:
        print("requests.exceptions.ConnectionError")  
        number_of_retries = number_of_retries+1
        if number_of_retries <= retry:
            logging.warning('sleeping for 1 minute and get call to fetch group ids (connection error)')
            time.sleep(60)
            return https_get_call_handling_groups(url, headers, page_number, number_of_retries)
        else:
            logging.info('page_number:'+str(page_number))
            logging.error("Error Connecting:",exc_info=True)
    except requests.exceptions.Timeout:
        print("requests.exceptions.Timeout")  
        number_of_retries = number_of_retries+1
        if number_of_retries <= retry:
            logging.warning('sleeping for 1 minute and get call to fetch group ids (timeout)')
            time.sleep(60)
            return https_get_call_handling_groups(url, headers, page_number, number_of_retries)
        else:
            logging.info('page_number:'+str(page_number))
            logging.error("Timeout Error:",exc_info=True)
    except requests.exceptions.RequestException:
        print("equests.exceptions.RequestException")  
        number_of_retries = number_of_retries+1
        if number_of_retries <= retry:
            logging.warning('sleeping for 1 minute and get call to fetch group ids (request exception)')
            time.sleep(60)
            return https_get_call_handling_groups(url, headers, page_number, number_of_retries)
        else:
            logging.info('page_number:'+str(page_number))
            logging.error("Something Other API error:",exc_info=True)
            print("------ 5")
    print(requests.exceptions)        

def https_get_call_handling_per_group(url, headers, group_id, number_of_retries):
    try:
        response = requests.get(url, headers=headers, timeout=60)
        status = response.status_code
        response.raise_for_status()
        return response, status
    except requests.exceptions.HTTPError:
        if response.status_code == 400 and "does not exist" in response.json().get("error", {})['message']:
            logging.warning(response.json().get("error", {})['message'])
            logging.info('group doesn''t exist anymore, so skipping group number'+str(group_id))
            response = {"data": []}
            #giving randon number not related to https requests
            status = None
            return  response, status
        elif response.status_code == 500 and "An unknown error has occurred" in response.json().get("error", {})['message']:
            logging.warning(response.json().get("error", {})['message'])
            logging.info('one of the graph end point has issues, so skipping group number:'+str(group_id))
            response = {"data": []}
            #giving randon number not related to https requests
            status = None
            return  response, status
        else: 
            number_of_retries = number_of_retries+1
            if number_of_retries <= 3:
                logging.warning('sleeping for 1 minute and get call to fetch group level information - HTTP Error')
                time.sleep(60)
                response,status = https_get_call_handling_per_group(url, headers, group_id, number_of_retries)
                status = response.status_code
                return response, status
            else:
                logging.info('error occured at group number:'+str(group_id))
                logging.error("Http Error:", exc_info=True)  
    except requests.exceptions.ConnectionError:
        number_of_retries = number_of_retries+1
        if number_of_retries <= 3:
            logging.warning('sleeping for 1 minute and get call to fetch group level information - Connection Error')
            time.sleep(60)
            response, status = https_get_call_handling_per_group(url, headers, group_id, number_of_retries)
            status = response.status_code
            return response, status
        else:
            logging.info('error occured at group number:'+str(group_id))
            logging.error("Error Connecting:",exc_info=True)
    except requests.exceptions.Timeout:
        number_of_retries = number_of_retries+1
        if number_of_retries <= 3:
            logging.warning('sleeping for 1 minute and get call to fetch group level information - Timeout')
            time.sleep(60)
            response, status = https_get_call_handling_per_group(url, headers, group_id, number_of_retries)
            status = response.status_code
            return response, status
        else:
            logging.info('error occured at group number:'+str(group_id))
            logging.error("Timeout Error:",exc_info=True)
    except requests.exceptions.RequestException:
        number_of_retries = number_of_retries+1
        if number_of_retries <= 3:
            logging.warning('sleeping for 1 minute and get call to fetch group level information - Request Exception')
            time.sleep(60)
            response, status = https_get_call_handling_per_group(url, headers, group_id, number_of_retries)
            status = response.status_code
            return response, status
        else:
            logging.info('error occured at group number:'+str(group_id))
            logging.error("Something Other API error:",exc_info=True)

'''
In this function, a batch of 50 group objects is the input. A batch of requests is made to Meta to get the post feeds.
Another key is added to each group object which is a array to store the posts for each group.
This enhance group object is then sent into the load_group function, which loads each post for the group to the project
'''
def get_group_batch_data(batch, group_type):
    logging.info('In get_group_batch_data ------ ')
    print('In get_group_batch_data ------ ')
    #post_url=  "https://graph.facebook.com/"+f"{group['id']}/feed?fields=id, created_time, formatting, from{{email, title, name, id, primary_address, department, locale, link}}, icon, link, name, place, poll, properties, status_type, story, to, updated_time, with_tags, type, picture, object_id, message,permalink_url, created_time,comments{{id,from{{email, title, name, id, primary_address, department, locale, link}},object_id, message,comments{{id,from{{email, title, name, id, primary_address, department, locale, link}},message, object_id, permalink_url, created_time}} ,permalink_url, created_time}}&since={start_time}&until={end_time}"
    #print('url ------ '+post_url)
    batch_payload = requests.utils.quote(
        json.dumps(
            [
                {
                    "method": "GET",
                    "relative_url": f"{group['id']}/feed?fields=id,attachments,created_time, formatting, from{{email, title, name, id, primary_address, department, locale, link}}, icon, link, name, place, poll{{options,votes}}, properties, status_type, story, to, updated_time, with_tags, type, picture, object_id, message,permalink_url,comments{{id,from{{email, title, name, id, primary_address, department, locale, link}},object_id, message,comments{{id,from{{email, title, name, id, primary_address, department, locale, link}},message, object_id, permalink_url, created_time}} ,permalink_url, created_time}}&since={start_time}&until={end_time}"
                }
                for group in batch
            ]
        )
    )

    print(batch_payload)
   # print('requests.utils ------ '+ str(requests.utils.get('relative_url')))

    response = make_batch_request(batch_payload, 0)
    #response = requests.get(post_url, headers=headers, timeout=60)
  #  print('response:' + str(response))
    logging.info('batch request response: ' + str(response.status_code))
    for group_num_in_batch, individual_response in enumerate(response.json()):
        #print('---------------ha')
        #print(individual_response.get('code'))
        # We need to retry individual responses within the batch of responses if the status code is not 200
        individual_response_retries = 0
        while individual_response.get('code') != 200:
            #print('failed------')
            individual_response_retries = individual_response_retries + 1
            logging.warning('retrying individual response for group id: ' + str(batch[group_num_in_batch]['id']))
            if individual_response_retries > 3:
                logging.error('max retries reached for group id : ' + str(batch[group_num_in_batch]['id']))
                break

            batch_payload = requests.utils.quote(
                json.dumps(
                    [
                        {
                            "method": "GET",
                            "relative_url": f"{batch[group_num_in_batch]['id']}/feed?fields=id,attachments,created_time, formatting, from{{email, title, name, id, primary_address, department, locale, link}},icon, link, name, place, poll, properties, status_type, story, to, updated_time, with_tags, type,picture, object_id, message,permalink_url,comments{{id,from{{email, title, name, id, primary_address, department, locale, link}}, object_id, message,comments{{id,from{{email, title, name, id, primary_address, department, locale, link}}, object_id, message, permalink_url, created_time}} ,permalink_url, created_time}}&since={start_time}&until={end_time}"
                        }
                    ]
                )
            )
            individual_response = make_batch_request(batch_payload, 0).json()[0]
            print('individual_response '+ str(individual_response))
        body = json.loads(individual_response.get('body'))
        logging.info('response for group id ' + str(batch[group_num_in_batch]['id']) + ': ' + str(body))
        batch[group_num_in_batch]['posts'] = []
        logging.info('get_group_batch_data :: body.get(data) ' + str(body.get('data')))
        for item in body.get('data'):
            batch[group_num_in_batch]['posts'].append(item)

        

        if 'paging' in body and 'next' in body['paging']:
            logging.info('Paging for group id ' + str(batch[group_num_in_batch]['id']))
            url = body['paging']['next']
            while url:
                #response = requests.get(url).json()
                response_json, status = https_get_call_handling_per_group(url, {"Authorization": f"Bearer {access_token}"}, batch[group_num_in_batch]['id'], 0)
                response = response_json.json()
                logging.info('Paging response: ' + str(response))
                for item in response.get('data'):
                    batch[group_num_in_batch]['posts'].append(item)

                if 'paging' in response and 'next' in response['paging']:
                    url = response['paging']['next']

                else:
                    url = None
    batch_messages_processed = 0
    batch_messages_extracted = 0
    #print('before for loop ', str(batch))
    with open('posts.json', 'w') as json_file:
        json.dump(batch, json_file, indent=4)
    for group in batch:
        #print('in for loop ', group)
        group_messages_processed, group_messages_extracted = load_group(group, group_type)
        print('in for loop group_messages_extracted ', group_messages_extracted)
        print('in for loop group_messages_processed ', group_messages_processed)
        batch_messages_processed = batch_messages_processed + group_messages_processed
        batch_messages_extracted = batch_messages_extracted + group_messages_extracted

    
    return batch_messages_processed, batch_messages_extracted

# Write data directly to a CSV file
def exporting_from_workplace_to_project(all_group, group_type):
    logging.info(f'starting next phase of data extraction, to fetch information from each {group_type}')
    #print("tarting next phase of data extraction, to fetch information from each"+str({group_type})
    logging.info('total_groups:'+str(len(all_group)))
    print(len(all_group))
    group_batches = create_batches(all_group)
    total_count_messages_extracted=0
    total_count_messages_processed=0
    total_count_groups_processed=0
    for batch in group_batches:
        batch_messages_processed, batch_messages_extracted = get_group_batch_data(batch, group_type)
        total_count_messages_extracted = total_count_messages_extracted + batch_messages_extracted
        total_count_messages_processed = total_count_messages_processed + batch_messages_processed
        total_count_groups_processed = total_count_groups_processed + len(batch)
        logging.info('batch complete, total groups processed: ' + str(total_count_groups_processed))

    logging.info('total_count_messages_extracted:'+str(total_count_messages_extracted))
    logging.info('total_count_messages_processed:'+str(total_count_messages_processed))


def elt_main():
    logging.info('Date Range: ' + str(start_time) + ' to ' + str(end_time))
    all_group = get_all_groups()
    # Use this if you don't want to get all groups via the API and instead read from the file
    '''
    with open("all_group.json", "r") as file:
        all_group = json.load(file)
    '''
    with open("all_group.json", "w") as outfile: 
        json.dump(all_group, outfile)
    
    all_sub_groups = get_all_subgroups(all_group)
    # Use this if you don't want to get all sub-groups via the API and instead read from the file
    '''
    with open("all_sub_groups.json", "r") as file:
        all_sub_groups = json.load(file)
    '''
    #with open("all_sub_groups.json", "w") as outfile:
        #json.dump(all_sub_groups, outfile)

    exporting_from_workplace_to_project(all_group, "group")
    exporting_from_workplace_to_project(all_sub_groups, "sub-group")

try:
    elt_main()
except Exception:
    logging.error('something went wrong with the script',exc_info=True)
    #print("something went wrong with the script")
