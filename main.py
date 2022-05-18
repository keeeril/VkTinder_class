import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from package.token import token_group
from vkbot import VkBot
from database import db, VkUsers
import time

vk = vk_api.VkApi(token=token_group)
vk = vk.get_api()
longpoll = VkLongPoll(vk)

bot = VkBot()


def sender(id_user, message, keyboard=None):
    if keyboard is not None:
        vk.messages.send(user_id=id_user, message=message, random_id=0, keyboard=keyboard.get_keyboard())
    else:
        vk.messages.send(user_id=id_user, message=message, random_id=0)


def photo_sender(id_user, attachment):
    vk.messages.send(user_id=id_user, attachment=attachment, random_id=0)


def get_message():
    user_res = vk.messages.getConversations()
    user_input = user_res['items'][0]['last_message']['text']
    return user_input


def db_candidate(cand_lst):
    with db:
        db.create_tables([VkUsers])
        data_db = VkUsers.select()
        id_list = [i.id for i in data_db]

        for cand in cand_lst:
            if cand[0] not in id_list:
                cand_data = [{'id': cand[0], 'first_name': cand[1], 'last_name': cand[2]}]
                VkUsers.insert_many(cand_data).execute()
                return [cand[0], cand[1], cand[2]]


def message_bot():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            message_in = event.text.lower()
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button('Следующий', VkKeyboardColor.POSITIVE)
            user_id = event.user_id
            user_info = bot.user_data(user_id)
            candidates = [[cand_info['id'], cand_info['first_name'], cand_info['last_name']] for cand_info in
                          bot.vk_user_search(user_info) if cand_info['is_closed'] is False]

            if message_in in ["привет", "хай", "здорова", "начать"]:
                sender(user_id, f"Хай {user_info['name']}! Я уже ищу для Вас пару...")
                time.sleep(2)
                print(f"{user_info}")

                if user_info['year'] is None or len(user_info['year']) < 4:
                    sender(user_id, "Уточните, в каком году Вы родились? (Пример: 1988)")
                    time.sleep(5)
                    user_info['year'] = get_message()

                if user_info['city'] is None:
                    sender(user_id, "Уточните, в каком городе Вы проживаете?")
                    time.sleep(7)
                    user_info['city'] = get_message().title()

                sender(user_id, f"Подходящие кондидаты:")
                # d = db_candidate(candidates)
                # print(d)
                if bot.get_vk_photos(d[0]) == 'No photos':
                    sender(user_id, f"[id{d[0]}|{d[1]} {d[2]}] - Фотографий нет", keyboard)
                else:
                    sender(user_id, f"[id{d[0]}|{d[1]} {d[2]}]", keyboard)
                    photo_sender(user_id, bot.get_vk_photos(d[0]))

            elif message_in in ["еще", "ещё", "след", "следующий"]:
                # d = db_candidate(candidates)
                # print(d)
                if bot.get_vk_photos(d[0]) == 'No photos':
                    sender(user_id, f"[id{d[0]}|{d[1]} {d[2]}] - Фотографий нет", keyboard)
                else:
                    sender(user_id, f"[id{d[0]}|{d[1]} {d[2]}]", keyboard)
                    photo_sender(user_id, bot.get_vk_photos(d[0]))

            elif message_in == "пока":
                sender(user_id, "Пока((")

            else:
                sender(event.user_id, "Не понял вашего ответа...")


if __name__ == '__main__':
    message_bot()
