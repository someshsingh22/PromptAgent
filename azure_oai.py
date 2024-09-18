import json
import os

import requests

class OpenAIModel:
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    AUTHORIZATION_CODE = os.getenv("AUTHORIZATION_CODE")
    AZURE_URL = os.getenv("AZURE_URL")
    FIREFALL_URL = os.getenv("FIREFALL_URL")

    def __init__(self, model_name: str, temperature: float, **kwargs):
        self.model_name = model_name
        self.temperature = temperature
        self.batch_forward_func = self.batch_forward_chatcompletion
        self.refresh_token()
        self.generate = self.gpt_chat_completion

    def refresh_token(self):
        data={
                "grant_type": "authorization_code",
                "client_id": self.CLIENT_ID,
                "client_secret": self.CLIENT_SECRET,
                "code": self.AUTHORIZATION_CODE,
        }
        response = requests.post(
            self.AZURE_URL,
            data=data
        )
        self.auth_token = json.loads(response.text)["access_token"]

    def gpt_chat_completion(self, prompt, max_tokens=100):
        headers = {
            "x-gw-ims-org-id": self.CLIENT_ID,
            "x-api-key": self.CLIENT_ID,
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json",
        }
        json_data = {
            "dialogue": {"question": prompt},
            "llm_metadata": {
                "model_name": self.model_name,
                "temperature": self.temperature,
                "max_tokens": max_tokens,
                "n": 1,
                "llm_type": "azure_chat_openai",
            },
        }
        try:
            response = requests.post(
                self.FIREFALL_URL, headers=headers, json=json_data
            )
        except:
            self.refresh_token()
            response = requests.post(
                self.FIREFALL_URL, headers=headers, json=json_data
            )
        openai_response = json.loads(response.text)
        text = openai_response["generations"][0][0]["text"]
        return text

    def batch_forward_chatcompletion(self, batch_prompts):
        responses = []
        for prompt in batch_prompts:
            response = self.gpt_chat_completion(prompt=prompt)
            responses.append(response)
        return responses
