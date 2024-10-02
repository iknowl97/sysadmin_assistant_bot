import socket
import requests
from ping3 import ping
import json


def load_config():
    with open('config.json', 'r') as file:
        return json.load(file)


config = load_config()


def send_notification(bot, chat_id, status_message):
    bot.send_message(chat_id, status_message)


def check_services(bot, message):
    online_responses = []
    offline_responses = []

    # Check websites using HTTP requests
    for host in config["hosts"]:
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
    for service in config["ip_ports"]:
        ip = service["ip"]
        port = service["port"]
        print(f"Checking {ip}:{port}...")
        try:
            with socket.create_connection((ip, port), timeout=5):
                online_responses.append(f"✅ Service {ip}:{port} = online")
                print(f"{ip}:{port} is online")
        except Exception as e:
            offline_responses.append(
                f"🚫 {ip}:{port} = offline or error: {str(e)}")
            print(f"{ip}:{port} is offline or error: {str(e)}")

    # Check SQL Server statuses
    for server in config["sql_servers"]:
        ip = server["ip"]
        port = server["port"]
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
    send_notification(bot, message.chat.id,
                      "✅ Online services:\n" + online_message)
    if offline_responses:
        send_notification(bot, message.chat.id,
                          "🚫 Offline services:\n" + offline_message)
    else:
        send_notification(bot, message.chat.id, "✅ Everything is fine! 🏆")


def ping_ips(bot, message):
    online_responses = []
    offline_responses = []

    for ip in config["ips"]:
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
    send_notification(bot, message.chat.id,
                      "✅ Reachable IPs:\n" + online_message)
    if offline_responses:
        send_notification(bot, message.chat.id,
                          "🚫 Unreachable IPs:\n" + offline_message)
    else:
        send_notification(bot, message.chat.id, "✅ All IPs are reachable! 🏆")
