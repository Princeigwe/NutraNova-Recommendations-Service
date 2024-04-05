from .cosine_similarity import cosine_similarities_for_chef_preference
from utils.kafka.produce.recommended_feed import send_user_recommended_feed


def recommend_feed_for_user(messages):
  for message in messages:
    print(message)
    recommended_feed = []
    recipe_cos_similarities = cosine_similarities_for_chef_preference(message.value)
    for item in recipe_cos_similarities:
      # get the first 5 items in the cos similarities list
      if recipe_cos_similarities.index(item) > 4:
        break

      # remove the cosine similarity data
      item.pop("recipe_cos_similarity")
      recommended_feed.append(item)
    
    print(f"Recommended feed for {message.value}: ", recommended_feed)
    # return recommended_feed

    # publish processed recommended feed to kafka
    user_recommended_feed = {
      "username": message.value, # message.value is the username the cos similarity function is working with
      "recommended_feed": recommended_feed
    }
    send_user_recommended_feed(user_recommended_feed)
    
