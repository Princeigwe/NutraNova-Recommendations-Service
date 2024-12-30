from .cosine_similarity import cosine_similarities_for_chef_preference
# from utils.kafka.produce.recommended_feed import send_user_recommended_feed
from utils.rabbitmq.publishers.send_user_recommended_feed import send_user_recommended_feed
from recommend_engine.models import Chef
from neomodel import DoesNotExist
import os

# def recommend_feed_for_existing_user(messages):
#     for message in messages:
#         print(message)
#         recommended_feed = []
#         recipe_cos_similarities = cosine_similarities_for_chef_preference(
#             message.value)
#         for item in recipe_cos_similarities:
#             # get the first 5 items in the cos similarities list
#             if recipe_cos_similarities.index(item) > 4:
#                 break

#             # remove the cosine similarity data
#             item.pop("recipe_cos_similarity")
#             recommended_feed.append(item)
#         print(f"Recommended feed for {message.value}: ", recommended_feed)

#         # publish processed recommended feed to kafka
#         user_recommended_feed = {
#             # message.value is the username the cos similarity function is working with
#             "username": message.value,
#             "recommended_feed": recommended_feed
#         }
#         send_user_recommended_feed(user_recommended_feed)


def recommend_feed_for_existing_user(message):
  rabbitmq_message_type = os.environ.get('RECOMMENDED_FEED_MESSAGE_TYPE')
  print(message)
  recommended_feed = []
  recipe_cos_similarities = cosine_similarities_for_chef_preference(message['username'])
  for item in recipe_cos_similarities:
    # get the first 5 items in the cos similarities list
    if recipe_cos_similarities.index(item) > 4:
      break

    # remove the cosine similarity data
    item.pop("recipe_cos_similarity")
    recommended_feed.append(item)
  print(f"Recommended feed for {message['username']}: ", recommended_feed)

  # publish processed recommended feed to rabbitmq
  user_recommended_feed = {
    "type": rabbitmq_message_type,
    "username": message['username'],
    "recommended_feed": recommended_feed
  }
  send_user_recommended_feed(user_recommended_feed)


def recommend_feed_for_new_user(user_detail):
  """this function will be responsible for assisting recommending chefs to follow for new users, in the recipes service"""

  chef_username = user_detail['chef_username']
  chef_first_name = user_detail['chef_first_name']
  chef_last_name = user_detail['chef_last_name']
  chef_preferences = user_detail['chef_preferences']

  try:
    chef = Chef.nodes.get(username=chef_username)
  except DoesNotExist:
    chef = Chef(username=chef_username, first_name=chef_first_name, last_name=chef_last_name, preferences=chef_preferences).save()

  recommended_feed = []
  recipe_cos_similarities = cosine_similarities_for_chef_preference(chef.username)
  for item in recipe_cos_similarities:
    # get the first 7 items in the cos similarities list
    if recipe_cos_similarities.index(item) > 5:
      break

    # remove the cosine similarity data
    item.pop("recipe_cos_similarity")
    recommended_feed.append(item)
      
  return recommended_feed
