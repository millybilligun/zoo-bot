import telebot
from config import TOKEN, SUPPORT_CONTACT
from extensions import Quiz
from questions import QUESTIONS

bot = telebot.TeleBot(TOKEN)
quiz = Quiz()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    text = (
        "Добро пожаловать в бот Московского зоопарка!\n\n"
        "Пройди викторину и узнай, какое животное могло бы стать твоим тотемом! "
        "Ты также можешь поддержать зоопарк, став опекуном животного.\n"
        "Отправь /quiz для начала викторины или /feedback, чтобы оставить отзыв."
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['quiz'])
def start_quiz(message):
    chat_id = message.chat.id
    quiz.start_quiz(chat_id)
    send_question(message, 0)

def send_question(message, question_index):
    if question_index < len(QUESTIONS):
        question = QUESTIONS[question_index]
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for option in question["options"]:
            markup.add(option)
        bot.send_message(message.chat.id, question["question"], reply_markup=markup)
        bot.register_next_step_handler(message, process_answer, question_index)
    else:
        show_result(message)

def process_answer(message, question_index):
    answer = message.text
    chat_id = message.chat.id
    quiz.process_answer(chat_id, question_index, answer)
    send_question(message, question_index + 1)

def show_result(message):
    chat_id = message.chat.id
    result_animal = quiz.get_result(chat_id)
    if result_animal:
        text = f"Твоё тотемное животное — {result_animal}!\n\n"
        text += (
            f"Ты можешь стать опекуном {result_animal} и помочь зоопарку заботиться о его обитателях! "
            "Чтобы узнать больше, нажми на кнопку 'Подробнее'."
        )
        bot.send_message(chat_id, text)

        # Отправляем изображение животного
        try:
            with open(f'images/{result_animal}.jpg', 'rb') as photo:
                bot.send_photo(chat_id, photo)
        except FileNotFoundError:
            bot.send_message(chat_id, "Изображение временно недоступно.")
        
        # Кнопки для информации о программе и перезапуска
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("Подробнее", url="https://moscowzoo.ru/"),
            telebot.types.InlineKeyboardButton("Попробовать ещё раз", callback_data="retry_quiz")
        )
        bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Произошла ошибка. Попробуйте снова.")

@bot.callback_query_handler(func=lambda call: call.data == "retry_quiz")
def retry_quiz(call):
    bot.answer_callback_query(call.id)
    start_quiz(call.message)

@bot.message_handler(commands=['feedback'])
def feedback(message):
    text = (
        "Мы ценим ваш отзыв!\n"
        "Пожалуйста, отправьте своё мнение или вопрос. Мы с радостью на него ответим.\n\n"
        f"Вы также можете связаться с нами по электронной почте: {SUPPORT_CONTACT}"
    )
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, receive_feedback)

def receive_feedback(message):
    feedback_text = message.text
    chat_id = message.chat.id
    # Логируем обратную связь
    with open("feedback.log", "a") as file:
        file.write(f"Отзыв от {chat_id}: {feedback_text}\n")
    bot.send_message(chat_id, "Спасибо за ваш отзыв! Мы его получили и учтём.")

bot.polling()