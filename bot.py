import random
import re
import os
import time
from threading import Thread

import vk_api
from flask import Flask
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType


TOKEN = "vk1.a.vQsAXzkzX8zjMiwVagPuvllNdhke8EXnt-JrXfMIl9MHuSbW0bz9zxOOhDKTf7omkC7SnLMJGOqm4gPv_F1elNvmYUMnW42VLFM9hmW5wksbQJYMKAeaXofsaSWB2wV_yv_9hffOVj-cq8rNqwA6U1_ph0tqQDlP2vFa7zIX2k_h3CDavShkUt3A5Z6iCcDv_BKgcrPZ3iq6gAVvavV1pg"
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
    "тау": "тау СОСАТ!",
    "эреб": "Эреб не гей",
    "магнус": "Магнус не предавал",
    "pasta": "Абрик опять посты не пишет",
    "трап": "Трап эльф это парень, который старается выглядеть, блять, как парень.",
    "друкхари": "Резать Друкхари!",
    "кхарн": "Кровь кровавому богу! Черепа трону черепов!",
    "горя": "Эбать.... Я только щас осмыслел. Что я конченный",
    "штрассе": "Слава рогатой крысе",
    "таркус": "А я собираю крутую мету, круто ложащуюся на лор.",
    "сшк": "Из-за неполного СШК нам пришлось адаптировать для Центурионов иную технологию управления, для чего так же необходимо было вживить дополнительные мышцы в соски боевых братьев",
    "железо": "На гусеничные траки переплавим. А то распизделись Железо внутри! Железо снаружи! Да нам на вас срать! Империуму нужны паровозы, Империуму нужен металл!"
}


app = Flask(__name__)


@app.route("/")
def home():
    return "Кубятня работает!"


def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


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

        for trigger, reply in SPECIAL_REPLIES.items():
            if trigger in lower_text_full:
                vk.messages.send(
                    peer_id=peer_id,
                    random_id=random.randint(1, 2**31),
                    message=reply
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
