#!/usr/bin/python3

import json
import os
import time
import requests
import time

FDROID_INDEX="https://f-droid.org/repo/index-v2.json"
PERSONALITY_API="https://localhost:8071/" # use localhost and ssh tunnel 
#TREE_ID=4074565107161372948
#TREE_ID=3393573391536046210
TREE_ID=2331682371050802309
VERIFY=False

def prepare_data_directory():
    current_time = time.strftime("%Y%m%d%H%M")
    data_directory = os.path.join("data", current_time)
    os.makedirs(data_directory, exist_ok = True)
    return data_directory


def load_fdroid_index(data_directory):
    result = requests.get(FDROID_INDEX)
    with open(data_directory + "/fdroid-index.json", "w") as fdroid_index:
        fdroid_index.write(result.text)
    return json.dumps(result.json())

def prepare_log_entries(json_data, data_directory):
    data = json.loads(json_data)
    print("Repository name: " + data["repo"]["name"]["en-US"])
    print("Repository url: " + FDROID_INDEX)
    print("---------------------------------------------")
    log_entries = []
    for (key, value) in data["packages"].items():
        package_name = str(key)
        for (key_version, value_version) in data["packages"][key]["versions"].items():
            package_hash = data["packages"][key]["versions"][key_version]["file"]["sha256"]
            package_version = data["packages"][key]["versions"][key_version]["manifest"]["versionName"]            
            #print(package_name)
            #print(package_version)
            #print(package_hash)            
            json_object = {"applicationId": package_name, "version": package_version, "signatureData": package_hash}
            json_result = json.dumps(json_object)
            log_entries.append(json_result)
    with open(data_directory + "/prepared_log_entries.json", "w") as file:
    #    for entry in log_entries:
        file.write(str(log_entries))
    return log_entries
    
def request_access_token():
    login_url = PERSONALITY_API + "Login/RequestAccessToken"
    with open('api_credentials.json') as credentials_file:
        credentials = json.load(credentials_file)
    response = requests.post(login_url,verify=VERIFY,json=credentials)
    if response.status_code != 200:
        print(f"[Error]: Request Access Token Status Code: {response.status_code}")
    return response.json()["token"]

def create_log_entries(access_token, log_entries):
    print("-----------------------------------------------")
    print("Started to create log entries...")
    print(datetime.now())
    print("-----------------------------------------------")
    create_log_url = PERSONALITY_API + "LogBuilder/AddLogEntry"
    tree_id_param = { 'treeId': TREE_ID}
    t = time.process_time()
    for logentry in log_entries:
        r = requests.post(create_log_url,verify=VERIFY,headers={'Authorization': 'Bearer {}'.format(access_token)},json=json.loads(logentry),params=tree_id_param)
        #print(r.status_code)
    elapsed_time = time.process_time() - t 
    print(datetime.now())
    print("Time elapsed: ",elapsed_time)

data_directory = prepare_data_directory()
fdroid_index_content = load_fdroid_index(data_directory)
#with open('index-v2.json') as local_file:
#  fdroid_index_content = json.dumps(json.load(local_file))
log_entries = prepare_log_entries(fdroid_index_content, data_directory)
print("# of unique packages: ",len(log_entries))
access_token = request_access_token()
create_log_entries(access_token,log_entries)
