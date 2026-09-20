import customtkinter as ctk
import threading
from eduSess import EduSession
from bot import EduBot  

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EduBot Controller")
        self.geometry("350x300")

        self.label = ctk.CTkLabel(self, text="Вход в Moodle", font=("Arial", 20))
        self.label.pack(pady=20)

        self.entry_login = ctk.CTkEntry(self, placeholder_text="Логин", width=250)
        self.entry_login.pack(pady=10)

        self.entry_pass = ctk.CTkEntry(self, placeholder_text="Пароль", width=250, show="*")
        self.entry_pass.pack(pady=10)

        self.btn_start = ctk.CTkButton(self, text="Запустить бота", command=self.start_bot_thread)
        self.btn_start.pack(pady=20)

        self.status_label = ctk.CTkLabel(self, text="Статус: Ожидание", text_color="gray")
        self.status_label.pack(pady=10)

    def start_bot_thread(self):
        login = self.entry_login.get()
        password = self.entry_pass.get()

        if not login or not password:
            self.status_label.configure(text="Ошибка: введите данные!", text_color="red")
            return

        self.btn_start.configure(state="disabled")
        self.status_label.configure(text="Статус: Запуск...", text_color="yellow")

        threading.Thread(target=self.run_logic, args=(login, password), daemon=True).start()

    def run_logic(self, login, password):
        try:
            with EduSession(login, password) as active_session:
                self.status_label.configure(text="Статус: Бот работает!", text_color="green")
                bot = EduBot(edu_session=active_session)
                bot.run()
        except Exception as e:
            self.status_label.configure(text=f"Ошибка: {str(e)[:20]}...", text_color="red")
            self.btn_start.configure(state="normal")


if __name__ == "__main__":
    app = App()
    app.mainloop()