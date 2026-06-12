import random
import re
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

TOKEN = "vk1.a.vQsAXzkzX8zjMiwVagPuvllNdhke8EXnt-JrXfMIl9MHuSbW0bz9zxOOhDKTf7omkC7SnLMJGOqm4gPv_F1elNvmYUMnW42VLFM9hmW5wksbQJYMKAeaXofsaSWB2wV_yv_9hffOVj-cq8rNqwA6U1_ph0tqQDlP2vFa7zIX2k_h3CDavShkUt3A5Z6iCcDv_BKgcrPZ3iq6gAVvavV1pg"
GROUP_ID = 239351715

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)

print("Бот запущен")

def send(peer_id, text):
    vk.messages.send(
        peer_id=peer_id,
        message=text,
        random_id=random.randint(1, 2147483647)
    )

def roll_dice(text):
    text = text.strip()

    if text.startswith("/"):
        text = text[1:]

    comment = ""

    if "#" in text:
        text, comment = text.split("#", 1)
        text = text.strip()
        comment = comment.strip()

    text = text.lower().replace("k", "к")

    match = re.fullmatch(r"(\d*)к(\d+)(?:\+(\d+))?", text)

    if not match:
        return None

    count = int(match.group(1) or 1)
    sides = int(match.group(2))
    bonus = int(match.group(3) or 0)

    if count < 1:
        return None

    if count > 100:
        return "❌ Максимум 100 кубиков за бросок."

    if sides < 2:
        return "❌ Кубик должен иметь минимум 2 грани."

    rolls = [random.randint(1, sides) for _ in range(count)]

    total = sum(rolls) + bonus

    dice_name = f"{count}к{sides}"

    if bonus:
        dice_name += f"+{bonus}"

    result = "━━━━━━━━━━━━━━\n"
    result += f"🎲 Бросок: {dice_name}\n"

    if comment:
        result += f"💬 {comment}\n"

    result += "━━━━━━━━━━━━━━\n"

    if count == 1:
        result += f"🎯 Выпало: {rolls[0]}\n"
    else:
        result += f"🎯 Выпало: {', '.join(map(str, rolls))}\n"

    if bonus:
        result += f"➕ Бонус: +{bonus}\n"

    result += f"🏁 Итог: {total}\n"
    result += "━━━━━━━━━━━━━━"

    return result

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:

        msg = event.object.message

        text = msg.get("text", "")
        peer_id = msg["peer_id"]

        answers = []

        for line in text.split("\n"):
            answer = roll_dice(line)

            if answer:
                answers.append(answer)

        if answers:
            send(peer_id, "\n\n".join(answers))