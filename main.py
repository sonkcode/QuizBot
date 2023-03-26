import telebot
import random
import time
import json
bot = telebot.TeleBot("6282287565:AAE-_Rm_rKRj0XRND9tTnTvcl0Gwp9bfv5g")

with open("questions.txt", "r", encoding='UTF8') as f:
    lines = f.readlines()
questions = {}
answers = {}
i = 0
while i < len(lines):
    question = lines[i].strip().split("Q: ")[1]
    answer_options = []
    for j in range(4):
        option = lines[i + j + 1].strip().split("A: ")[1]
        answer_options.append(option)
    correct_index = int(lines[i + 5].strip().split("C: ")[1])
    correct_answer = answer_options[correct_index]
    questions[question] = answer_options
    answers[question] = correct_answer
    i += 6
POINTS_FILE = "leaderboard.json"

def load_points():
    try:
        with open(POINTS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_points(points):
    with open(POINTS_FILE, "w") as f:
        json.dump(points, f)

points = load_points()
NUM_QUESTIONS = 49
recipient_username = 1170363727
@bot.message_handler(commands=['leaderboard'])
def leaderboard_command(message):
    sorted_points = sorted(points.items(), key=lambda x: x[1], reverse=True)
    leaderboard = "Таблица лидеров:\n\n"
    for i, (player_id, player_points) in enumerate(sorted_points):
        player = bot.get_chat(player_id)
        leaderboard += f"{i+1}. {player.first_name} {player.last_name}: {player_points} points\n"
    bot.send_message(message.chat.id, leaderboard)

@bot.message_handler(func=lambda message: message.text == "Таблица лидеров")
def leaderboard_handler(message):
    leaderboard_command(message)

@bot.message_handler(commands=['start'])
def start_command(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    markup.add(telebot.types.KeyboardButton("Начать играть"), telebot.types.KeyboardButton("Выход"))
    markup.add(telebot.types.KeyboardButton("Приз игры"), telebot.types.KeyboardButton("Правила игры"))
    markup.add(telebot.types.KeyboardButton("Таблица лидеров"))
    bot.send_message(message.chat.id,
                     "Добро пожаловать в бот 'Незнайка 1.1'! Добавлена таблица лидеров. [Весенний сезон. Игра 2.]",
                     reply_markup=markup)
@bot.message_handler(func=lambda message: True)
def menu_handler(message):
    if message.text == "Начать играть":
        points[message.chat.id] = 0
        question_list = list(questions.keys())
        random.shuffle(question_list)
        ask_question(message, question_list, 0, recipient_username, time.time())
    elif message.text == "Приз игры":
        photo = open('q1.jpg', 'rb')
        bot.send_photo(message.chat.id, photo)
    elif message.text == "Правила игры":
        bot.send_message(message.chat.id,
                          "Вопрос и четыре варианта ответа. Только один вариант правильный. Игра ограничена 12 минутами. Для того чтобы сыграть снова напишите сообщение /start")
    elif message.text == "Выход":
        bot.send_message(message.chat.id, "Пока.", reply_markup=telebot.types.ReplyKeyboardRemove())
    elif message.text == "Leaderboard":
        leaderboard_command(message)
        return
    save_points(points)
def ask_question(message, question_list, question_index, recipient_username, start_time):
    if question_index >= NUM_QUESTIONS or time.time() - start_time > 750:
        num_points = points[message.chat.id]
        points_word = "очков"
        if num_points % 10 == 1 and num_points != 11:
            points_word = "очко"
        elif num_points % 10 in [2, 3, 4] and num_points not in [12, 13, 14]:
            points_word = "очка"
        bot.send_message(message.chat.id, f"Игра завершилась! Вы заработали {num_points} {points_word}.",
                         reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.send_message(recipient_username,
                         f"Результаты: {message.chat.first_name} {message.chat.last_name}:{message.chat.id} заработал {num_points} {points_word}.")
        if question_index >= NUM_QUESTIONS:
            markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
            markup.add(telebot.types.KeyboardButton("Играть еще раз"), telebot.types.KeyboardButton("Выход"))
            bot.send_message(message.chat.id, "Вы ответили на все вопросы! Хотите сыграть еще раз или выйти?",
                             reply_markup=markup)
            bot.register_next_step_handler(message, handle_offer)
        return
    question = question_list[question_index]
    answer_options = questions[question]
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    for i in range(0, len(answer_options), 2):
        markup.add(telebot.types.KeyboardButton(answer_options[i]), telebot.types.KeyboardButton(answer_options[i + 1]))
    bot.send_message(message.chat.id, f"Вопрос {question_index + 1}/{NUM_QUESTIONS}\n<b>{question}</b>",
                     reply_markup=markup, parse_mode='HTML')
    bot.register_next_step_handler(message, handle_answer, question, answer_options, question_list, question_index,
                                   start_time)
def handle_offer(message):
    if message.text == "Играть еще раз":
        points[message.chat.id] = 0
        question_list = list(questions.keys())
        random.shuffle(question_list)
        ask_question(message, question_list, 0, recipient_username, time.time())
    elif message.text == "Выход":
        bot.send_message(message.chat.id, "Спасибо за игру! До свидания.",
                         reply_markup=telebot.types.ReplyKeyboardRemove())
def is_game_over(start_time):
    return time.time() - start_time >= 750

def handle_answer(message, question, answer_options, question_list, question_index, start_time):
    answer = message.text
    num_points = points[message.chat.id]
    points_word = "очков"
    if num_points % 10 == 1 and num_points != 11:
        points_word = "очко"
    elif num_points % 10 in [2, 3, 4] and num_points not in [12, 13, 14]:
        points_word = "очка"
    elapsed_time = time.time() - start_time
    if elapsed_time >= 750:
        bot.send_message(message.chat.id, "Время вышло! Игра закончилась.")
        bot.send_message(message.chat.id, f"Игра завершилась! Вы заработали {num_points} {points_word}.",
                         reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.send_message(recipient_username,
                         f"Результаты: {message.chat.first_name} {message.chat.last_name}:{message.chat.id} заработал {num_points} {points_word}.")
        return
    if answer == answers[question]:
        points[message.chat.id] += 1
        bot.send_message(message.chat.id, "Правильно! Вы заработали 1 очко.")
    else:
        bot.send_message(message.chat.id, f"Неверно. Правильный ответ\n<b>{answers[question]}</b>", parse_mode="HTML")
    ask_question(message, question_list, question_index + 1, recipient_username, time.time())
bot.polling()