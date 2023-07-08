import telebot
import json
import requests
from bs4 import BeautifulSoup
from telebot import types
import html

with open('', 'r') as f: # Путь к конфигу
    config = json.load(f)
# Initialize the Telegram bot token
bot = telebot.TeleBot("  ",parse_mode="HTML")
def get_news():
    url = 'https://www.bbc.com/russian'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    news_list = []

    first_news = reversed(soup.find('body').find_all('li', class_='ebmt73l0 bbc-lpu9rr e13i2e3d1'))

    for idx, new in enumerate(first_news):
        img_url = new.find('img')['src']
        desc = new.find("p", class_='bbc-1k1unud ea6by781')
        headline = new.find("span")

        if headline != None and headline.text not in ['Telegram', 'Instagram', 'YouTube','ВКонтакте','Facebook','Одноклассники','Twitter','TikTok']:
            descTxt = desc.text if desc != None else " "
            news_list.append(("<b>"+headline.text+"</b>", descTxt, "https://www.bbc.com"+new.find('a')['href'],img_url))

    return news_list[::-1]  # Инвертируем список новостей
# Global variables to store user inputs
user_data = {}
media_files = []
buttons = []
@bot.message_handler(commands=['start'])
def start_cmd(message):
    add_new_user(message.from_user.id)
    news_list = get_news()

    if news_list:
        if len(news_list) > 1:
            # Создаем кнопку для следующей новости
            keyboard = telebot.types.InlineKeyboardMarkup()
            button = telebot.types.InlineKeyboardButton(text="Следующая новость", callback_data=str(1))
            button1 = telebot.types.InlineKeyboardButton(text="Подробнее", url=news_list[0][2])
            keyboard.add(button)
            keyboard.add(button1)

            # Отправляем первую новость с кнопкой для остальных новостей
            bot.send_photo(chat_id=message.chat.id, photo=news_list[0][3],caption=news_list[0][0] + "\n\n" + news_list[0][1], reply_markup=keyboard)
    else:
        bot.send_message(chat_id=message.chat.id, text="К сожалению, нет новых новостей.")
# Обработка нажатия на кнопку "Следующая новость"
@bot.callback_query_handler(func=lambda call: call.data not in ['mailing','stats','yes_media','no_media','yes_text','no_text','yes_buttons','no_buttons','send','cancel'])
def button_click(call):
    try:
        if call.data.isdigit():
            news_list = get_news()

            index = int(call.data)

            if index < len(news_list):

                if index < len(news_list) - 1:
                    # Обновляем кнопку "Следующая новость"
                    keyboard = telebot.types.InlineKeyboardMarkup()
                    back = telebot.types.InlineKeyboardButton(text="Предыдущая новость", callback_data=str(index - 1)) if index > 0 else telebot.types.InlineKeyboardButton(text="", callback_data="empty_button")
                    link = telebot.types.InlineKeyboardButton(text="Подробнее", url=news_list[index][2])
                    next = telebot.types.InlineKeyboardButton(text="Следующая новость", callback_data=str(index + 1)) if index < len(news_list) else telebot.types.InlineKeyboardButton(text="", callback_data="empty_button")
                    keyboard.add(back, next)
                    keyboard.add(link)

                    # Добавляем кнопку к отредактированному сообщению
                    # Редактируем сообщение с новой новостью
                bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        media=telebot.types.InputMediaPhoto(media=news_list[index][3]))
                bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        caption=news_list[index][0] + "\n\n" + news_list[index][1], reply_markup=keyboard)
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Новости больше нет.")
    except:
        bot.send_message(call.message.from_user.id, "Произошла ошибка при обработке команды. Свяжитесь с разработчиком!")
