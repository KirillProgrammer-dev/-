from cgitb import text
from threading import Thread
import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
import random
import vk
import os
import requests
from user import User
from game import Game, Games
from multiprocessing import Process
from threading import Thread
import time


def write_msg(vk, text: str, peer_id: int, keyboard=None):
    vk.messages.send(
        peer_id=peer_id,
        message=text,
        random_id=get_random_id(),
        keyboard=keyboard
    )


TOKEN = "9736222c76f6f28f0f95082c5a0d2b8383f09b2e61be6a094f02c69962cef2c0478a3e0b1638edd0dcd54"

all_words = {}
game = False
questionName = False
questionNewGame = False
vk_session = vk_api.VkApi(token=TOKEN)
gameslist = []
longpoll = VkLongPoll(vk_session)
vkBot = vk_session.get_api()
sessionParser = vk.Session(
    access_token="2bfeffcb03cd8910ab6b2d1eeb2ae9c72400b0b5c05574893df0c55c3b11260026cd82201cdb030bd2712")
vkapi = vk.API(sessionParser, v='5.81')
users = []
games = Games([])
room = ""

def listen():
    global all_words, game, questionName, questionNewGame, longpoll, vkBot, sessionParser, vkapi, users, room, gameslist
    
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            if 'старт' in event.text.lower():
                game = True
                used_cards = []
                noalbum = False
                findedUser = False
                curUser = 0
                userCounter = 0
                for user in users:
                    if user.user_id == event.peer_id:
                        curUser = user
                        userCounter += 1
                        findedUser = True
                        break
                    userCounter += 1
                if len(event.text.split()) == 1:
                    
                    if findedUser:
                        for i in range(5):
                            upload = vk_api.VkUpload(vkBot)
                            card = random.randrange(1, 99)
                            while card in used_cards:
                                card = random.randrange(1, 99)
                            used_cards.append(card)
                            photo = upload.photo_messages(
                                f'assets/cards/{card}.jpg')
                            owner_id = photo[0]['owner_id']
                            photo_id = photo[0]['id']
                            access_key = photo[0]['access_key']
                            attachment = f'photo{owner_id}_{photo_id}_{access_key}'
                            vkBot.messages.send(
                                peer_id=event.peer_id, random_id=get_random_id(), attachment=attachment)
                        curUser.true_card = random.choice(used_cards)
                        keyboard = VkKeyboard(one_time=True)
                        keyboard.add_button(
                            used_cards[0], color=VkKeyboardColor.PRIMARY)
                        for i in used_cards[1::]:
                            keyboard.add_line()
                            keyboard.add_button(i, color=VkKeyboardColor.PRIMARY)

                        with open("assets/cards/words.txt", "r", encoding="utf-8") as f:
                            for i in f.readlines():
                                if str(user.true_card) in i:
                                    write_msg(vkBot, i.replace(f'{user.true_card}.jpg', '').strip(
                                    ), event.peer_id, keyboard.get_keyboard())
                                    break
                        write_msg(
                            vkBot, "Угадай номер загаданной картинки!", event.peer_id)
                    else:
                        write_msg(vkBot, "Необходимо зарегестрироваться сначала", event.peer_id)

                else:
                    if findedUser:
                        album_id = event.text.split()[1]
                        if os.path.isdir(f'assets/{album_id}'):
                            for i in range(5):
                                upload = vk_api.VkUpload(vkBot)
                                card = random.randrange(
                                    1, len(os.listdir(f'assets/{album_id}')))
                                while card in used_cards:
                                    card = random.randrange(
                                        1, len(os.listdir(f'assets/{album_id}')))
                                used_cards.append(card)
                                photo = upload.photo_messages(
                                    f'assets/{album_id}/{card}.jpg')
                                owner_id = photo[0]['owner_id']
                                photo_id = photo[0]['id']
                                access_key = photo[0]['access_key']
                                attachment = f'photo{owner_id}_{photo_id}_{access_key}'
                                vkBot.messages.send(
                                    peer_id=event.peer_id, random_id=get_random_id(), attachment=attachment)
                                write_msg(vkBot, f"Номер {card}", event.peer_id)
                            user.true_card = random.choice(used_cards)

                            keyboard = VkKeyboard(one_time=True)
                            keyboard.add_button(
                                used_cards[0], color=VkKeyboardColor.PRIMARY)
                            for i in used_cards[1::]:
                                keyboard.add_line()
                                keyboard.add_button(
                                    i, color=VkKeyboardColor.PRIMARY)

                            with open(f"assets/{album_id}/words.txt", "r", encoding="utf-8") as f:
                                for i in f.readlines():
                                    if str(user.true_card) in i:
                                        write_msg(vkBot, i.replace(f'{user.true_card}.jpg', '').strip(
                                        ), event.peer_id, keyboard.get_keyboard())
                                        break

                            write_msg(
                                vkBot, "Угадай номер загаданной картинки!", event.peer_id)
                        else:
                            write_msg(vkBot, "Необходимо зарегестрироваться сначала", event.peer_id)
                    else:
                        write_msg(
                            vkBot, "Такого альбома не существует", event.peer_id)
                        noalbum = True

            if game and event.text.isdigit():
                findedUser = False
                curUser = 0
                userCounter = 0
                for user in users:
                    if user.user_id == event.peer_id:
                        curUser = user
                        userCounter += 1
                        findedUser = True
                        break
                    userCounter += 1
                if int(event.text) == user.true_card:
                    write_msg(vkBot, "Правильно! +3 балла!", event.peer_id)
                    curUser.rating += 3
                    
                else:
                    write_msg(vkBot, "Неверно! 0 балла!", event.peer_id)
                game = False

            if "https://vk.com/album" in event.text:
                if game:
                    write_msg(vkBot, "Сначала закончи игру", event.peer_id)
                else:
                    write_msg(
                        vkBot, "Мы приняли альбом, нужно немного подождать чтобы достать оттуда фото", event.peer_id)
                    url = event.text

                    album_id = url.split('/')[-1].split('_')[1]
                    owner_id = url.split(
                        '/')[-1].split('_')[0].replace('album', '')

                    photos_count = vkapi.photos.getAlbums(owner_id=owner_id, album_ids=album_id)[
                        "items"][0]["size"]
                    photos = vkapi.photos.get(
                        album_id=album_id, count=photos_count, owner_id=owner_id)
                    counter = 1
                    if not os.path.isdir(f"assets/{album_id}"):
                        os.mkdir(f"assets/{album_id}")
                    with open(f"assets/{album_id}/words.txt", "w", encoding="utf-8") as file:
                        file.write("")
                    for i in photos["items"]:
                        URL = i['sizes'][-1]['url']

                        r = requests.get(URL)
                        with open(f"assets/{album_id}/{counter}.jpg", 'wb') as file:
                            file.write(r.content)
                        with open(f"assets/{album_id}/words.txt", "a+", encoding="utf-8") as file:
                            file.write(f"{counter}.jpg {i['text']}\n")
                        counter += 1
                    write_msg(
                        vkBot, f'Колода создана, ей можно начать играть с помощью команды "Старт {album_id}"', event.peer_id)

            if "регистрация" in event.text.lower():
                questionName = True
                write_msg(vkBot, f'Напишите Ваше имя', event.peer_id)

            if questionName:
                if "регистрация" not in event.text.lower():
                    findedUser = False
                    curUser = 0
                    userCounter = 0
                    for user in users:
                        if user.user_id == event.peer_id:
                            curUser = user
                            userCounter += 1
                            findedUser = True
                            break
                        userCounter += 1
                    if not findedUser:
                        name = event.text
                        user = User(name, event.user_id)
                        users.append(user)
                        write_msg(vkBot, f'Ваше имя - {name}', event.peer_id)
                        questionName = False
                    else:
                        write_msg(
                            vkBot, f"Вы уже зарегестрированы. Ваше имя - {curUser.name}", event.peer_idS)
                print(users)

            if "новая комната" in event.text.lower():
                questionNewGame = True
                write_msg(vkBot, f'Напишите название комнаты', event.peer_id)

            if questionNewGame:
                if "новая комната" not in event.text.lower():
                    findedUser = False
                    curUser = 0
                    userCounter = 0
                    for user in users:
                        if user.user_id == event.peer_id:
                            curUser = user
                            userCounter += 1
                            findedUser = True
                            break
                        userCounter += 1
                    if findedUser:
                        name = event.text
                        room = Game(name, event.user_id)
                        games.games.append(room)
                        print(games.games)
                        games.games[-1].addUser(curUser)
                        write_msg(
                            vkBot, f'Название комнаты - {name}', event.peer_id)
                        write_msg(
                            vkBot, f'Колличество участников в комнате - {games.games[-1].users_amount}', event.peer_id)
                        write_msg(
                            vkBot, f"Игра автоматически начнется при нахождении в комнате 3 пользователей", user.user_id)
                        questionNewGame = False
                    else:
                        write_msg(
                            vkBot, f'Сначало необходимо зарегестрироваться', event.peer_id)

                print(games.games)

            if event.text == "Комнаты":
                for i in range(len(games.games)):
                    write_msg(vkBot, game.name, event.peer_id)

            if "присоединиться к" in event.text.lower():
                name_room = event.text.replace("присоединиться к", "").strip()
                curUser = 0
                userCounter = 0
                for user in users:
                    if user.user_id == event.peer_id:
                        curUser = user
                        userCounter += 1
                        break
                    userCounter += 1

                findedGame = False

                for game in games.games:
                    if game.name.lower() == name_room.lower():
                        findedGame = True
                        game.addUser(curUser)
                        write_msg(
                            vkBot, f"Мы присоединили Вас к игровой комнате - {game.name.lower()}", event.peer_id)
                        game.sendAllUsers(vkBot, f"У нас новый участник {user.name}!Теперь нас {game.users_amount}", get_random_id())
                        game.sendAllUsers(vkBot, f"Игра автоматически начнется при нахождении в комнате 3 пользователей", get_random_id())
                        break

                if not findedGame:
                    write_msg(
                        vkBot, "К сожалению, мы не нашли такую комнату", event.peer_id)

                if "результаты" in event.text.lower():
                    findedUser = False
                    curUser = 0
                    userCounter = 0
                    for user in users:
                        if user.user_id == event.peer_id:
                            curUser = user
                            userCounter += 1
                            findedUser = True
                            break
                        userCounter += 1
                    print(findedUser)
                    write_msg(
                        vkBot, f"У вас {curUser.rating} бал(ов)", event.peer_id)
                
                if "все результаты" in event.text.lower():
                    findedUser = False
                    for i in games.games:
                        if curUser in i.users:
                            findedUser = True
                            for j in i.users:
                                i.sendAllUsers(vkBot, f"{j.name} - {j.rating}")
                                break
                    if not findedUser:
                        write_msg(
                        vkBot, f"Вы не находитеся в комнате", event.peer_id)
                if "выйти" in event.text.lower():
                    findedUser = False
                    for i in games.games:
                        if curUser in i.users:
                            games.games.users.remove(curUser)
                    if not findedUser:
                        write_msg(
                        vkBot, f"Вы не находитеся в комнате", event.peer_id)
                
                    
                    


