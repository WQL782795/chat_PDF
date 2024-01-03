import json
import sqlite3
import copy
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

client = OpenAI()

instruction = """
你的任务是识别用户对手机流量套餐产品的选择条件。
"""

database_schema_string = """
CREATE TABLE FlowPackage (
    package_id INT PRIMARY KEY NOT NULL ,--主键，不为空
    name VARCHAR(255) NOT NULL,--套餐名字
    price DECIMAL(10, 2) NOT NULL,--套餐价格
    data INT NOT NULL,--流量额度
    requirement TEXT--特殊套餐，满足特定条件的用户才能购买，可选项有：在校生
);
"""


class DB:
    def __init__(self):
        self.conn = sqlite3.connect(':memory:')
        self.cr = self.conn.cursor()
        self.mock_data()

    def ask_database(self, query):
        self.cr.execute(query)
        records = self.cr.fetchall()
        return records

    def mock_data(self):
        self.cr.execute(database_schema_string)

        mock_data = [(1, "经济套餐", 50, 10, None), (2, "畅游套餐", 180, 100, None), (3, "无限套餐", 300, 1000, None),
                     (4, "校园套餐", 150, 200, "在校生")]
        for record in mock_data:
            self.cr.execute('''
            INSERT INTO FlowPackage (package_id, name, price, data, requirement)
            VALUES (?, ?, ?, ?, ?)
            ''', record)
        self.conn.commit()


class NLU:

    def _get_completion(self, messages, model="gpt-3.5-turbo-1106"):
        response = client.chat.completions.create(
            model=model, messages=messages, temperature=0, tools=[{
                "type": "function",
                "function": {
                             "name": "ask_database",
                             "description": "Use this function to answer user questions about business. \
                                        Output should be a fully formed SQL query.",
                             "parameters": {
                                            "type": "object",
                                            "properties": {
                                                           "query": {
                                                                      "type": "string",
                                                               "description": f"""
                                        SQL query extracting info to answer the user's question.
                                        SQL should be written using this database schema:
                                        {database_schema_string}
                                        The query should be returned in plain text, not in JSON.
                                        The query should only contain grammars supported by SQLite.
                                        """,
                                            }
                                        }, "required": ["query"],
                                    }
                            }
                    }
            ],
        )
        response = response.choices[0].message

        if response.tool_calls is not None:
            tool_call = response.tool_calls[0]
            if tool_call.function.name == "ask_database":
                args = json.loads(tool_call.function.arguments)
                return args["query"]

class DialogManager:
    def __init__(self, prompt_templates):
        self.state = {}
        self.session = [{"role": "system",
            "content": "你是一个手机流量套餐的客服代表，你叫小瓜。可以帮助用户选择最合适的流量套餐产品。"}]
        self.db = DB()
        self.nlu = NLU()
        self.prompt_templates = prompt_templates

    def _wrap(self, user_input, records):
        if records:
            gpt_prompt=f'用户说：{user_input} \n\n'
            for pack in records:
                prompt = self.prompt_templates["recommand"]
                for index, value in enumerate(pack):
                    prompt = prompt.replace(f"__{index}__", str(value))
                gpt_prompt+=prompt

        else:
            gpt_prompt = self.prompt_templates["not_found"].replace("__INPUT__", user_input)
        return gpt_prompt

    def _call_chatgpt(self, prompt, model="gpt-3.5-turbo"):
        session = copy.deepcopy(self.session)
        session.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(model=model, messages=session, temperature=0, )
        return response.choices[0].message.content

    def parse(self, user_input):
        self.session.append({"role": "user", "content": user_input})
        return self.nlu._get_completion(self.session)



    def run(self, user_input):
        print("客官稍等哦，小瓜查询ing~")
        # 调用NLU获得语义解析
        sql = self.parse(user_input)
        print("===sql===")
        print(sql)

        # 根据状态检索DB，获得满足条件的候选
        records = self.db.ask_database(sql)

        # 拼装prompt调用chatgpt
        prompt_for_chatgpt = self._wrap(user_input, records)
        print(prompt_for_chatgpt)
        # 调用chatgpt获得回复
        response = self._call_chatgpt(prompt_for_chatgpt)

        # 将当前用户输入和系统回复维护入chatgpt的session
        self.session.append({"role": "assistant", "content": response})
        print(response)


if __name__ == "__main__":
    prompt_templates = {
        "recommand": "向用户介绍如下产品：__1__，月费__2__元，每月流量__3__G。",
        "not_found": "用户说：__INPUT__ \n\n没有找到满足__2__元价位__3__G流量的产品，询问用户是否有其他选择倾向。"}
    dm = DialogManager(prompt_templates)
    while(True):
        dm.run(input("您好，请问有什么可以帮您\n"))