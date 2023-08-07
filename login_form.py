from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot import types
import random
import smtplib, ssl
import functions
from email.message import EmailMessage

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "tankssimulatormanager@gmail.com"  # Enter your address
password = "gdzqkejlfaasdgpu"
class LoginForm:
    def __init__(self, bot, chat_id, conn):
        self.connector = conn
        self.bot = bot
        self.chat_id = chat_id
        self.user_data = {}
        self.verify = random.randint(100000, 999999)

    def start(self):
        self.bot.send_message(self.chat_id, "Пожалуйста, введите имя пользователя:")
        self.bot.register_next_step_handler_by_chat_id(self.chat_id, self.get_name)

    def get_name(self, message):
        self.result = functions.GetAllInformation(conn=self.connector,username=message.text)
        if self.result != None:
            if(message.text == self.result['UserName']):
                self.user_data['username'] = message.text
                self.bot.send_message(self.chat_id, "Пожалуйста, введите пароль:")
                self.bot.register_next_step_handler_by_chat_id(self.chat_id, self.get_password)
        else:
            self.bot.send_message(self.chat_id, "Такого пользователя не существует... Повторите попытку:")
            self.bot.register_next_step_handler_by_chat_id(self.chat_id, self.get_name)

    def get_password(self, message):
        if message.text == self.result['Password']:
            self.user_data['password'] = message.text
            self.bot.send_message(self.chat_id, "Проверьте электронную почту! Введите код из письма:")
            self.bot.register_next_step_handler_by_chat_id(self.chat_id, self.get_verify_code)
            msg = EmailMessage()
            msg.set_content("Ваш код для входа в аккаунт: " + str(self.verify))
            msg['Subject'] = "Подтверждение почты"
            msg['From'] = sender_email
            msg['To'] = self.result['EMail']
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, password)
                server.send_message(msg, from_addr=sender_email, to_addrs=self.result['EMail'])
        else:
            self.bot.send_message(self.chat_id, "Введите пароль еще раз, похоже что ввели не правильно!: ")
            self.bot.register_next_step_handler_by_chat_id(self.chat_id, self.get_password)
    
    def get_verify_code(self, message):
        if(int(message.text)) == self.verify:
            self.bot.send_message(self.chat_id, "Вы успешно подтвердили свою подлинность!")
            functions.loginInProfile(conn=self.connector, username=self.user_data['username'], password=self.user_data['password'], telegramuserid=message.from_user.id)
        else:
            self.bot.send_message(self.chat_id, "Повторите попытку:")
            self.bot.register_next_step_handler_by_chat_id(self.chat_id, self.get_verify_code)
        