def play_rooms():
    global all_words, game, questionName, questionNewGame, longpoll, vkBot, sessionParser, vkapi, users, room
    while True:
        print(games.games)
        for game in games.games:
            if game.users_amount == 1:
                game.status = "playing"
                game.sendAllUsers(vkBot, "Приготовтесь!", get_random_id())
            else:
                game.status = "waiting"
                game.sendAllUsers(vkBot, f"Ждем {3 - game.users_amount}", get_random_id())
            if game.status == "playing":
                used_cards = []

                for i in range(5):
                    upload = vk_api.VkUpload(vkBot)
                    card = random.randrange(1, 99)
                    while card in used_cards:
                        card = random.randrange(1, 99)
                    used_cards.append(card)
                    photo = upload.photo_messages(f'assets/cards/{card}.jpg')
                    owner_id = photo[0]['owner_id']
                    photo_id = photo[0]['id']
                    access_key = photo[0]['access_key']
                    attachment = f'photo{owner_id}_{photo_id}_{access_key}'
                    for user in game.users:
                        vkBot.messages.send(
                            peer_id=user.user_id, random_id=get_random_id(), attachment=attachment)
                user.true_card = random.choice(used_cards)

                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button(
                    used_cards[0], color=VkKeyboardColor.PRIMARY)
                for i in used_cards[1::]:
                    keyboard.add_line()
                    keyboard.add_button(i, color=VkKeyboardColor.PRIMARY)

                with open("assets/cards/words.txt", "r", encoding="utf-8") as f:
                    for i in f.readlines():
                        if str(user.true_card) in i:
                            for user in game.users:
                                write_msg(vkBot, i.replace(f'{user.true_card}.jpg', '').strip(
                                ), user.user_id, keyboard.get_keyboard())
                            break
                for user in game.users:
                    write_msg(
                        vkBot, "Угадай номер загаданной картинки!", user.user_id)
        time.sleep(59)

def debug():
    global all_words, game, questionName, questionNewGame, longpoll, vkBot, sessionParser, vkapi, users, room ,gameslist
    while True:
        findedUser = False
        curUser = 0
        userCounter = 0
        try:
            print(users[0].true_card)
        except:
            pass
        print(time.time(), ":", games.getGames())
        time.sleep(1)
if __name__ == "__main__":
    th1 = Thread(target=listen)
    print(games.games)
    th2 = Thread(target=play_rooms)
    th3 = Thread(target=debug)
    th1.start()
    th2.start()
    th3.start()
