
from dotenv import load_dotenv
load_dotenv()
from utils.recommend_feed import recommend_feed_for_existing_user

def consume_recommend_feed_request(message):
  print("recommending feed...")
  recommend_feed_for_existing_user(message)
