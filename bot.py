import random
import re
import os
import time
from threading import Thread

import vk_api
from vk_api import VkUpload
from flask import Flask
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType


TOKEN = "vk1.a.ceenGlcLhhVpKFGc4HAJfNdEZiBEwu4qoN25_7vnElyV7S7GF4PQGoYVCqD_eAFaUqnSe-MjCuttecLlxuyxqI6dsi93ACm7Wrdg6NDar7x5F5GVl1IFrPnGbPzgKn1W3sIAlAsPAYcWjOF9Ab-olAIcpby-Y4LAOYUSgbDP5iRGPvdRIO0eM4dJJVKf_sU7IHjhTZI3nx6M3fAIJTFHbQ"
GROUP_ID = 239351715

if not TOKEN:
    raise RuntimeError("TOKEN не найден")


def load_quotes():
    try:
        with open("quotes.txt", "r", encoding="utf-8") as file:
            quotes = [
                line.strip()
                for line in file.readlines()
                if line.strip()
            ]

        quotes = list(dict.fromkeys(quotes))

        if not quotes:
            return ["За Императора!"]

        return quotes

    except FileNotFoundError:
        print("Файл quotes.txt не найден.", flush=True)
        return ["За Императора!"]


QUOTES = load_quotes()
quote_pool = []


SPECIAL_REPLIES = {
    "AjdbuGss": {
        "text": "тау СОСАТ!",
        "image": "Tau.png"
    },
    "эреб": {
        "text": "Эреб пидор",
        "image": "Ereb.png"
    },
    "магнус": {
        "text": "Магнус не предавал",
        "image": "Magnus.png"
    },
    "pasta": {
        "text": "Абрик опять посты не пишет",
        "image": "Pasta.png"
    },
    "трап": {
        "text": "Трап эльф это парень, который старается выглядеть, блять, как парень.",
        "image": None
    },
    "друкхари": {
        "text": "Резать Друкхари!",
        "image": "Drukhari.png"
    },
    "кхарн": {
        "text": "Кровь кровавому богу! Черепа трону черепов!",
        "image": None
    },
    "горя": {
        "text": "Ебашим Контакт-5",
        "image": "Contact.png"
    },
    "штрассе": {
        "text": "Слава рогатой крысе",
        "image": "Rat.png"
    },
    "таркус": {
        "text": "Мета Жаба",
        "image": "Jaba.png"
    },
    "сшк": {
        "text": "Из-за неполного СШК нам пришлось адаптировать для Центурионов иную технологию управления, для чего так же необходимо было вживить дополнительные мышцы в соски боевых братьев",
        "image": "SHK.png"
    },
    "железо": {
        "text": "На гусеничные траки переплавим. А то распизделись Железо внутри! Железо снаружи! Да нам на вас срать! Империуму нужны паровозы, Империуму нужен металл!",
        "image": None
    }
}


app = Flask(__name__)


@app.route("/")
def home():
    return "Кубятня работает!"


def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def upload_photo(vk_session, peer_id, image_path):
    if not image_path:
        return None

    if not os.path.exists(image_path):
        print(f"Картинка не найдена: {image_path}", flush=True)
        return None

    try:
        upload = VkUpload(vk_session)

        photo = upload.photo_messages(
            photos=image_path
        )[0]

        print(f"Фото загружено: {image_path}", flush=True)

        access_key = photo.get("access_key")

        if access_key:
            return f"photo{photo['owner_id']}_{photo['id']}_{access_key}"

        return f"photo{photo['owner_id']}_{photo['id']}"

    except Exception as e:
        print(f"Ошибка загрузки картинки {image_path}: {e}", flush=True)
        return None


def get_random_quote():
    global quote_pool
    if not quote_pool:
        quote_pool = QUOTES.copy()
        random.shuffle(quote_pool)
    return quote_pool.pop()


def get_user_name(vk, user_id):
    try:
        user = vk.users.get(user_ids=user_id)[0]
        return f"[id{user_id}|{user['first_name']}]"
    except Exception:
        return f"[id{user_id}|Игрок]"


def make_help():
    return (
        "🎲 КУБЯТНЯ — СПРАВКА\n"
        "━━━━━━━━━━━━━━━\n\n"
        "📖 Команды:\n\n"
        "[к100 — бросить 1 кубик на 100 граней\n"
        "[2к100 — бросить 2 кубика\n"
        "[3к20+15 — бросок с бонусом\n"
        "[3к20+15 #атака — бросок с комментарием\n\n"
        "[цитата — случайная цитата\n"
        "[ц — короткая команда цитаты\n\n"
        "📌 Примеры:\n"
        "[к100\n"
        "[2к6\n"
        "[5к10+7\n"
        "[3к20+69 #стрельба\n\n"
        "🗣 Автоответы:\n"
        "тау / эреб / магнус / pasta / трап / друкхари / кхарн\n\n"
        f"📜 В базе цитат: {len(QUOTES)}\n"
        "⚔ Бот реагирует на команды только через символ ["
    )


