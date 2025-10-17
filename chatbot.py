import math
from common import client, makeup_response, gpt_num_tokens

from warning_agent import WarningAgent
# from pprint import pprint


class Chatbot:

    def __init__(self, model, system_role, instruction, **kwargs):
        self.context = [{'role': 'developer', 'content': system_role}]
        self.model = model
        self.instruction = instruction
        self.max_token_size = 16 * 1024
        self.kwargs = kwargs
        self.user = kwargs['user']
        self.assistant = kwargs['assistant']
        self.warningAgent = self._create_warning_agent()

    def add_user_message(self, message):
        self.context.append({'role': 'user', 'content': message})

    def _send_request(self):
        try:
            if gpt_num_tokens(self.context) > self.max_token_size:
                self.context.pop()
                return makeup_response('메시지를 조금 짧게 보내줄래?')
            else:
                response = client.responses.create(
                    model=self.model,
                    input=self.context)
        except Exception as e:
            print(f'> Exception 오류({type(e)}) 발생:{e} ')
            return makeup_response('[내 찐친 챗봇에 문제가 발생했습니다. 잠시 뒤 이용해주세요]')
        return response

    def send_request(self):
        print(1)
        if self.warningAgent.monitor_user(self.context):
            return makeup_response(self.warningAgent.warn_user()) 
        else:
            self.context[-1]['content'] += self.instruction
            return self._send_request()

    def add_response(self, response):
        # pprint(response.output[-1].model_dump())
        self.context.append({
            'role': response.output[-1].role,
            'content': response.output_text})

    def get_last_response(self):
        return self.context[-1]['content']

    def clean_context(self):
        for idx in reversed(range(len(self.context))):
            if self.context[idx]['role'] == 'user':
                self.context[idx]['content'] = self.context[idx]['content'].split('instruction:\n')[0].strip()
                break

    def handle_token_limit(self, response):
        try:
            if response['usage']['total_tokens'] > self.max_token_size:
                remove_size = math.ceil(len(self.context) / 10)
                self.context = [self.context[0]] + self.context[remove_size+1:]
        except Exception as e:
            print(f'> handle_token_limit exception:{e}')

    def _create_warning_agent(self):
        return WarningAgent(
                    model=self.model,
                    user=self.user,
                    assistant=self.assistant,
               )
