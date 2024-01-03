#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymilvus import *
import db_demo
import zlib
from pdf_split import extract_text_from_pdf

import BGE


def insert_data(vectors):
    condb()
    fields = [FieldSchema(name="id", dtype=DataType.INT64, is_primary=True),
              FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=768)]

    schema = CollectionSchema(fields)
    collection_name = "kylin"
    collection = Collection(name=collection_name)
    for vector in vectors:
        mr = collection.insert([{"vector": vector}])
        print(mr)


def condb():
    connections.connect("default", uri="https://in03-c9dcdc65d293a68.api.gcp-us-west1.zillizcloud.com",
                        user="kylinw782795@gmail.com", password="Wql@782795",
                        token="7e069fbae019f043cf453b5c41c370677d6f43eacb177c6f4b2cd169addf30378cf42e4fd802f1ebe00c1e464c75bb39fd114d79")
    for conn in utility.list_collections():
        print(conn)


def compress_text(text):
    compressed = zlib.compress(text.encode('utf-8'))
    vector = [int(b) for b in compressed]
    return vector


def decompress_text(vector):
    byte_param = bytes([int(b) for b in vector])
    compressed = zlib.decompress(byte_param)
    return compressed.decode('utf-8')


def get_embedding(paragraphs_list, embedding_list, retry_list):
    for i, paragraph in enumerate(paragraphs_list):
        print(paragraph)
        print('-' * 80)
        res = BGE.text_embedding(paragraph)
        if not res:
            retry_list.append(paragraph)
            continue
        vector = compress_text(paragraph)
        raw = {"id": i + 1, "text_compress": vector, "text_embedding": res}
        embedding_list.append(raw)
        paragraphs_list.remove(paragraph)


pdf_path = 'xuezhong.pdf'

if __name__ == '__main__':
    # paragraphs_list = extract_text_from_pdf(pdf_path)
    # raws = []
    # retry_list = []
    # get_embedding(paragraphs_list, raws, retry_list)
    # if len(retry_list) >= 1:
    #     get_embedding(retry_list, raws, retry_list)
    # if len(retry_list) >= 1:
    #     raise "retry error"
    #
    # print(raws)
    # db_demo.db_insert(raws)

    result = db_demo.db_search("徐凤年是谁")
    for re in result:
        for i, r in enumerate(re) :
            print(f"Top{i+1}\nDistance:{r.distance}\nText:{decompress_text(r.entity.text_compress)}\n\n")