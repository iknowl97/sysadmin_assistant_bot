import os
import socket
import telebot
import requests
from ping3 import ping
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime
from telegramAPItoken import telegram_api_token_for_web_panel_notif

botpcname = socket.gethostname()
bot = telebot.TeleBot(telegram_api_token_for_web_panel_notif)
user_state = {}
bot_info = bot.get_me()
botClientName = bot_info.username


def send_notification(chat_id, status_message):
    bot.send_message(chat_id, status_message)


def check_services(message):
    hosts = ["web.fina24.ge", "fina.ge", "web.miomedica.ge", "web.weeksy.ge"]
    ip_ports = [("license.fina.ge", 64270),
                ("web.fina24.ge", 8089), ("web.fina24.ge",
                                          8888), ("web.fina24.ge", 443),
                ("web.fina24.ge", 8097), ("web.fina24.ge",
                                          8098), ("up.fina.ge", 80), ("up.fina.ge", 443),
                ("d.fina.ge", 80), ("up.fina.ge",
                                    443), ("a.fina.ge", 80), ("a.fina.ge", 443)
                ]
    sql_servers = [("10.0.1.19", 1433), ("10.0.1.95", 1433), ("10.0.1.39", 1433),
                   ("10.0.1.55", 1433), ("10.0.1.202", 1433)]
    online_responses = []
    offline_responses = []

    # Check websites using HTTP requests
    for host in hosts:
        print(f"Checking {host}...")
        try:
            response = requests.get(f"http://{host}", timeout=5)
            if response.status_code == 200:
                online_responses.append(f"✅ Website: {host} = online")
                print(f"{host} is online")
            else:
                offline_responses.append(
                    f"🚫 {host} = offline (status code: {response.status_code})")
                print(f"{host} is offline (status code: {response.status_code})")
        except requests.RequestException as e:
            offline_responses.append(f"⚠️ Error checking {host}: {str(e)}")
            print(f"Error checking {host}: {str(e)}")

    # Check services using IP:Port
    for ip, port in ip_ports:
        print(f"Checking {ip}:{port}...")
        try:
            with socket.create_connection((ip, port), timeout=5):
                online_responses.append(f"✅ Service {ip}:{port} = online")
                print(f"{ip}:{port} is online")
        except Exception as e:
            offline_responses.append(
                f"🚫 {ip}:{port} = offline or error: {str(e)}")
            print(f"{ip}:{port} is offline or error: {str(e)}")

    # Check SQL Server statuses using IP:Port
    for ip, port in sql_servers:
        print(f"Checking SQL Server {ip}:{port}...")
        try:
            with socket.create_connection((ip, port), timeout=5):
                online_responses.append(f"✅ SQL Server: {ip}:{port} = online")
                print(f"SQL Server {ip}:{port} is online")
        except Exception as e:
            offline_responses.append(f"🚫 SQL Server: {ip}:{
                                     port} = offline or error: {str(e)}")
            print(f"SQL Server {ip}:{port} is offline or error: {str(e)}")

    online_message = "\n".join(online_responses)
    offline_message = "\n".join(offline_responses)

    # Send messages based on the status of services
    send_notification(message.chat.id, "✅ Online services:\n" + online_message)
    if offline_responses:
        send_notification(
            message.chat.id, "🚫 Offline services:\n" + offline_message)
    else:
        send_notification(message.chat.id, "✅ ყველაფერი რიგზეა ! ! ! 🏆")


