from openai import OpenAI
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())

client = OpenAI()

prompt_template = """
你是一个问答机器人。
你的任务是根据下述给定的已知信息回答用户问题。
确保你的回复完全依据下述已知信息。不要编造答案。
如果下述已知信息不足以回答用户的问题，请直接回复"我无法回答您的问题"。

已知信息:
__INFO__

用户问：
__QUERY__

请用中文回答用户问题。
"""


def send_llm(messages, model="gpt-4"):
    return client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
    )

def build_prompt(query, rag_data):
    return prompt_template.replace("__INFO__", rag_data).replace("__QUERY__", query)

def build_messages(query, rag_data, context):
    prompt = build_prompt(query, rag_data)
    messages = context + [
        {"role": "user", "content": prompt}
    ]
    return messages