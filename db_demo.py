from pymilvus import DataType, connections, utility, FieldSchema, CollectionSchema, Collection

import BGE

conn = connections.connect("default", uri="https://in03-c9dcdc65d293a68.api.gcp-us-west1.zillizcloud.com",
                           user="kylinw782795@gmail.com", password="Wql@782795",
                           token="7e069fbae019f043cf453b5c41c370677d6f43eacb177c6f4b2cd169addf30378cf42e4fd802f1ebe00c1e464c75bb39fd114d79")

# 创建集合
COLLECTION_NAME = 'kylin_vector'
fields = [FieldSchema(name="id", dtype=DataType.INT64, is_primary=True),
          FieldSchema(name="text_embedding", dtype=DataType.FLOAT_VECTOR, dim=1024)]

schema = CollectionSchema(fields, description="Schema of Medium articles", enable_dynamic_field=True)
# if not utility.has_collection(COLLECTION_NAME):
collection = Collection(name=COLLECTION_NAME,
                        description="Medium articles published between Jan and August in 2020 in prominent publications",
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