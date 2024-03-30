from .models import Recipe,Tag, Chef
from utils import cosine_similarity


def resolve_create_tag(*_, name):
  pass


def resolve_user_preference_vector(*_, username):
  cosine_similarity.chef_preference_to_tag_vector_embedding(username)
  return "vector given"