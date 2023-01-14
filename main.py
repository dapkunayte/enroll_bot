import telebot
from telebot import types
import dbworker

bot = telebot.TeleBot("", parse_mode=None)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("📅 Расписание на неделю")
    markup.add(btn1)
    bot.send_message(message.chat.id,
                     text="Привет, {0.first_name}! Я бот, который будет отправлять тебе расписание на неделю, "
                          "когда ты попросишь".format(message.from_user), reply_markup=markup)


@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("📅 Расписание на неделю")
    markup.add(btn1)
    bot.send_message(message.chat.id, "Что ж, начнём по-новой.", reply_markup=markup)


@bot.message_handler(commands=["enroll"])
def enroll(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Понедельник")
    btn2 = types.KeyboardButton("Среда")
    btn3 = types.KeyboardButton("Пятница")
    markup.add(btn1, btn2, btn3)
    msg = bot.send_message(message.chat.id, "Введите день недели, в который хотите прийти. "
                                            "Для отмены записи нажмите /reset", reply_markup=markup)
    bot.register_next_step_handler(msg, user_entering_day)


def user_entering_day(message):
    if str(message.text) == "Понедельник" or str(message.text) == "Среда" or str(message.text) == "Пятница":
        user_info = {'day': str(message.text)}
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("14:00")
        btn2 = types.KeyboardButton("16:00")
        btn3 = types.KeyboardButton("18:00")
        markup.add(btn1, btn2, btn3)
        msg = bot.send_message(message.chat.id, "Теперь укажите, пожалуйста, время", reply_markup=markup)
        bot.register_next_step_handler(msg, user_entering_time, user_info)
    elif message.text == "/reset":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("📅 Расписание на неделю")
        markup.add(btn1)
        bot.send_message(message.chat.id, "Что ж, начнём по-новой.", reply_markup=markup)
        return
    else:
        bot.send_message(message.chat.id, "Что-то не так, введите день ещё раз! Для отмены записи нажмите /reset")
        return


def user_entering_time(message, user_info):
    if str(message.text) == "14:00" or str(message.text) == "16:00" or str(message.text) == "18:00":
        if user_info['day'] == 'Понедельник':
            if int(dbworker.monday[str(message.text)]) <= 0:
                msg = bot.send_message(message.chat.id, "Извините, свободных мест нет! Выберете другое время. "
                                                        "Для отмены записи нажмите /reset")
                bot.register_next_step_handler(msg, user_entering_time, user_info)
                return
        if user_info['day'] == 'Среда':
            if dbworker.wednesday[str(message.text)] <= 0:
                msg = bot.send_message(message.chat.id, "Извините, свободных мест нет! Выберете другое время. "
                                                        "Для отмены записи нажмите /reset")
                bot.register_next_step_handler(msg, user_entering_time, user_info)
                return
        if user_info['day'] == 'Пятница':
            if int(dbworker.friday[str(message.text)]) <= 0:
                msg = bot.send_message(message.chat.id, "Извините, свободных мест нет! Выберете другое время. "
                                                        "Для отмены записи нажмите /reset")
                bot.register_next_step_handler(msg, user_entering_time, user_info)
                return
        user_info['time'] = message.text
        msg = bot.send_message(message.chat.id, "Теперь укажите, пожалуйста, своё имя")
        bot.register_next_step_handler(msg, user_entering_name, user_info)
    elif message.text == "/reset":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("📅 Расписание на неделю")
        markup.add(btn1)
        bot.send_message(message.chat.id, "Что ж, начнём по-новой.", reply_markup=markup)
        return
    else:
        bot.send_message(message.chat.id, "Что-то не так, введите день ещё раз! Для отмены записи нажмите /reset")
        return


def user_entering_name(message, user_info):
    if message.text == "/reset":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("📅 Расписание на неделю")
        markup.add(btn1)
        bot.send_message(message.chat.id, "Что ж, начнём по-новой.", reply_markup=markup)
        return
    if user_info['day'] == "Понедельник":
        dbworker.monday[user_info['time']] = str(int(dbworker.monday[user_info['time']])-1)
    if user_info['day'] == "Среда":
        dbworker.wednesday[user_info['time']] = str(int(dbworker.wednesday[user_info['time']])-1)
    if user_info['day'] == "Пятница":
        dbworker.friday[user_info['time']] = str(int(dbworker.friday[user_info['time']])-1)
    user_info['name'] = message.text
    user_info['message_id'] = str(message.chat.id)
    dbworker.enrolls.append('users', user_info)
    print(dbworker.enrolls['users'].decode("utf-8"))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("📅 Расписание на неделю")
    markup.add(btn1)
    bot.send_message(message.chat.id, "Отлично! Вы записаны", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def schedule(message):
    if message.text == "📅 Расписание на неделю":
        days = "Доступные дни для записи:\n - Понедельник\n - Среда\n - Пятница\n" \
               "Чтобы посмотреть количество свободных мест, выберете день недели \n" \
               "Чтобы записаться выберете команду /enroll"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Понедельник")
        btn2 = types.KeyboardButton("Среда")
        btn3 = types.KeyboardButton("Пятница")
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id, text=days, reply_markup=markup)
    elif message.text == "Понедельник":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Понедельник")
        btn2 = types.KeyboardButton("Среда")
        btn3 = types.KeyboardButton("Пятница")
        markup.add(btn1, btn2, btn3)
        text_pattern = "Количество свободных мест: \n"
        first = dbworker.monday["14:00"]
        second = dbworker.monday["16:00"]
        third = dbworker.monday["18:00"]
        places_14 = " • 14:00 - " + first.decode("utf-8") + '\n'
        places_16 = " • 16:00 - " + second.decode("utf-8") + '\n'
        places_18 = " • 18:00 - " + third.decode("utf-8") + '\n'
        enroll_text = "Чтобы записаться, выберете команду /enroll"
        text = text_pattern + places_14 + places_16 + places_18 + enroll_text
        bot.send_message(message.chat.id, text=text, reply_markup=markup)
    elif message.text == "Среда":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Понедельник")
        btn2 = types.KeyboardButton("Среда")
        btn3 = types.KeyboardButton("Пятница")
        markup.add(btn1, btn2, btn3)
        text_pattern = "Количество свободных мест: \n"
        first = dbworker.wednesday["14:00"]
        second = dbworker.wednesday["16:00"]
        third = dbworker.wednesday["18:00"]
        places_14 = " • 14:00 - " + first.decode("utf-8") + '\n'
        places_16 = " • 16:00 - " + second.decode("utf-8") + '\n'
        places_18 = " • 18:00 - " + third.decode("utf-8") + '\n'
        enroll_text = "Чтобы записаться, выберете команду /enroll"
        text = text_pattern + places_14 + places_16 + places_18 + enroll_text
        bot.send_message(message.chat.id, text=text, reply_markup=markup)
    elif message.text == "Пятница":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Понедельник")
        btn2 = types.KeyboardButton("Среда")
        btn3 = types.KeyboardButton("Пятница")
        markup.add(btn1, btn2, btn3)
        text_pattern = "Количество свободных мест: \n"
        first = dbworker.friday["14:00"]
        second = dbworker.friday["16:00"]
        third = dbworker.friday["18:00"]
        places_14 = " • 14:00 - " + first.decode("utf-8") + '\n'
        places_16 = " • 16:00 - " + second.decode("utf-8") + '\n'
        places_18 = " • 18:00 - " + third.decode("utf-8") + '\n'
        enroll_text = "Чтобы записаться, выберете команду /enroll"
        text = text_pattern + places_14 + places_16 + places_18 + enroll_text
        bot.send_message(message.chat.id, text=text, reply_markup=markup)
    elif message.text == "Записаться":
        bot.send_message(message.chat.id, text="Чтобы записаться, введите команду /enroll")
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("📅 Расписание на неделю")
        markup.add(btn1)
        bot.send_message(message.chat.id, text="Чтобы записаться, введите команду /enroll")


bot.infinity_polling()
