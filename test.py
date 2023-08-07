import telebot

# Создание объекта бота
bot = telebot.TeleBot('6392581487:AAEGhJ8DZSugnEcU1vLUeQliiwaGePyDJms',parse_mode="HTML")

@bot.message_handler(content_types=['text'])
def handle_group_message(message):
     if(message.from_user.id == 56064826 and message.chat.type == "private"):
        bot.send_message(-1001565718999, message.text)

# Запуск бота
bot.polling()