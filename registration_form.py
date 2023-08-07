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
class RegistrationForm:
    def __init__(self, bot, chat_id, conn):
        self.connector = conn
        self.bot = bot
        self.chat_id = chat_id
        self.user_data = {}
        self.verify = random.randint(100000, 999999)
        print(self.verify)

    def start(self):
        self.bot.send_message(self.chat_id, "<b>Введите желаемое</b> <code>имя пользователя:</code>")
        self.bot.register_next_step_handler_by_chat_id(self.chat_id, self.get_name)

    def get_name(self, message):
        self.user_data['username'] = message.text
        self.bot.send_message(self.chat_id, " <b>Введите</b> <code>вашу почту</code> <i>(для точности - введите два раза разделяя пробелом)</i>:")
        self.bot.register_next_step_handler_by_chat_id(self.chat_id, self.get_email)

    def get_email(self, message):
        try:
            mails = message.text.split()
            if mails[0] == mails[1]:
                if "@gmail" in message.text:
                    self.user_data['email'] = mails[0]
                    self.bot.send_message(self.chat_id, "<b>Введите желаемый</b> <code>пароль:</code>")
                    self.bot.register_next_step_handler_by_chat_id(self.chat_id, self.get_password)
                else:
                    self.bot.send_message(self.chat_id, "<b>⛔️ Некорректная почта, введите еще раз (разрешены только от GMail):</b>")
                    self.bot.register_next_step_handler_by_chat_id(self.chat_id, self.get_email)
            else:
                self.bot.send_message(self.chat_id, "<b>⛔️ Проверьте схожесть почт!</b>")
                self.bot.register_next_step_handler_by_chat_id(self.chat_id, self.get_email)
        except:
            self.bot.send_message(self.chat_id, "<b>Проверьте ввод почты! Пример:</b> <code>example@gmail.com example@gmail.com</code>")
            self.bot.register_next_step_handler_by_chat_id(self.chat_id, self.get_email)  

    def get_password(self, message):
        if len(message.text) >= 8:
            self.user_data['password'] = message.text
            self.bot.send_message(self.chat_id, "🔻 <b>Проверьте электронную почту!</b> <code>Введите код из письма:</code>")
            self.bot.register_next_step_handler_by_chat_id(self.chat_id, self.get_verify_code)
            msg = EmailMessage()
            msg.set_content("Ваш код для подтверждения почты: " + str(self.verify))
            msg['Subject'] = "Подтверждение почты"
            msg['From'] = sender_email
            msg['To'] = self.user_data['email']
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, password)
                server.send_message(msg, from_addr=sender_email, to_addrs=self.user_data['email'])
        else:
            self.bot.send_message(self.chat_id, "<b>Введите пароль еще раз, он должен</b> <code>состоять > 8 символов:</code>")
            self.bot.register_next_step_handler_by_chat_id(self.chat_id, self.get_password)
    
    def get_verify_code(self, message):
        if(int(message.text)) == self.verify:
            self.bot.send_message(self.chat_id, "✅  <b>Вы успешно подтвердили свою</b> <code>почту!</code> <b>Спасибо за регистрацию!</b>")
            functions.registerNewProfile(conn=self.connector, username=self.user_data['username'], EMail=self.user_data['email'], password=self.user_data['password'], telegramuserid=message.from_user.id)
        else:
            self.bot.send_message(self.chat_id, "<b>Повторите попытку:</b>")
            self.bot.register_next_step_handler_by_chat_id(self.chat_id, self.get_verify_code)
        

