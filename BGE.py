import requests
import dotenv
import os
from transformers import AutoTokenizer, AutoModel

dotenv.load_dotenv(dotenv.find_dotenv())
AK=os.getenv("ACCESS_TOKEN")

headers = {"Authorization": f"Bearer {AK}"}

def text_embedding(text):
	response = requests.post(os.getenv("API_URL"), headers=headers, json=text)
	if response.status_code != 200:
		print(f"reserror:{response.json()}")
		return False
	return  response.json()[0][0]


if __name__ == "__main__":
	# output = text_embedding({"inputs": "我是说", })
	#
	# print(output)
	# Use a pipeline as a high-level helper
	from transformers import pipeline

	# pipe = pipeline("feature-extraction", model="BAAI/bge-large-zh-v1.5")
	tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-large-zh-v1.5")
	model = AutoModel.from_pretrained("BAAI/bge-large-zh-v1.5")
	print(model.config.hidden_size)