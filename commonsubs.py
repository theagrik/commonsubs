#
# Common Subscribers Counter - скрипт для подсчёта количества подписчиков одной группы в других
# Made by aGrIk, 01.04.2022
#

from vk_api import VkApi
from time import time
import datetime

vk = VkApi(token="ВВЕДИТЕ ЗДЕСЬ ПОЛУЧЕННЫЙ ТОКЕН").get_api()
VkApi.RPS_DELAY = 0.05


def getsubs(group_id):
    print("Получение подписчиков...")
    subs = []
    start = time()
    count = vk.groups.getById(group_id=group_id, fields="members_count")[0]["members_count"]
    for i in range(count // 1000 + 1):
        subs.extend(vk.groups.getMembers(group_id=group_id, offset=i * 1000, count=1000)["items"])
        print(f"Подписчиков: {len(subs)}/{count}, затрачено секунд: {round(time() - start, 2)}")
    print("Получение завершено.")
    return subs

def readableDate(unixtime):
    dex = deunix(unixtime)
    return f"{dex[2]}.{dex[1]}.{dex[0]} {dex[3]}:{dex[4]}:{dex[5]}"

def deunix(integer):
    return datetime.datetime.fromtimestamp(integer).strftime('%Y %m %d %H %M %S').split(" ")

def writeto(text, target):
    file = open(str(target), 'w', encoding='utf-8')
    file.write(str(text))
    file.close()


correct = False
while not correct:
    try:
        print("\nСейчас нужно прикрепить ссылку к сообществу, подписчики которого будут искаться в других группах.")
        print("Например: https://vk.com/catpy, vk.com/catpy, @catpy или catpy.")
        mainpub = input("Введи ссылку: ").replace("http://", "").replace("https://", "").replace("www.", "").replace("vk.com/", "").replace("vkontakte.ru", "").replace("/", "").replace("@", "").replace("*", "")
        mainpub = vk.groups.getById(group_id=mainpub, fields="members_count")[0]
        correct = True
    except:
        print("Некорректная ссылка, проверь и попробуй ещё раз\n")

print(f"Целевое сообщество: \"{mainpub['name']}\" ({mainpub['screen_name']}), подписчиков: {mainpub['members_count']}")
mainpub_subs = getsubs(mainpub['id'])

print(f"\nТеперь введи ссылки на сообщества, где будут искаться подписчики \"{mainpub['name']}\", по одной на строку. ")
print("Чтобы прекратить ввод, просто отправь в конце пустую строку.")
print("Начинай вводить: ", end="")

reading = True
pubs = []
while reading:
    inp = input()
    if inp: pubs.append(inp)
    else: reading = False

print("\nНачинаю обработку...")

subscribers = {}
commons = {}
for pub in pubs:
    try:
        pub_info = vk.groups.getById(group_id=pub.replace("http://", "").replace("https://", "").replace("www.", "").replace("vk.com/", "").replace("vkontakte.ru", "").replace("/", "").replace("@", "").replace("*", ""), fields="members_count")[0]
        print(f"\nСообщество: \"{pub_info['name']}\" ({pub_info['screen_name']}), подписчиков: {pub_info['members_count']}")
    except:
        print(f"Ссылка {pub} некорректна.\n")
    try:
        subscribers[pub_info["id"]] = getsubs(pub_info["id"])
        commons[pub_info["id"]] = {"name": pub_info['name'], "total_subscribers": pub_info['members_count'], "common": 0, "short": pub_info['screen_name']}
    except:
        print("Получение подписчиков не удалось.")

print(f"\nОбработка завершена. Успешно обработанных сообществ: {len(subscribers.keys())}/{len(pubs)}\n")

print("Начинаю поиск...")
for pub in subscribers.keys():
    print(f"Сканирую \"{commons[pub]['name']}\"... ", end="")
    for sub in mainpub_subs:
        if sub in subscribers[pub]: commons[pub]["common"] += 1
    print("Готово.")

print("\nФормирую отчёт... ", end="")

ret = f"""
Отчёт по количеству общих подписчиков. Составлен {readableDate(time())} программой Common Subscribers Counter от @theagrik

Целевое сообщество: "{mainpub['name']}" (vk.com/{mainpub['screen_name']}), всего подписчиков: {mainpub['members_count']}.

Отсканированные сообщества:
"""

for x in commons.keys():
    curr = commons[x]
    ret += f'{curr["name"]} (@{curr["short"]}), общих подписчиков: {curr["common"]}/{curr["total_subscribers"]}\n'

filename = f"csc_report_{round(time())}.txt"
writeto(ret, filename)
print("Отчёт сформирован.")
print(f"Отчёт сохранён под названием {filename}")

while True: pass
