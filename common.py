import os
from openai import OpenAI
from dataclasses import dataclass

@dataclass(frozen=True)
class Model:
    basic: str = 'gpt-5-mini'
    advanced: str = 'gpt-5'


model = Model()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=30,
    max_retries=1
)



import tiktoken

def gpt_num_tokens(messages, model='gpt-4o'):
    encoding = tiktoken.encoding_for_model(model)
    tokens_per_message = 3    # 모든 메시지는 다음 형식을 따른다: <|start|>{role/name}\n{content}<|end|>\n
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for _, value in message.items():
            num_tokens += len(encoding.encode(value))
    num_tokens += 3    # 모든 메시지는 다음 형식으로 assistant의 답변을 준비한다: <|start|>assistant<|message|>
    return num_tokens


from types import SimpleNamespace

def dict_to_namespace(data):
    if isinstance(data, dict):
        return SimpleNamespace(**{k: dict_to_namespace(v) for k, v in data.items()})
    elif isinstance(data, list):
        return [dict_to_namespace(i) for i in data]
    else:
        return data

def makeup_response(message):
    data = {
        'output': [{
            'content': [{'text': message}],
            'role': 'assistant'
        }],
        'usage': {'total_tokens': 0}
    }
    ns = dict_to_namespace(data)

    ns.output_text = message

    return ns
