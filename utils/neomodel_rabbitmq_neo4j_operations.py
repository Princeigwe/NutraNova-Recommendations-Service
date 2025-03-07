from neomodel import db
from neomodel.exceptions import NeomodelException
import os

ENVIRONMENT = os.environ.get("ENVIRONMENT", default="production" )

def get_custom_rabbitmq_user_message_ids():
  try:
    query = " MATCH (user_data_message_id: RabbitMQ_User_Data_Message_id) RETURN user_data_message_id; "
    results,meta = db.cypher_query(query=query)
    print ("Results: ",results)
    user_message_ids = [node[0]["message_id"] for node in results]
    print("User data message ids: ",user_message_ids)
    return user_message_ids
  except NeomodelException as e:
    print("Error fetching rabbitmq user message id nodes: ", e)


def add_consumed_rabbitmq_user_message_id(message_id):
  try:
    query = " CREATE(user_data_message_id: RabbitMQ_User_Data_Message_id{ message_id: $message_id }) RETURN user_data_message_id; "
    db.cypher_query(query=query, params={"message_id": message_id})
    print("Message id node inserted successfully")
  except NeomodelException as e:
    print("Error inserting new custom rabbitmq user data message id node: ", e)