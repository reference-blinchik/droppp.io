import imaplib
import time

import requests
from pyuseragents import random as random_useragent


def get_mails():
    mails = {}

    with open("mails.txt", "r") as file:
        for i in file.readlines():
            e, p = i.split(":")[0], i.split(":")[1]
            mails[e] = p

    return mails


def get_proxy():
    with open("proxy.txt", "r") as file:
        proxies = file.readlines()

    return proxies


def create_account(mail, password, proxies, user_agent):
    headers = {
        'authority': 'api.droppp.io',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'origin': 'https://droppp.io',
        'referer': 'https://droppp.io/',
        'user-agent': user_agent
    }

    data = {
        'email': mail,
        'password': password
    }
    response = requests.post('https://api.droppp.io/v1/user/add', headers=headers, data=data, proxies=proxies).json()
    try:
        token = response["token"]['access_token']
    except KeyError:
        print(f"[ERROR {mail}]", response["errors"])
        if response["errors"] == {'generic': 'Too many requests'}:
            token = "proxies"
        else:
            token = "continue"
    return token


def send_code(mail, token, proxies, user_agent):
    headers = {
        'user-agent': user_agent,
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'origin': 'https://droppp.io',
        'referer': 'https://droppp.io/',
        'authority': 'api.droppp.io',
        'authorization': f'Bearer {token}',
    }

    response = requests.post('https://api.droppp.io/v1/user/email/verify/send', headers=headers, proxies=proxies)
    if "<!DOCTYPE html>" in response.text:
        print("[INFO] Proxy is invalid")
        return "proxies"

    print(f"[{mail}]", "Code sent:", response.text)


def get_code_from_rambler(login, password):
    mail = imaplib.IMAP4_SSL('imap.rambler.ru')
    mail.login(login, password)
    mail.list()
    mail.select("inbox")
    result, data = mail.search(None, "ALL")
    ids = data[0]
    id_list = ids.split()
    latest_email_id = id_list[-1]
    result, data = mail.fetch(latest_email_id, '(RFC822)')
    result, data = mail.uid('search', None, "ALL")
    latest_email_uid = data[0].split()[-1]
    result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
    raw_email = data[0][1]
    mail = raw_email.decode('UTF-8')
    el = mail.split()
    index_of_code = el.index("#F0F0F3;border-radius=") + 2
    code = el[index_of_code][6:12]

    return code


def enter_code(code, token, proxies, user_agent, mail):
    headers = {
        'authority': 'api.droppp.io',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'authorization': f'Bearer {token}',
        'origin': 'https://droppp.io',
        'referer': 'https://droppp.io/',
        'user-agent': user_agent
    }

    data = {
        'code': code
    }

    requests.post('https://api.droppp.io/v1/user/email/verify/set', headers=headers, data=data, proxies=proxies)

    print(f"[{mail}]", "Registration done")


def main():
    print("Telegram: @cryptoblinchik")
    print("Прокси и почты должны быть в одной папке с файлом run.py")
    print("Прокси должны быть в файле - proxy.txt")
    print("Почты должны быть в файле - mails.txt")
    print("Telegram: @cryptoblinchik")

    mails = get_mails()
    proxy = get_proxy()
    i = 0
    j = 0
    for mail, password in mails.items():
        if i == 2:
            print("[INFO] Proxy changed")
            j += 1
            i = 0
        try:
            proxies = {'http': 'http://' + proxy[j].replace("\n", ''), 'https': 'http://' + proxy[j].replace('\n', '')}
        except IndexError:
            print("[INFO] More accounts than proxies")
            print("[INFO] Registration is over")
            print("[INFO] Last mail:", mail)
            time.sleep(60 * 60)
            break
        user_agent = random_useragent()
        try:
            token = create_account(mail, password, proxies, user_agent)
        except:
            print("[ERROR] requests error")
            token = "proxies"
        if token == "continue":
            continue
        elif token == "proxies":
            i = 2
            continue
        if send_code(mail, token, proxies, user_agent) == "proxies":
            i = 2
            continue
        time.sleep(10)
        try:
            code = get_code_from_rambler(mail, password)
        except:
            print("[ERROR] Something wrong with email")
        enter_code(code, token, proxies, user_agent, mail)
        time.sleep(10)
        i += 1


if __name__ == "__main__":
    main()
