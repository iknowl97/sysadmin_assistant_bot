import socket
import telebot
import time
import threading
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from handlers import check_services, ping_ips
from telegramAPItoken import telegram_api_token_for_web_panel_notif

# Loading emojis for the animation
loading_emojis = ['🔄', '🔃', '🔁', '🔂']
botpcname = socket.gethostname()
bot = telebot.TeleBot(telegram_api_token_for_web_panel_notif)


def animate_loading(sent_message, stop_event):
    chat_id = sent_message.chat.id
    message_id = sent_message.message_id
    while not stop_event.is_set():  # Continue animating until stop_event is set
        for emoji in loading_emojis:
            if stop_event.is_set():
                break
            bot.edit_message_text(
                chat_id=chat_id, message_id=message_id, text=emoji)
            time.sleep(0.5)
    bot.delete_message(chat_id, message_id)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(row_width=2)
    btn1 = KeyboardButton('Check FINA Services')
    btn2 = KeyboardButton('Ping All Servers')
    markup.add(btn1, btn2)
    bot.send_message(
        message.chat.id, "🤖 How can I assist you? Choose a function from the menu:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Check FINA Services')
def handle_option1(message):
    initial_message = bot.send_message(
        message.chat.id, "🔍 Checking FINA services ⌛️")

    stop_event = threading.Event()
    loading_thread = threading.Thread(
        target=animate_loading, args=(initial_message, stop_event))
    loading_thread.start()

    # Perform service check (this will take time)
    check_services(bot, message)

    # Stop the loading animation
    stop_event.set()
    loading_thread.join()


@bot.message_handler(func=lambda message: message.text == 'Ping All Servers')
def handle_ping(message):
    initial_message = bot.send_message(message.chat.id, "🔍 Pinging IPs ⌛️")

    stop_event = threading.Event()
    loading_thread = threading.Thread(
        target=animate_loading, args=(initial_message, stop_event))
    loading_thread.start()

    # Perform the ping checks (this will take time)
    ping_ips(bot, message)

    # Stop the loading animation
    stop_event.set()
    loading_thread.join()


bot.polling()