@bot.message_handler(commands=['admin'])
def command_admin_tools(message):
    add_new_user(message.from_user.id)
    if(message.from_user.id == config['admin_id']):
        markup = types.InlineKeyboardMarkup()
        mailing_btn = types.InlineKeyboardButton("📦 Расслыка", callback_data="mailing")
        stats_btn = types.InlineKeyboardButton("📊 Статистика", callback_data="stats")
        markup.add(mailing_btn, stats_btn)

        bot.send_message(message.chat.id, "Выберите меню:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "stats")
def handle_stats(call):
    with open(config['path_to_statistic_json'], 'r') as f:
        stat = json.load(f)
    total_users = stat['total_users']
    active_users = stat['active_users']
    users_succes = stat['last_newsletter']['users_succes']
    users_fail = stat['last_newsletter']['users_fail']
    bot.send_message(call.message.chat.id,f'<b>Статистика бота:</b>\n\n<b>Всего пользователей:</b> <i>{total_users}</i>\n<b>Активных пользователей</b>: <i>{active_users}</i>\n\n<b><i>Статистика за последнюю рассылку:</i></b>\n<b>Успешные пользователи</b>: <i>{users_succes}</i>\n<b>Не успешные пользователи:</b> <i>{users_fail}</i>')

@bot.callback_query_handler(func=lambda call: call.data == "mailing")
def handle_mailing_to_users(call):
    user_data[call.message.chat.id] = {}
    user_data[call.message.chat.id]['media'] = False
    user_data[call.message.chat.id]['text'] = False
    user_data[call.message.chat.id]['buttons'] = False

    markup = types.InlineKeyboardMarkup()
    yes_btn = types.InlineKeyboardButton("Да", callback_data="yes_media")
    no_btn = types.InlineKeyboardButton("Нет", callback_data="no_media")
    markup.add(yes_btn, no_btn)

    bot.send_message(call.message.chat.id, "Желаете прикрепить медиа-файлы?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ["yes_media", "no_media"])
def handle_media_confirmation(call):
    user_data[call.message.chat.id]['media'] = True if call.data == "yes_media" else False

    if user_data[call.message.chat.id]['media']:
        bot.send_message(call.message.chat.id, "Отправьте медиа-файл (картинка, гиф, видео)")
    else:
        bot.send_message(call.message.chat.id, "Добавление медиа-файла пропущено!")
        ask_text(call.message)


@bot.message_handler(content_types=['photo', 'video', 'animation'])
def handle_media(message):
    # Check if the message contains a document, video, or photo
    if message.video:
        user_data[message.chat.id]['media_type'] = "video"
        user_data[message.chat.id]['media'] = True
        media_files.append(message.video.file_id)
    elif message.photo:
        user_data[message.chat.id]['media_type'] = "photo"
        user_data[message.chat.id]['media'] = True
        media_files.append(message.photo[-1].file_id)
    elif message.animation:
        user_data[message.chat.id]['media_type'] = "animation"
        user_data[message.chat.id]['media'] = True
        media_files.append(message.animation.file_id)
    else:
        bot.send_message(message.chat.id, "Не поддерживаемый тип медиа!")
        return

    ask_text(message)



def ask_text(message):
    markup = types.InlineKeyboardMarkup()
    yes_btn = types.InlineKeyboardButton("Да", callback_data="yes_text")
    no_btn = types.InlineKeyboardButton("Нет", callback_data="no_text")
    markup.add(yes_btn, no_btn)

    bot.send_message(message.chat.id, "Добавить текст к сообщению?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ["yes_text", "no_text"])
def handle_text(call):
    user_data[call.message.chat.id]['text'] = True if call.data == "yes_text" else False

    if user_data[call.message.chat.id]['text']:
        bot.send_message(call.message.chat.id, "Пожалуйста, введите текст для сообщения!")
        bot.register_next_step_handler(call.message, handle_entered_text)
    else:
        bot.send_message(call.message.chat.id, "Добавление текста пропущено.")
        ask_buttons(call.message)


def handle_entered_text(message):
    user_data[message.chat.id]['entered_text'] =  message.html_text
    ask_buttons(message)


def ask_buttons(message):
    markup = types.InlineKeyboardMarkup()
    yes_btn = types.InlineKeyboardButton("Да", callback_data="yes_buttons")
    no_btn = types.InlineKeyboardButton("Нет", callback_data="no_buttons")
    markup.add(yes_btn, no_btn)
    messagetxt = "Добавить кнопку к тексту?" if len(buttons) == 0 else "Добавить еще кнопку к тексту?"
    bot.send_message(message.chat.id, messagetxt, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ["yes_buttons", "no_buttons"])
def handle_buttons(call):

    if call.data == "yes_buttons":
        bot.send_message(call.message.chat.id, "Отправьте текст для кнопки")
        bot.register_next_step_handler(call.message, handle_button_text)
    else:
        bot.send_message(call.message.chat.id, "Добавление кнопки пропущено")
        generate_post(call.message)


def handle_button_text(message):
    user_data[message.chat.id]['buttons'] = True
    buttons.append((message.text, ""))  # Store button text temporarily
    bot.send_message(message.chat.id, "Теперь отправьте ссылку для кнопки")
    bot.register_next_step_handler(message, handle_button_link)


def handle_button_link(message):
    buttons[-1] = (buttons[-1][0], message.text) 
    ask_buttons(message)


def generate_post(message):
    
    global mark
    mark = types.InlineKeyboardMarkup()
    markup = types.InlineKeyboardMarkup()
    send_btn = types.InlineKeyboardButton(text="Отправить ➡️", callback_data="send")
    cancel_btn = types.InlineKeyboardButton(text="Отменить ⛔️", callback_data="cancel")
    if user_data[message.chat.id]['buttons']:
        for button in buttons:
            button = types.InlineKeyboardButton(text=button[0], url = button[1])
            mark.add(button)
            markup.add(button)
    markup.add(send_btn, cancel_btn)
    if user_data[message.chat.id]['media'] == True:
        
        if user_data[message.chat.id]['media_type'] == "photo":
            bot.send_photo(message.chat.id,photo=media_files[-1], caption=user_data[message.chat.id]['entered_text'], reply_markup=markup)
        if user_data[message.chat.id]['media_type'] == "animation":
            bot.send_animation(message.chat.id, animation=media_files[-1], caption=user_data[message.chat.id]['entered_text'],reply_markup=markup)
        if user_data[message.chat.id]['media_type'] == "video":
            bot.send_video(message.chat.id, video=media_files[-1], caption=user_data[message.chat.id]['entered_text'],reply_markup=markup)
    else:
        bot.send_message(message.chat.id, user_data[message.chat.id]['entered_text'], reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ["send", "cancel"])
def handle_send_cancel(call):
    with open(config["path_to_statistic_json"], 'r') as f:
        stat = json.load(f)
    with open(config['path_to_users_list'], "r") as f:
        users = f.read().splitlines()
    if call.data == "send":
        users_send_fail = 0
        users_send_succes = 0
        for user in users:
            try:
                if user_data[call.message.chat.id]['media'] == True:
                    
                    if user_data[call.message.chat.id]['media_type'] == "photo":
                        bot.send_photo(user,photo=media_files[-1], caption=user_data[call.message.chat.id]['entered_text'], reply_markup=mark)
                    if user_data[call.message.chat.id]['media_type'] == "animation":
                        bot.send_animation(user, animation=media_files[-1], caption=user_data[call.message.chat.id]['entered_text'],reply_markup=mark)
                    if user_data[call.message.chat.id]['media_type'] == "video":
                        bot.send_video(user, video=media_files[-1], caption=user_data[call.message.chat.id]['entered_text'],reply_markup=mark)
                else:
                    bot.send_message(user, user_data[call.message.chat.id]['entered_text'], reply_markup=mark)
                users_send_succes += 1
            except:
                with open(config['path_to_users_list'], 'r') as file:
                    lines = file.readlines()
                updated_lines = [line for line in lines if users not in line]
                with open(config['path_to_users_list'], 'w') as file:
                    file.writelines(updated_lines)
                users_send_fail += 1
                continue
        stat['last_newsletter'] = {"users_succes":users_send_succes,"users_fail":users_send_fail}
        stat['active_users'] = int(stat['total_users']) - int(stat["last_newsletter"]['users_fail'])
        if call.message.chat.id in user_data:
            del user_data[call.message.chat.id]
        media_files.clear()
        buttons.clear()
        with open(config["path_to_statistic_json"], 'w') as f:
            json.dump(stat, f)
        bot.send_message(call.message.chat.id, "Успешно! Можете посмотреть статистику по последней рассылке в панели." if call.data == "send" else "Cancelled.")
    if call.data == 'cancel':
        media_files.clear()
        buttons.clear()
        bot.send_message(call.message.chat.id, "Отменено!")


def add_new_user(id):
    with open(config['path_to_users_list'], "r") as f:
        users = f.read().splitlines()
    with open(config["path_to_statistic_json"], 'r') as f:
        stat = json.load(f)
    stat['total_users'] += 1
    if str(id) not in users:
        users.append(str(id))
        with open(config['path_to_users_list'], "w") as f:
            f.write('\n'.join(users))
    else:
        return
    with open(config["path_to_statistic_json"], 'w') as f:
        json.dump(stat, f)

bot.polling()
