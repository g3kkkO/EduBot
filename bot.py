import time
import requests
from  questions import que
from dotenv import load_dotenv
import os


load_dotenv()


API_KEY = os.getenv("KEY")



class EduBot:
    def __init__(self, edu_session):
        self.sess = edu_session
        self.ajax_url_base = f"https://edu.stankin.ru/lib/ajax/service.php?sesskey={self.sess.sesskey}"

    def get_messages(self, limit=20):
        payload = [{
            "index": 0,
            "methodname": "core_message_get_conversation_messages",
            "args": {
                "currentuserid": self.sess.userid,
                "convid": self.sess.conversation_id,
                "newest": True,
                "limitnum": limit,
                "limitfrom": 0
            }
        }]
        try:
            response = self.sess.session.post(self.ajax_url_base + "&info=core_message_get_conversation_messages",
                                              json=payload)
            data = response.json()
            if not data[0].get('error'):
                return data[0]['data']['messages']
        except Exception as e:
            print(f"[ОШИБКА СЕТИ] При получении сообщений: {e}")
        return []

    def send_reply(self, text):
        payload = [{
            "index": 0,
            "methodname": "core_message_send_messages_to_conversation",
            "args": {
                "conversationid": self.sess.conversation_id,
                "messages": [{"text": text}]
            }
        }]
        try:
            self.sess.session.post(self.ajax_url_base + "&info=core_message_send_messages_to_conversation",
                                   json=payload)
        except Exception as e:
            print(f"[ОШИБКА СЕТИ] При отправке: {e}")

    def mark_as_read(self):
        payload = [{
            "index": 0,
            "methodname": "core_message_mark_all_conversation_messages_as_read",
            "args": {
                "userid": self.sess.userid,
                "conversationid": self.sess.conversation_id
            }
        }]
        try:
            self.sess.session.post(self.ajax_url_base + "&info=core_message_mark_all_conversation_messages_as_read",
                                   json=payload)
        except Exception:
            pass

    def run(self, poll_interval=5):
        print(f"\n=== Бот запущен! Рабочий чат ID: {self.sess.conversation_id} ===")
        history = self.get_messages()
        last_processed_id = max([msg['id'] for msg in history]) if history else 0

        while True:
            try:
                time.sleep(poll_interval)
                messages = self.get_messages()
                messages = sorted(messages, key=lambda x: x['id'])

                for msg in messages:
                    if msg['id'] > last_processed_id:
                        raw_text = msg['text'].replace('<p>', '').replace('</p>', '').strip()
                        if "Бот:" not in raw_text:
                            prompt = f"""
                                Ты — эксперт по виртуализации и сетевым технологиям. Используй только ПРИВЕДЕННУЮ НИЖЕ базу знаний.
                                Смотри, каждый вариант ответа отделен между собой, но не цифрами а пробелма или новой строкой, так что 
                                просто выбери из предложенных правильный.
                                ПРАВИЛА:
                                1. Если в базе есть точный или похожий вопрос, ответь СТРОГО на основе ответа из базы.
                                2. Если вопроса нет в базе, ответь самостоятельно.

                                БАЗА ЗНАНИЙ:
                                {que}

                                ВОПРОС СТУДЕНТА:
                                {raw_text}

                                ОТВЕТ:
                                """
                            print(f"\n<<< [ВОПРОС]: {raw_text}")

                            
                            response = requests.post(
                                "https://openrouter.ai/api/v1/chat/completions",
                                headers={
                                    "Authorization": f"Bearer {API_KEY}",
                                    "Content-Type": "application/json",
                                },
                                json={
                                    "model": "google/gemini-3-flash-preview", 
                                    "messages": [
                                        {"role": "system", "content": "You are Grok, a helpful AI assistant."},
                                        {"role": "user", "content": f"{prompt}"}
                                    ]
                                }
                            )

                            
                            data = response.json()
                            ai_text = data["choices"][0]["message"]["content"].strip()

                            self.send_reply(f"Бот: {ai_text}")
                            self.mark_as_read()

                        last_processed_id = msg['id']

            except Exception as e:
                print(f"\n[ОШИБКА]: {e}")
                time.sleep(10)