import telebot
import random
import threading

# Create a new bot by passing the bot token obtained from BotFather
bot = telebot.TeleBot("6190023351:AAEHl4Z0C5IZE7prX5pMOgbYuxNK7b9Y5BY")

with open("questions.txt", "r") as f:
    lines = f.readlines()

questions = {}
answers = {}

i = 0
while i < len(lines):
    # Read the question
    question = lines[i].strip().split("Q: ")[1]
    # Read the answer options
    answer_options = []
    for j in range(4):
        option = lines[i + j + 1].strip().split("A: ")[1]
        answer_options.append(option)
    # Read the index of the correct answer option
    correct_index = int(lines[i + 5].strip().split("C: ")[1])
    correct_answer = answer_options[correct_index]
    # Add the question and answer to the dictionaries
    questions[question] = answer_options
    answers[question] = correct_answer
    # Update the index to the next question
    i += 6
# Define a dictionary to keep track of the user's points
points = {}

# Define the number of questions to ask in each game
NUM_QUESTIONS = 3

# Define the time limit for answering each question (in seconds)
TIME_LIMIT = 10

recipient_username = 1170363727

# Handler for the "/start" command
@bot.message_handler(commands=['start'])
def start_command(message):
    # Create the reply markup with the main menu options
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
    markup.add(telebot.types.KeyboardButton("Start playing"))
    markup.add(telebot.types.KeyboardButton("Rules of the game"))
    markup.add(telebot.types.KeyboardButton("Exit"))

    # Send the main menu to the user
    bot.send_message(message.chat.id,
                     "Welcome to the Trivia Bot! Please select an option from the menu below:",
                     reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def menu_handler(message):
    if message.text == "Start playing":
        # Reset the user's points
        points[message.chat.id] = 0

        # Create a shuffled list of the questions
        question_list = list(questions.keys())
        random.shuffle(question_list)

        # Send a welcome message and start the first question
        bot.send_message(message.chat.id,
                         "Welcome to the Trivia Bot! You will be asked a series of questions and earn points for each correct answer. Let's begin!")
        ask_question(message, question_list, 0, recipient_username)


    elif message.text == "Rules of the game":
        # Send the rules of the game to the user
        bot.send_message(message.chat.id,
                          "The rules of the game are simple. You will be asked a series of questions and earn points for each correct answer. Good luck!")

    elif message.text == "About the author":
        # Send information about the author to the user
        bot.send_message(message.chat.id,
                          "This bot was created by John Smith.")

    elif message.text == "Exit":
        # Send a message to indicate that the user has exited the game
        bot.send_message(message.chat.id, "Goodbye.", reply_markup=telebot.types.ReplyKeyboardRemove())
def ask_question(message, question_list, question_index, recipient_username):
    # If all questions have been asked, end the game
    if question_index >= NUM_QUESTIONS:
        bot.send_message(message.chat.id, f"Game over! You earned {points[message.chat.id]} points.", reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.send_message(recipient_username,
                         f"Results from Trivia Bot: {message.chat.first_name} {message.chat.last_name}:{message.chat.id} earned {points[message.chat.id]} points.")
        return

    # Get the next question and its answer options
    question = question_list[question_index]
    answer_options = questions[question]

    # Create the reply markup with the answer options
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
    for option in answer_options:
        markup.add(telebot.types.KeyboardButton(option))

    # Send the question to the user with the answer options
    bot.send_message(message.chat.id, question, reply_markup=markup)

    # Set the handler for the user's answer
    t = threading.Timer(TIME_LIMIT, handle_timeout, args=[message, question_list, question_index])
    t.start()
    bot.register_next_step_handler(message, handle_answer, question, answer_options, question_list, question_index, t)

def handle_timeout(message, question_list, question_index):
    bot.send_message(message.chat.id, "Sorry, time's up! Moving on to the next question.")
    ask_question(message, question_list, question_index + 1, recipient_username)

def handle_answer(message, question, answer_options, question_list, question_index, timer):
    # Stop the timer
    timer.cancel()

    # Get the user's answer
    answer = message.text

    # Check if the answer is correct
    if answer == answers[question]:
        # Increment the user's points
        points[message.chat.id] += 1
        bot.send_message(message.chat.id, "Correct! You earned 1 point.")
    else:
        bot.send_message(message.chat.id, "Sorry, that's incorrect.")

    # Ask the next question
    ask_question(message, question_list, question_index + 1, recipient_username)

# Run the bot
bot.polling()