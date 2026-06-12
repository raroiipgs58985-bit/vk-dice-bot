import random
import re
import os
from threading import Thread

import vk_api
from flask import Flask
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

TOKEN = "vk1.a.vQsAXzkzX8zjMiwVagPuvllNdhke8EXnt-JrXfMIl9MHuSbW0bz9zxOOhDKTf7omkC7SnLMJGOqm4gPv_F1elNvmYUMnW42VLFM9hmW5wksbQJYMKAeaXofsaSWB2wV_yv_9hffOVj-cq8rNqwA6U1_ph0tqQDlP2vFa7zIX2k_h3CDavShkUt3A5Z6iCcDv_BKgcrPZ3iq6gAVvavV1pg"
GROUP_ID = 239351715

QUOTES = [
    "Молчание — вот высшие добродетели.",
    "Страх убивает веру.",
    "Счастье — самообман слабых.",
    "Те, кто ищет совершенства, не найдут покоя в этом мире.",
    "Терпимость — признак слабости.",
    "Только глупцы говорят, что ничего не боятся и все знают.",
    "Только мёртвому нечего терять, у живых есть ещё хотя бы жизнь!",
    "Только служба приносит настоящее счастье.",
    "Труд — тоже молитва.",
    "У человека, лишившегося всего, остаётся вера.",
    "Убей мутанта.",
    "Убивай, убивай, убивай.",
    "Узкий взгляд лучше видит.",
    "Узнай мутанта и убей его.",
    "Умный человек всегда подозрителен.",
    "Успех измеряется в крови; твоей или твоих врагов.",
    "Успехи запоминают; неудачи стараются забыть.",
    "В пламя битвы! На наковальню войны!",
    "Благодаря моему гневу имя Императора будут знать все!",
    "Бойся меня, но повинуйся!",
    "Все за Императора!",
    "Вперед, в рукопашную!",
    "Гори, еретик!",
    "Доброе слово творит чудеса, а доброе слово палача — еще большие.",
    "Мы Имперская Гвардия. Мы сделаем то, что умеем лучше всего. Мы умрем сражаясь. Умрем стоя.",
    "За Терру и Империум!",
    "Ничего не боятся только дураки.",
    "Только дураки уверены полностью, комиссар.",
    "Не знаю, как врага, а меня они пугают, клянусь Императором.",
    "Неизвестный примарх с нами.",
    "Наша вера вечна!",
    "Наконец-то война!",
    "Здесь остался только огонь, варп, и бесстрашные космодесантники.",
    "Смотрите, братья! Нас защищает сам Император!",
    "Сражения, постоянные сражения, лишь бы не помнить и забыть себя.",
    "За Императора!",
    "Император защитит!",
    "Император защищает, но заряженный болтер не повредит!",
    "Император простит тебя. Инквизиция — никогда!",
    "Умри! Умри! Умри!",
    "Пади перед моим гневом!",
    "Пади, еретик!",
    "Предательство всегда окупается предательством.",
    "Мы возьмем каждого, кто может держать в руках оружие!",
    "Я очищу нечистое.",
    "Я очищу мир от скверны.",
    "Я вновь готов служить.",
    "Вера — мой щит! Ярость — мой меч!",
    "Я сломлю разум врага и сожгу его тело.",
    "Император направит мой клинок.",
    "Страдания — вот участь грешников!",
    "Там, где сомнения, я внесу ясность.",
    "Страх убивает веру. (Космодесантник)",
    "Без веры ты — лишь высосанный до костей червь на алтаре смерти. С ней же ты — Человек, который выстоит перед всем, что Тьма выставит против тебя!",
    "Этому телу неведома боль…"
]

app = Flask(__name__)

@app.route("/")
def home():
    return "Кубятня работает!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def get_user_name(vk, user_id):
    try:
        user = vk.users.get(user_ids=user_id)[0]
        return f"[id{user_id}|{user['first_name']}]"
    except:
        return f"[id{user_id}|Игрок]"

def roll(command):
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

    if count > 100:
        return "Слишком много кубиков."

    rolls = [random.randint(1, sides) for _ in range(count)]

    total = sum(rolls) + bonus

    return {
        "rolls": rolls,
        "total": total,
        "bonus": bonus,
        "dice": f"{count}к{sides}",
        "comment": comment
    }

def make_message(player, result):

    quote = random.choice(QUOTES)

    msg = (
        "╔══════════════════╗\n"
        "║     🎲 КУБЯТНЯ     ║\n"
        "╚══════════════════╝\
app.run - Данный веб-сайт выставлен на продажу! - app Ресурсы и информация.
app.run


n\n"
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

    print("Кубятня запущена.")

    for event in longpoll.listen():

        if event.type != VkBotEventType.MESSAGE_NEW:
            continue

        message = event.object.message

        text = message["text"].strip()

        if not text.startswith("/"):
            continue

        user_id = message["from_id"]
        peer_id = message["peer_id"]

        player = get_user_name(vk, user_id)

        result = roll(text[1:])

        if not result:
            continue

        vk.messages.send(
            peer_id=peer_id,
            random_id=random.randint(1, 2**31),
            message=make_message(player, result)
        )

if __name__ == "__main__":

    Thread(target=run_web, daemon=True).start()

    main()
