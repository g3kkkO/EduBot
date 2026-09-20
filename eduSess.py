from requests import Session
from bs4 import BeautifulSoup
import re


class EduSession:
    def __init__(self,login,password):
        self.login = login
        self.password = password
        self.session = Session()
        self.logintoken = None
        self.MoodleSession = None
        self.MOODLEID1_ =  None
        self.sesskey = None
        self.userid = None
        self.conversation_id = None
    def __enter__(self):
        login_page = self.session.get(
            "https://edu.stankin.ru/login/index.php",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
        )
        soup = BeautifulSoup(login_page.text, 'html.parser')
        token_input = soup.find('input', {'name': 'logintoken'})
        self.logintoken = token_input.get('value')
        login_data = {
            "username": self.login,
            "password": self.password,
            "anchor": "",
            "logintoken": self.logintoken,
        }
        login_response = self.session.post(
            "https://edu.stankin.ru/login/index.php",
            data=login_data,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://edu.stankin.ru",
                "Referer": "https://edu.stankin.ru/login/index.php",
            },
            allow_redirects=True
        )

        sess_dict = self.session.cookies.get_dict()
        self.MoodleSession = sess_dict['MoodleSession']
        self.MOODLEID1_ = sess_dict['MOODLEID1_']

        test_response = self.session.get(
            "https://edu.stankin.ru/my/courses.php",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
            }
        )
        self.sesskey = re.search(r'"sesskey":"([^"]+)"', test_response.text).group(1)

        match = re.search(r'"userid":"?(\d+)"?', test_response.text)
        if not match:
            match = re.search(r'"userid":(\d+)', test_response.text)
        if not match:
            match = re.search(r'data-userid="(\d+)"', test_response.text)
        self.userid = match.group(1)


        payload = [{
            "index": 0,
            "methodname": "core_message_get_self_conversation",  # Скрытый метод Moodle
            "args": {
                "userid": self.userid,
                "messagelimit": 1,
                "messageoffset": 0,
                "newestmessagesfirst": True
            }
        }]

        api_url = f"https://edu.stankin.ru/lib/ajax/service.php?sesskey={self.sesskey}&info=core_message_get_self_conversation"
        response = self.session.post(api_url, json=payload).json()
        self.conversation_id = response[0]['data']['id']

        return self




    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Закрываем соединение")
        return False