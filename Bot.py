import gradio as gr

from chatgpt import *
from db import *
from text_pre_handle import *


def query(query):
    rag_data = ''
    context = []
    result = db_search(query)
    for re in result:
        for i, r in enumerate(re):
            rag_data+= f"Top{i + 1}\nDistance:{r.distance}\nText:{decompress_text(r.entity.text_compress)}\n\n"
    response = send_llm(build_messages(query, rag_data, context))
    context.append({'role': 'user', 'content': query})
    context.append({'role': 'assistant', 'content': response})
    return response


demo = gr.Interface(
    fn=query,
    inputs=["text", "slider"],
    outputs=["text"],
)

demo.launch()
