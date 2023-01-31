import json

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import telegram
import asyncio
import PySimpleGUI as sg
from time import sleep

TELEGRAM_CONFIG = {
    'token': '5614224301:AAEz-FJX5gKMJQT05qtUt3vYnY4oQHJhg3s',
    'chat_id': '-805629730',
    'permition': True
}


# Localizar seu perfil de usuário chrome://version/
def initialize_chrome_browser(options=None):
    options = options or webdriver.ChromeOptions()
    options.add_argument(r'--user-data-dir=C:\\Users\\Genesis\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 3')
    options.add_argument('--profile-directory=Default')
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-logging")
    options.add_argument("--disable-login-animations")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-popup-blocking")
    driver = webdriver.Chrome(options=options)
    return driver


def save_data_to_json(strategies, file_path):
    with open(file_path, "w") as f:
        json.dump(strategies, f)


def load_data_from_json(file_path):
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        print("Carregando estratégias do arquivo json")
        return data
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return []


def get_use_existing_strategies_input():
    layout = [
        [sg.Text("Deseja usar as estratégias atuais?")],
        [sg.Button("Sim"), sg.Button("Não")]
    ]
    window = sg.Window("Estratégias existentes", layout)
    event, values = window.read()
    window.close()
    if event == "Sim":
        return True
    else:
        return False


# def get_strategies_input():
#     n_execucoes = input("Informe o número de estratégias a serem adicionadas: ")
#     if not n_execucoes.isdigit():
#         print("Valor inválido, insira um número inteiro")
#         return
#     strategies = []
#     for j in range(int(n_execucoes)):
#         strategy = {}
#         n_condicoes = input("Informe o número de condições que deseja verificar: ")
#         if not n_condicoes.isdigit():
#             print("Valor inválido, insira um número inteiro")
#             return
#         conditions = ""
#         for i in range(int(n_condicoes)):
#             pos = input("Informe a posição do elemento na lista: ")
#             if not pos.isdigit():
#                 print("Valor inválido, insira um número inteiro")
#                 return
#             value = input("Informe o valor para comparar: ")
#             comparacao = input("Informe o operador de comparação (igual ou diferente): ")
#             if comparacao == "igual":
#                 comparacao = "=="
#             elif comparacao == "diferente":
#                 comparacao = "!="
#             conditions += f"text_list[{pos}] {comparacao} '{value}' and "
#         strategy["conditions"] = conditions[:-4]  # remove the last "and "
#         strategy["message"] = input("Informe a mensagem a ser enviada: ")
#         strategies.append(strategy)
#     save_strategies = input("Deseja salvar as estratégias? (S/n)")
#     if save_strategies.lower() == "s":
#         save_data_to_json(strategies, "data.json")
#     return strategies


def get_strategies_input():
    n_execucoes = sg.popup_get_text("Informe o número de estratégias a serem adicionadas: ")
    if not n_execucoes.isdigit():
        sg.popup_error("Valor inválido, insira um número inteiro")
        return get_strategies_input()
    strategies = []
    for j in range(int(n_execucoes)):
        strategy = {}
        n_condicoes = sg.popup_get_text("Informe o número de condições que deseja verificar: ")
        if not n_condicoes.isdigit():
            sg.popup_error("Valor inválido, insira um número inteiro")
            return get_strategies_input()
        conditions = ""
        for i in range(int(n_condicoes)):
            pos = sg.popup_get_text("Informe a posição do elemento na lista: ")
            if not pos.isdigit():
                sg.popup_error("Valor inválido, insira um número inteiro")
                return get_strategies_input()
            value = sg.popup_get_text("Informe o valor para comparar: ")
            comparacao = sg.popup_get_text("Informe o operador de comparação (igual ou diferente): ")
            if comparacao == "igual":
                comparacao = "=="
            elif comparacao == "diferente":
                comparacao = "!="
            conditions += f"text_list[{pos}] {comparacao} '{value}' and "
        strategy["conditions"] = conditions[:-4]  # remove the last "and "
        strategy["message"] = sg.popup_get_text("Informe a mensagem a ser enviada: ")
        strategies.append(strategy)
    save_strategies = sg.popup_yes_no("Deseja salvar as estratégias?")
    if save_strategies:
        save_data_to_json(strategies, "data.json")
    return strategies


