import telebot
import pymysql
import json
import smtplib, ssl
import functions
from login_form import LoginForm
from registration_form import RegistrationForm
from email.message import EmailMessage
bot = telebot.TeleBot("6392581487:AAEGhJ8DZSugnEcU1vLUeQliiwaGePyDJms", parse_mode = "HTML")
allowReg = True 
def connectmsql():
    try:
        global conn
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='tanks_simulator',
            connect_timeout=10,
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except Exception as exept:
        print("Произошла ошибка подключения к MySQL! " + str(exept))
connectmsql()


Sellector = '-'

# Обработка команды /start
@bot.message_handler(content_types=['text'])
def start(message):
    if message.text.lower() == Sellector+"помощь":
        bot.send_message(message.chat.id, f"""<a href="tg://user?id={message.from_user.id}">{message.from_user.username}</a>, вы ввели команду <b>-помощь</b>.\nПолный функционал по этому боту <a href = "https://teletype.in/@tanks_simulator/bot_functions">здесь</a>""")
    elif message.text.lower() == Sellector+"регистрация"and message.chat.type == "private":
        bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
        if allowReg == False: 
             bot.send_message(message.chat.id, "Регистрации закрыты!")
             return
        if functions.checkSession(conn=conn,telegramuserid=message.from_user.id) == True:
            bot.send_message(message.chat.id, "Вы уже вошли в аккаунт!")
            return
        bot.send_message(message.chat.id, "⛔️ <b>Регистрируясь в боте - вы подтверждаете согласие с пользовательским соглашением!</b>")
        registration_form = RegistrationForm(bot, message.chat.id, conn)
        registration_form.start()
    elif message.text.lower() == Sellector+"профиль":
        cur = conn.cursor()
        form = functions.checkSession(conn=conn,telegramuserid=message.from_user.id)
        if form == True:
                result = functions.GetAllInformationByID(conn=conn, id=message.from_user.id)
                if result['Inventory'] != None:
                    inventory = json.loads(result['Inventory'])
                    item_names = []
                    for item_id, quantity in inventory.items():
                        cur.execute(f"SELECT ItemName FROM Items WHERE ID = '{item_id}'")
                        item_result = cur.fetchone()
                        if item_result:
                            item_name = item_result['ItemName']
                            item_names.append(f"  🔸 {item_name} (количество: {quantity})\n")

                    inventory_text = "".join(item_names) if item_names else "Инвентарь пуст"
                else: inventory_text = "Пусто"

                bot.send_message(message.chat.id, f"""🗂 <b>Личная карточка игрока</b> <a href="tg://user?id={message.from_user.id}">{message.from_user.username}</a>:\n\n🖊 <b>Пользовательский ник</b>: <code>{result['UserName']}</code>\n📌 <b>ID</b>: <code>{result["ID"]}</code>\n🧧 <b>Статус</b>: <code>{result['Status']}</code>\n\n🛒 <b>Инвентарь</b>:\n{inventory_text}\n📗 <b>Дата Регистрации</b>: <code>{result["DataRegistration"]}</code>""")
        elif form == "LogIn required":
                bot.send_message(message.chat.id, "Пожалуйста, зарегистрируйтесь, либо войдите в аккаунт.")
    elif message.text.lower() == Sellector+"логин" and message.chat.type == "private":
        bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
        if allowReg == False: 
            bot.send_message(message.chat.id, "Регистрации закрыты!")
            return
        if functions.checkSession(conn=conn,telegramuserid=message.from_user.id) == True:
            bot.send_message(message.chat.id, "Вы уже вошли в аккаунт!")
            return
        bot.send_message(message.chat.id, "Логинясь в боте - вы подтверждаете согласие с пользовательским соглашением!")
        registration_form = LoginForm(bot, message.chat.id, conn)
        registration_form.start()
    elif message.text.lower().startswith(Sellector+"бан"):
        args = message.text.split()
        if len(args) >= 3:
            func = functions.banUser(conn=conn,UserID=args[1])
            if func == False:
                bot.send_message(message.chat.id, "Проверьте пользователя")
            else:
                button = telebot.types.InlineKeyboardButton('Подробнее', url='https://teletype.in/@tanks_simulator/ban-reasons')
                markup = telebot.types.InlineKeyboardMarkup()
                markup.add(button)
                bot.send_message(func, f"⛔️ <code>Стоп-стоп</code>\n<b>К сожалению - теперь ваш аккаунт ограничен. </b>\n<code>Причина: {' '.join(args[2:])}</code>",reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Проверьте синтаксис команды")
    elif message.text.lower().startswith(Sellector+"анбан"):
        args = message.text.split()
        if len(args) == 2:
            func = functions.unbanUser(conn=conn,UserID=args[1])
            if func == False:
                bot.send_message(message.chat.id, "Проверьте пользователя")
            else:
                bot.send_message(func, "✅ <code>Повезло-Повезло</code>\n<b>Ваш аккаунт был разблокирован.</b>")
        else:
            bot.send_message(message.chat.id, "Проверьте синтаксис команды")
bot.polling()