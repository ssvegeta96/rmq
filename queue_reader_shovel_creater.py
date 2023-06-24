import requests
import json
import re
import csv
from datetime import datetime
import sys


# Set the RabbitMQ API endpoint
RMQ1 = "192.168.1.111"
RMQ2 = "192.168.1.222"

REPO = '/home/test/pyapp/gui/test'
# Set the RabbitMQ credentials
'''
alaternativly you call for user intput here to avoid sotring passwod in scripts

uname = input('username: ')
and getpass.getpass for the password to store it securly after taking the users reponse
'''
username = "admin"
password = "password"

queue_name = 'copy'
vhost = 'VHOST'

payload = {"value":{"src-protocol":"amqp091","src-uri":f"amqp://{username}:{password}@{RMQ1}/{vhost}","src-queue":f"{queue_name}","dest-protocol":"amqp091","dest-uri":f"amqp://{username}:{password}@{RMQ2}/{vhost}","dest-queue":f"{queue_name}"}}

formated_date = datetime.now().strftime("%Y_%m_%d_%H_%M")
NEWR =f'{REPO}/queue_report_{formated_date}.csv'

with open(f'{REPO}/queue_report_{formated_date}.csv', 'a', encoding='utf8', newline='') as output_file:
    r = requests.get(f'http://{RMQ1}:15672/api/queues?sort=messages_ready&sort_reverse=true&columns=vhost,name,messages_ready',auth=(username,password))
    rj = r.json()
    fc = csv.DictWriter(output_file,fieldnames=rj[0].keys())
    fc.writeheader()
    fc.writerows(rj)


with open(f'{NEWR}','r') as muh:
    csv_reader = csv.reader(muh)
    next(csv_reader, None)
    for i in csv_reader:
        queue_name = i[1]
        vhost = i[2]
        #print(row)
        headers = {"Content-Type": "application/json"}
        #remove src delete after for old RMQ servers
        payload = {"value":{"src-protocol":"amqp091","src-uri":f"amqp://{username}:{password}@{RMQ1}/{vhost}","src-queue":f"{queue_name}","dest-protocol":"amqp091","dest-uri":f"amqp://{username}:{password}@{RMQ2}/{vhost}","dest-queue":f"{queue_name}","ack-mode": "on-confirm", "src-delete-after": "queue-length"}}
        
        #continue
        if int(i[0]) > 0:
            pattern = re.compile(r'^PATTERN2|PATTERN')
            muh = re.search(pattern,i[1])
            if muh:
               get_msg_rdy = requests.get(f'http://{RMQ1}:15672/api/queues/{vhost}/{queue_name}',auth=(username,password)).json()
               msg_rdy = get_msg_rdy['messages_ready']
               
               while True:
                user_input = input(f"{queue_name} has {msg_rdy} in {vhost} continue y/n? ")
                if user_input == 'y':
                    shovel = requests.put(f'http://{RMQ1}:15672/api/parameters/shovel/{vhost}/{queue_name}',json=payload,auth=(username,password),headers=headers)
                    if shovel.success_code in [ 204 ,201 ]:
                        print(i[1],'in', i[2],f' had {msg_rdy} messages moved: Sucess Code: {shovel.status_code}\n')
                        break
                elif user_input == 'n':
                     print(f"{queue_name} in {vhost} skipped")
                     break
                else:
                    print('y/n only')
            else:
                print(i[1],'in', i[2],'not shoveled')
