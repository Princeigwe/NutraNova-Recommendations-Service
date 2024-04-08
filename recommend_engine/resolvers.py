from .models import Recipe, Tag, Chef
from utils import cosine_similarity
from utils.recommend_feed import recommend_feed_for_new_user
from utils.get_user import get_access_token, get_user


def resolve_create_tag(*_, name):
    pass


def resolve_user_preference_vector(*_, username):
    cosine_similarity.chef_preference_to_tag_vector_embedding(username)
    return "vector given"


def resolve_recipes_tags_vector(*_):
    cosine_similarity.recipe_to_tag_embeddings()
    return "recipe vectors given"


def resolve_cosine_similarities(*_, username):
    cosine_similarity.cosine_similarities_for_chef_preference(username)
    return f"cosine similarities for {username} calculated"


def resolve_recommend_feed_for_new_user(_, info):
    user = get_user(info)
    user_preferences = {
        "dietary_preference": user['dietary_preference'],
        "health_goal": user['health_goal'], 
        "allergens": user['allergens'], 
        "activity_level": user['activity_level'], 
        "cuisines": user['cuisines'], 
        "medical_conditions": user['medical_conditions'], 
        "taste_preferences": user['taste_preferences']
    }
    user_detail = {
        "chef_username": user['username'],
        "chef_first_name": user['first_name'],
        "chef_last_name": user['last_name'],
        "chef_preferences": user_preferences
    }
    recommended_feed = recommend_feed_for_new_user(user_detail)
    return recommended_feed