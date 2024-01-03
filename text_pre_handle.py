#!/usr/bin/env python
# -*- coding: utf-8 -*-
import db
import zlib
from pdf_split import extract_text_from_pdf

import BGE


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

    result = db.db_search("徐凤年是谁")
    for re in result:
        for i, r in enumerate(re) :
            print(f"Top{i+1}\nDistance:{r.distance}\nText:{decompress_text(r.entity.text_compress)}\n\n")