from neomodel import db

def create_offset_node():
  query = """
    MERGE (:RABBITMQ_MESSAGE_OFFSET{custom_id: 1});
  """
  db.cypher_query(query)


def update_offset_node(new_offset):
  query = """
    MATCH(offset_node: RABBITMQ_MESSAGE_OFFSET{custom_id: 1}) SET offset_node.message_offset=$new_offset RETURN offset_node;
  """
  params = {"new_offset": new_offset}
  db.cypher_query(query, params)


def get_offset_node(custom_id):
  query = """
    MATCH(offset_node: RABBITMQ_MESSAGE_OFFSET{custom_id: $custom_id}) RETURN offset_node;
  """
  params = {"custom_id": custom_id}
  result = db.cypher_query(query, params)
  return result