async def create_bot():
    try:
        bot = telegram.Bot(token=TELEGRAM_CONFIG['token'])
        await bot.get_me()
        return bot
    except telegram.error.TelegramError as e:
        print("Error creating bot:", e)
        return None


async def get_telegram_message(message_id):
    bot = await create_bot()
    if bot:
        try:
            message = await bot.get_message(chat_id=TELEGRAM_CONFIG['chat_id'], message_id=message_id)
            return message
        except telegram.error.TelegramError as e:
            print("Error getting message:", e)
            return None
    else:
        print("Unable to get message. Bot not connected.")
        return None


async def send_telegram_message(message):
    bot = await create_bot()
    if bot:
        try:
            message = await bot.send_message(chat_id=TELEGRAM_CONFIG['chat_id'], text=message)
            print("Message sent successfully.")
            return message.message_id
        except telegram.error.TelegramError as e:
            print("Error sending message:", e)
            return None
    else:
        print("Unable to send message. Bot not connected.")
        return None


async def delete_telegram_message(message_id):
    bot = await create_bot()
    if bot:
        try:
            await bot.delete_message(chat_id=TELEGRAM_CONFIG['chat_id'], message_id=message_id)
            print("Message deleted successfully.")
        except telegram.error.TelegramError as e:
            print("Error deleting message:", e)
        else:
            print("Unable to delete message. Bot not connected.")


async def delete_all_messages_except_last():
    bot = await create_bot()
    try:
        updates = await bot.getUpdates()
        for update in updates:
            message = update.message
            if message.text != "Robo analisando, nenhuma entrada a vista" or message.text != "Jogar no 🔵 ou Empate":
                continue
            await bot.delete_message(chat_id=TELEGRAM_CONFIG['chat_id'], message_id=message.message_id)
            break
    except telegram.error.TelegramError as e:
        print("Error deleting messages:", e)


async def check_and_send_message(text_list, last_message_id, last_message, strategies):
    bot = await create_bot()
    for strategy in strategies:
        if eval(strategy["conditions"]):
            if last_message_id:
                try:
                    last_message = await bot.delete_message(chat_id=TELEGRAM_CONFIG['chat_id'],
                                                            message_id=last_message_id)
                except:
                    pass
            message = strategy["message"]
            sent_message = await bot.send_message(chat_id=TELEGRAM_CONFIG['chat_id'], text=message)
            last_message_id = sent_message.message_id
            return last_message_id, message
    if last_message == "Robo analisando, nenhuma entrada a vista":
        await bot.delete_message(chat_id=TELEGRAM_CONFIG['chat_id'], message_id=last_message_id)
    message = "Robo analisando, nenhuma entrada a vista"
    sent_message = await bot.send_message(chat_id=TELEGRAM_CONFIG['chat_id'], text=message)
    last_message_id = sent_message.message_id
    return last_message_id, message


def extract_text_from_elements(driver):
    # Find all elements with class 'badgeSVG--3f405' and extract their text
    elements = driver.find_elements(By.CLASS_NAME, 'derivedRoadsText--6e552')
    text_list = [element.text for element in elements]

    # Replace the values in text_list
    text_list = ["vermelho" if x == "B" else "azul" if x == "P" else "empate" if x == "T" else x for x in text_list]
    return text_list[-12:]


def wait_for_element_disappear(driver):
    try:
        wait = WebDriverWait(driver, 200)
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".gameResultWrapper--fa385.immersive--b7a8f.landscape--3d474")))
        print("Apareceu")

        wait.until(EC.invisibility_of_element_located(
            (By.CSS_SELECTOR, ".gameResultWrapper--fa385.immersive--b7a8f.landscape--3d474")))
        print("Sumiu")
    except Exception as e:
        print("Error waiting for element to disappear:", e)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    use_existing_strategies = get_use_existing_strategies_input()

    if use_existing_strategies:
        strategies = load_data_from_json("data.json")
        if not strategies:
            strategies = []
    else:
        strategies = get_strategies_input()
    driver = initialize_chrome_browser()
    driver.get('https://blaze.com/pt/games/bac-bo')
    input('Aguarde')

    # Switch to the iframe
    driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="game_wrapper"]/iframe'))
    input('Aguarde')
    last_message_id = None
    last_message = None
    while True:
        wait_for_element_disappear(driver)
        text_list = extract_text_from_elements(driver)
        print(text_list)
        last_message_id, last_message = loop.run_until_complete(
            check_and_send_message(text_list, last_message_id, last_message, strategies))
