import os
from dotenv import load_dotenv
load_dotenv()
import json
import neomodel
from neomodel import db, DoesNotExist
from recommend_engine.models import Chef
# from utils.rabbitmq.rabbitmq_config import channel
from utils.rabbitmq.channels.consume_chef_data_channel import channel

rabbitmq_message_type = os.environ.get('CHEF_DATA_UPDATE_MESSAGE_TYPE')

def consume_and_update_chef_node_data(message):
  try:
    print(f"Received message: {message}")

    # checking if 'old_username' key is in kafka message. this handles the operation for just updating the username of the Chef node
    if 'old_username' in message:
      chef = Chef.nodes.get(username=message['old_username'])
      chef.username = message['new_username']
      chef.save()
      print(f"{chef.first_name} username is now {chef.username}")
      
    # this is a response operation for the 'updateProfile' resolver in the user microservice
    else:
      chef = Chef.nodes.get(username=message['username'])
      chef.first_name = message['first_name'] if 'first_name' in message else chef.first_name
      chef.last_name = message['last_name'] if 'last_name' in message else chef.last_name
      chef.preferences = message['preferences'] if 'preferences' in message else chef.preferences
      chef.save()
      print(f"{chef.username} data updated")
        

  except DoesNotExist:
    pass
    # chef = Chef(username=message['username'] if 'username' in message else message['new_username'], first_name=message['first_name'], last_name=message['last_name'], preferences=message['preferences']).save()

  except KeyboardInterrupt:
    pass
  