def make_quote():
    global QUOTES
    global quote_pool

    QUOTES = load_quotes()
    quote_pool = []

    quote = get_random_quote()

    return (
        "📜 ЦИТАТА ДНЯ\n"
        "━━━━━━━━━━━━━━━\n"
        f"«{quote}»"
    )


def roll(command):
    command = command.strip()

    if not command.startswith("["):
        return None

    command = command[1:].strip()
    command = command.lower().replace("k", "к")

    comment = ""

    if "#" in command:
        command, comment = command.split("#", 1)
        command = command.strip()
        comment = comment.strip()

    match = re.fullmatch(r"(\d*)к(\d+)(?:\+(\d+))?", command)

    if not match:
        return None

    count = int(match.group(1) or 1)
    sides = int(match.group(2))
    bonus = int(match.group(3) or 0)

    if count < 1:
        return None

    if count > 100:
        return "⛔ Слишком много кубиков. Максимум 100."

    if sides < 2:
        return "⛔ У кубика должно быть минимум 2 грани."

    rolls = [random.randint(1, sides) for _ in range(count)]
    total = sum(rolls) + bonus

    dice_name = f"{count}к{sides}"
    if bonus:
        dice_name += f"+{bonus}"

    return {
        "rolls": rolls,
        "total": total,
        "bonus": bonus,
        "dice": dice_name,
        "comment": comment
    }


def make_message(player, result):
    quote = get_random_quote()

    msg = (
        "🎲 КУБЯТНЯ 🎲\n"
        "━━━━━━━━━━━━━━━\n\n"
        f"👤 Игрок: {player}\n"
        f"🎲 Бросок: {result['dice']}\n"
    )

    if result["comment"]:
        msg += f"💬 {result['comment']}\n"

    msg += "\n"
    msg += f"🎯 Выпало: {', '.join(map(str, result['rolls']))}\n"

    if result["bonus"]:
        msg += f"➕ Бонус: +{result['bonus']}\n"

    msg += f"🏆 Итог: {result['total']}\n\n"
    msg += f"📜 Цитата дня:\n«{quote}»"

    return msg


def main():
    vk_session = vk_api.VkApi(token=TOKEN)
    vk = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, GROUP_ID)

    print("Кубятня запущена.", flush=True)

    for event in longpoll.listen():
        if event.type != VkBotEventType.MESSAGE_NEW:
            continue

        message = event.object.message
        text = message.get("text", "").strip()

        print(f"Получено сообщение: {text}", flush=True)

        if not text:
            continue

        peer_id = message["peer_id"]
        lower_text_full = text.lower()

        for trigger, data in SPECIAL_REPLIES.items():
            if trigger in lower_text_full:
                attachment = upload_photo(
                    vk_session,
                    peer_id,
                    data.get("image")
                )

                vk.messages.send(
                    peer_id=peer_id,
                    random_id=random.randint(1, 2**31),
                    message=data["text"],
                    attachment=attachment
                )
                break

        if not text.startswith("["):
            continue

        user_id = message["from_id"]
        player = get_user_name(vk, user_id)

        lower_text = text.lower().strip()

        if lower_text == "[help":
            vk.messages.send(
                peer_id=peer_id,
                random_id=random.randint(1, 2**31),
                message=make_help()
            )
            continue

        if lower_text in ["[цитата", "[ц"]:
            vk.messages.send(
                peer_id=peer_id,
                random_id=random.randint(1, 2**31),
                message=make_quote()
            )
            continue

        answers = []

        for line in text.splitlines():
            result = roll(line)

            if isinstance(result, str):
                answers.append(result)
            elif result:
                answers.append(make_message(player, result))

        if answers:
            vk.messages.send(
                peer_id=peer_id,
                random_id=random.randint(1, 2**31),
                message="\n\n".join(answers)
            )


def run_bot_forever():
    while True:
        try:
            main()
        except Exception as e:
            print(f"Ошибка VK LongPoll: {e}", flush=True)
            time.sleep(10)


if __name__ == "__main__":
    Thread(target=run_web, daemon=True).start()
    run_bot_forever()