def ping_ips(message):
    ips = ["10.0.1.208", "10.0.1.241", "10.0.1.220", "10.0.1.95", "10.0.1.225", "10.0.1.240",
           "10.0.1.157", "10.0.1.102", "10.0.1.39", "10.0.1.19", "10.0.1.55", "10.0.1.202",
           "10.0.1.21", "10.0.1.235"]
    online_responses = []
    offline_responses = []

    for ip in ips:
        print(f"Pinging {ip}...")
        try:
            response_time = ping(ip, timeout=1)
            if response_time is not None:
                online_responses.append(
                    f"✅ {ip} = reachable ({response_time*1000:.2f} ms)")
                print(f"{ip} is reachable ({response_time*1000:.2f} ms)")
            else:
                offline_responses.append(f"🚫 {ip} = unreachable")
                print(f"{ip} is unreachable")
        except Exception as e:
            offline_responses.append(f"⚠️ Error pinging {ip}: {str(e)}")
            print(f"Error pinging {ip}: {str(e)}")

    online_message = "\n".join(online_responses)
    offline_message = "\n".join(offline_responses)

    # Send messages based on the status of pings
    send_notification(message.chat.id, "✅ Reachable IPs:\n" + online_message)
    if offline_responses:
        send_notification(
            message.chat.id, "🚫 Unreachable IPs:\n" + offline_message)
    else:
        send_notification(message.chat.id, "✅ ყველა IP ხელმისაწვდომია! 🏆")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(row_width=2)
    btn1 = KeyboardButton('მომწერე ჩემი სახელი')
    btn2 = KeyboardButton('გადაამოწმე FINA -ს სერვისები')
    btn3 = KeyboardButton('Ping ყველა სერვერზე')
    markup.add(btn1, btn2, btn3)
    bot.send_message(
        message.chat.id, "🤖 რით შემიძლია დაგეხმარო? აირჩიე ფუნქცია მენიუდან:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'გადაამოწმე FINA -ს სერვისები')
def handle_option1(message):
    initial_message = bot.send_message(
        message.chat.id, "🔍 მიმდინარეობს FINA -ს სერვისების გადამოწმება ⌛️\nგთხოვთ დაელოდოთ პროცესის დასრულების თანავე თქვენ მიიღებთ შეტყობინებას სტატუსებით.\n⌛️⌛️⌛️")
    check_services(message)
    initial_message_id = initial_message.message_id
    bot.delete_message(chat_id=message.chat.id, message_id=initial_message_id)


@bot.message_handler(func=lambda message: message.text == 'მომწერე ჩემი სახელი')
def handle_option2(message):
    chat_user_client_id = str(message.from_user.id)
    chat_user_client_username = message.from_user.username if message.from_user.username else str(
        message.from_user.id)
    chat_user_client_name = message.from_user.first_name if message.from_user.first_name else str(
        message.from_user.id)

    initial_message = bot.send_message(
        message.chat.id, "🔎 მოდი გამოვიცნო შენი სახელი ...\n...")
    initial_message_id = initial_message.message_id
    initial_message2 = bot.send_message(message.chat.id, "...")
    initial_message2_id = initial_message2.message_id
    initial_message3 = bot.send_message(message.chat.id, "...")
    initial_message3_id = initial_message3.message_id

    bot.send_message(message.chat.id,
                     f"📝 შენი სახელი არის: *{chat_user_client_name}*\n"
                     f"📱 შენი ტელეგრამ მომხმარებელი არის: `{
                         chat_user_client_username}`\n"
                     f"🆔 და ასევე შენი ტელეგრამ აიდი არის: `{
                         chat_user_client_id}`",
                     parse_mode="Markdown")

    bot.delete_message(chat_id=message.chat.id, message_id=initial_message3_id)
    bot.delete_message(chat_id=message.chat.id, message_id=initial_message2_id)
    bot.delete_message(chat_id=message.chat.id, message_id=initial_message_id)


@bot.message_handler(func=lambda message: message.text == 'Ping ყველა სერვერზე')
def handle_ping(message):
    initial_message = bot.send_message(
        message.chat.id, "🔍 მიმდინარეობს IP-ების პინგით შემოწმება ⌛️\nგთხოვთ დაელოდოთ პროცესის დასრულებას.")
    ping_ips(message)
    initial_message_id = initial_message.message_id
    bot.delete_message(chat_id=message.chat.id, message_id=initial_message_id)


@bot.message_handler(commands=['hello'])
def start_response(message):
    user_state[message.chat.id] = 'waiting_for_number'
    bot.send_message(message.chat.id, f'👋 სალამი მე ვარ {
                     botpcname}, რით შემიძლია დაგეხმარო?')


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.send_message(message.chat.id, '📩 შეტყობინება მიღებულია!')
    bot.send_message(message.chat.id, '📝 გთხოვთ აირჩიოთ შესაბამისი ფუნქცია!')


bot.polling()
