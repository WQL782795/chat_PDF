import gradio as gr

from chatgpt import *
from db import *
from text_pre_handle import *


def query(query_text, history):
    rag_data = ''
    context = []
    result_data = db_search(query_text)
    for data in result_data:
        for i, r in enumerate(data):
            rag_data += f"Top{i + 1}\nDistance:{r.distance}\nText:{decompress_text(r.entity.text_compress)}\n\n"
    response = send_llm(build_messages(query_text, rag_data, context))
    context.append({'role': 'user', 'content': query_text})
    context.append({'role': 'assistant', 'content': response})
    return response


gr.ChatInterface(query,
                 chatbot=gr.Chatbot(height=300),
                 textbox=gr.Textbox(placeholder="welcome to ask me question!", container=False, scale=7),
                 title="雪中悍刀行",
                 description="Ask me any question about the book 《雪中悍刀行》",
                 theme="soft",
                 retry_btn=None,
                 undo_btn="Delete Previous",
                 clear_btn="Clear", ).launch(share=True)