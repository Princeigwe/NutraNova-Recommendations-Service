from .models import Recipe,Tag, Chef
from utils import cosine_similarity


def resolve_create_tag(*_, name):
  pass


def resolve_user_preference_vector(*_, username):
  cosine_similarity.chef_preference_to_tag_vector_embedding(username)
  return "vector given"


def resolve_recipes_tags_vector(*_):
  cosine_similarity.recipe_to_tag_embeddings()
  return "recipe vectors given"


def resolve_cosine_similarities(*_, username):
  cosine_similarity.cosine_similarity_for_chef_preference(username)
  return f"cosine similarities for {username} calculated"