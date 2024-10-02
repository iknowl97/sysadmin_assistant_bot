import socket
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from handlers import check_services, ping_ips
from telegramAPItoken import telegram_api_token_for_web_panel_notif

botpcname = socket.gethostname()
bot = telebot.TeleBot(telegram_api_token_for_web_panel_notif)


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
        message.chat.id, "🔍 Checking FINA services ⌛️\nPlease wait while the process completes.\n⌛️⌛️⌛️")
    check_services(bot, message)
    initial_message_id = initial_message.message_id
    bot.delete_message(chat_id=message.chat.id, message_id=initial_message_id)


@bot.message_handler(func=lambda message: message.text == 'Ping All Servers')
def handle_ping(message):
    initial_message = bot.send_message(
        message.chat.id, "🔍 Pinging IPs ⌛️\nPlease wait for the process to complete.")
    ping_ips(bot, message)
    initial_message_id = initial_message.message_id
    bot.delete_message(chat_id=message.chat.id, message_id=initial_message_id)


bot.polling()
