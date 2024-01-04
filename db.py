import os

from pymilvus import DataType, connections, utility, FieldSchema, CollectionSchema, Collection

import BGE
from dotenv import load_dotenv,find_dotenv

load_dotenv(find_dotenv())

conn = connections.connect("default", uri=os.getenv("MILVUS_URI"),
                           user=os.getenv("MILVUS_USER"), password=os.getenv("MILVUS_PASSWORD"),
                           token=os.getenv("MILVUS_TOKEN"))

COLLECTION_NAME = 'kylin_vector'
fields = [FieldSchema(name="id", dtype=DataType.INT64, is_primary=True),
          FieldSchema(name="text_embedding", dtype=DataType.FLOAT_VECTOR, dim=1024)]

schema = CollectionSchema(fields, description="Schema of Medium articles", enable_dynamic_field=True)
collection = Collection(name=COLLECTION_NAME,
                        description="test",
                        schema=schema)
index_params = {"index_type": "AUTOINDEX", "metric_type": "L2", "params": {}}

collection.create_index(field_name="text_embedding", index_params=index_params, index_name='text_embedding_index')


def db_insert(rows):
    res = collection.insert(rows)
    print(f"response: {res}")
    collection.load()
    progress = utility.loading_progress(COLLECTION_NAME)['loading_progress']
    print(progress)


def db_search(query):
    query_vector = BGE.text_embedding(query)
    search_params = {"metric_type": "L2"}

    results = collection.search(data=[query_vector], anns_field="text_embedding", param=search_params,
                                output_fields=["text_embedding", "text_compress"], limit=5)

    return results


if __name__ == '__main__':
    db_search("小二")