import os
from dotenv import load_dotenv
load_dotenv()
import json
import neomodel
from neomodel import db, DoesNotExist
from recommend_engine.models import Chef
from utils.rabbitmq.rabbitmq_config import channel

##** this queue was manually created on the dashboard
# queue = os.environ.get('CLOUDAMQP_USER_DATA_UPDATE_QUEUE')

exchange_name=os.environ.get('CLOUDAMQP_FANOUT_EXCHANGE')

# creating and binding queue to fanout exchange
queue = os.environ.get('CLOUDAMQP_RECOMMENDATION_CHEF_DATA_UPDATE_QUEUE')
result = channel.queue_declare(queue=queue, exclusive=True) # 'exclusive' argument deletes queue once consumer connection is deleted
channel.queue_bind(exchange=exchange_name, queue=result.method.queue)

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


def callback(ch, method, properties, body):
  body = json.loads(body)
  consume_and_update_chef_node_data(body)


def consume():
  channel.basic_consume(queue, callback, auto_ack=True)
  channel.start_consuming()